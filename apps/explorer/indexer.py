import asyncio
import logging
import sys
from collections import deque
from datetime import datetime
from decimal import Decimal
from sys import stdout

import pytz
from dateutil.parser import parse
from sqlalchemy.engine.url import URL

from apps.explorer.models import Block, Wallet, Transaction
from apps.mileapi.api import get_current_block, get_block, get_wallet
from apps.mileapi.constants import TX_TYPES
from core.collections import unique_deque
from core.common import utcnow
from core.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE, TASKS_LIMIT
from core.di import db
from core.logging import setup_logging

logger = setup_logging(__name__)

last_processed_block_id = 0

TASK_BLOCK = 0
TASK_WALLET = 1
TASKS_NAMES = {TASK_BLOCK: 'block', TASK_WALLET: 'wallet'}


def start():
    logger.info('started')

    global last_processed_block_id
    loop = asyncio.get_event_loop()

    dsn = URL(
        drivername='asyncpg', host=DB_HOST, username=DB_USER, password=DB_PASSWORD, database=DB_NAME,
    )

    loop.run_until_complete(
        db.set_bind(
            dsn,
            echo=False,
            min_size=DB_POOL_MIN_SIZE,
            max_size=DB_POOL_MAX_SIZE,
            loop=loop,
        )
    )

    fetch_tasks = unique_deque()

    last_processed_block_id = loop.run_until_complete(process_missing_blocks(fetch_tasks))
    asyncio.ensure_future(check_new_blocks(fetch_tasks))
    asyncio.ensure_future(handle_fetch_tasks(fetch_tasks))
    loop.run_forever()


async def check_new_blocks(fetch_tasks: deque):
    global last_processed_block_id
    while True:
        await asyncio.sleep(10)
        try:
            last_block = await get_current_block()
            for block_id in range(last_processed_block_id+1, last_block+1):
                fetch_tasks.append( (TASK_BLOCK, block_id) )
                logger.info(f"Queued block: {block_id}")
            last_processed_block_id = last_block
        except:
            pass


async def handle_fetch_tasks(fetch_tasks: deque):
    futures = []
    _fill_futures(futures, fetch_tasks)

    while True:
        await asyncio.sleep(0.1)
        # print(len(futures), len(block_tasks))
        for f in futures:
            if f.done():
                futures.remove(f)
                if f.exception() or not f.result():
                    logger.warning(f"Error during processing task: {TASKS_NAMES[f.task[0]]}:{f.task[1]}, {f.exception().__class__.__name__}({f.exception()})")
                    fetch_tasks.append(f.task)
        _fill_futures(futures, fetch_tasks)


def _fill_futures(futures: list, fetch_tasks: deque):
    while len(futures) < TASKS_LIMIT and len(fetch_tasks) > 0:
        task_type, item_id = fetch_tasks.popleft()
        if task_type==TASK_BLOCK:
            coro = _process_block(item_id, fetch_tasks)
        elif task_type==TASK_WALLET:
            coro = _process_wallet(item_id)
        else:
            assert False
        f = asyncio.ensure_future(coro)

        f.task = (task_type, item_id)
        futures.append(f)


async def process_missing_blocks(fetch_tasks: deque):

    blocks_ids = {row[0] for row in await Block.select('id').where(Block.reindex_needed==False).gino.all()}
    last_block = await get_current_block()

    for block_id in range(1, last_block+1):
        if block_id not in blocks_ids:
            fetch_tasks.append( (TASK_BLOCK, block_id) )

    wallets = {row[0] for row in await Wallet.select('pub_key').where(Wallet.update_needed==True).gino.all()}
    for pub_key in wallets:
        fetch_tasks.append( (TASK_WALLET, pub_key) )

    logger.info(len(fetch_tasks))

    return last_block


async def _process_wallet(pub_key):
    data = await get_wallet(pub_key)

    wallet = await Wallet.get(pub_key)
    if not wallet:
        await db.status(
            """
                insert into wallets (pub_key, created_at) 
                values ($1, now()) on conflict (pub_key) do nothing 
            """,
            wallet
        )
        wallet = await Wallet.get(pub_key)
    wallet.update_needed = False
    wallet.balance_updated_at = utcnow()

    if 'Node' in data.get('tags', []):
        wallet.is_node = True
    wallet.node_address = data.get('address')

    for balance in data['balance']:
        if balance['code'] == '0':
            wallet.xdr_balance = Decimal(balance['amount'])
            wallet.xdr_staked = Decimal(balance['frozen'])
        elif balance['code'] == '1':
            wallet.mile_balance = Decimal(balance['amount'])
            wallet.mile_staked = Decimal(balance['frozen'])
        else:
            logger.error(f"Unknown code: {balance['code']}")
            return True  # for manual processing later

    await wallet.update(**wallet.to_dict()).apply()
    return True



async def _process_block(block_id, fetch_tasks: deque):
    data = await get_block(block_id)

    block = Block(
        id=int(data["id"]),
        version=int(data["version"]),
        previous_block_digest=data["previous-block-digest"],
        merkle_root=data["merkle-root"],
        timestamp=parse(data["timestamp"]).replace(tzinfo=pytz.utc),
        transactions_count=int(data["transaction-count"]),
        number_of_signers=int(data["number-of-signers"]),
        round=int(data["round"]),
        block_header_digest=data["block-header-digest"],
        main_signer=data["escort-signatures"][0]['key']
    )

    txs = []
    for i, tx_data in enumerate(list(data['fee-transactions'])):
        tx = Transaction(
            digest=f"{tx_data['digest']}_{block_id}_{i}",
            block_id=block.id,
            num_in_block=-1,
            timestamp=block.timestamp,
            global_num=int(tx_data.get('transaction-id', 0)),
            is_fee=True,
            type=TX_TYPES[tx_data['transaction-type']],
            fee=Decimal(tx_data.get('fee', 0)),
            signature=tx_data['signature'],
            description=tx_data.get('description', '')
        )
        txs.append(tx)

        if not _fill_tx_type_specific_data(tx, tx_data, block):
            block.reindex_needed = True

        tx.wallet_from = None

    for num, tx_data in enumerate(list(data['transactions'])):
        tx = Transaction(
            digest=tx_data['digest'],
            block_id=block.id,
            num_in_block=num,
            timestamp=block.timestamp,
            global_num=int(tx_data.get('transaction-id', 0)),
            is_fee=False,
            type=TX_TYPES[tx_data['transaction-type']],
            fee=Decimal(tx_data.get('fee', 0)),
            signature=tx_data['signature'],
            description=tx_data.get('description', '')
        )
        txs.append(tx)

        if not _fill_tx_type_specific_data(tx, tx_data, block):
            block.reindex_needed = True



    async with db.transaction():
        # r = await Wallet.query.gino.all()
        old_block: Block = await Block.get(block.id)
        if old_block and old_block.reindex_needed:
            await Block.delete.where(Block.id==block.id).gino.status()
            await Transaction.delete.where(Transaction.block_id == block.id).gino.status()
        elif old_block:
            logger.error(f"Task to index, but reindex_needed=False: {block.id}")
            return True

        await block.create()
        for tx in txs:
            await tx.create()

    for tx in txs:
        for wallet in (tx.wallet_from, tx.wallet_to):
            if wallet:
                await db.status(
                    """
                        insert into wallets (pub_key, created_at) 
                        values ($1, now()) on conflict (pub_key) do update set update_needed=true
                    """,
                    wallet
                )
                fetch_tasks.append( (TASK_WALLET, wallet) )

    return True


def _fill_tx_type_specific_data(tx, tx_data, block):
    tx_type = tx_data['transaction-type']

    if tx_type == 'TransferAssetsTransaction':
        tx.wallet_from = tx_data['from']
        tx.wallet_to = tx_data['to']

        if len(tx_data['asset']) > 1:
            logger.warning(f"Several assets in one transfer: {block.id}")
            return False

        for asset_data in list(tx_data['asset']):
            if asset_data['code'] == "0":
                tx.xdr = Decimal(asset_data['amount'])
            elif asset_data['code'] == "1":
                tx.mile = Decimal(asset_data['amount'])
            else:
                logger.warning(f"Unknown asset: {block.id}, {asset_data['code']}")
                return False

    elif tx_type == 'EmissionTransaction':
        tx.wallet_from = tx_data['from']
        tx.asset = int(tx_data['code'])

    elif tx_type == 'RegisterNodeTransactionWithAmount':
        tx.wallet_from = tx_data['public-key']
        tx.node_address = tx_data['address']
        tx.xdr = Decimal(tx_data['amount'])

    elif tx_type == 'UnregisterNodeTransaction':
        tx.wallet_from = tx_data['public-key']

    elif tx_type == 'PostTokenRate':
        tx.wallet_from = tx_data['public-key']
        tx.rate = Decimal(tx_data['course'])

    elif tx_type == 'CreateTokenRateVoting':
        tx.wallet_from = tx_data['public-key']

    elif tx_type == 'GetTokenRate':
        tx.wallet_from = tx_data['public-key']
        tx.rate = Decimal(tx_data['course'])

    elif tx_type == 'UpdateEmission':
        tx.wallet_from = tx_data['from']

    else:
        logger.warning(f"Unknown tx type: {block.id}, {tx_type}")
        return False

    return True
