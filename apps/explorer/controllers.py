import re
from datetime import datetime

import pytz
from sanic.exceptions import NotFound
from sanic.log import logger
from sanic.request import Request

from apps.explorer.models import Transaction, Block, Wallet
from core.di import app, jinja
from core.pagination import get_paginator
from core.utils import url_without_qs_param


@app.exception(NotFound)
@jinja.template('error404.html')
async def error_page(request, exception):
    return {}


@app.exception(Exception)
@jinja.template('error.html')
async def error_page(request, exception):
    logger.error(str(exception))
    return {}





@app.route("/")
@jinja.template('index.html')
async def main(request):
    return {
        'main': 'hello'
    }


@app.route("/transactions")
@jinja.template('explorer/transactions.html')
async def transactions(request: Request):

    query = Transaction.query.where(Transaction.is_fee==False)

    block_id = request.raw_args.get('block_id')
    if block_id and re.match('^\d+$', block_id):
        query = query.where(Transaction.block_id==int(block_id))

        block_id = int(block_id)
        without_block_url = url_without_qs_param(request.url, 'block_id')
    else:
        block_id = without_block_url = None

    addr = request.raw_args.get('addr')
    if addr and re.match('^[A-Za-z0-9]+$', addr):
        query = query.where((Transaction.wallet_from==addr) | (Transaction.wallet_to==addr))

        without_addr_url = url_without_qs_param(request.url, 'addr')
    else:
        addr = without_addr_url = None

    paginator = await get_paginator(request, query, [
        (Transaction.block_id, 'desc', str, int, '\d+'),
        (Transaction.num_in_block, 'desc', str, int, '-?\d+'),
    ])

    return {
        'paginator': paginator,

        'block_id': block_id,
        'without_block_url': without_block_url,
        'addr': addr,
        'without_addr_url': without_addr_url
    }


@app.route("/transactions/<tx_digest:[A-Za-z0-9_]+>")
@jinja.template('explorer/transaction.html')
async def transaction(request: Request, tx_digest):

    tx = await Transaction.get(tx_digest)
    if not tx:
        raise NotFound('Transaction not found')

    return {'tx': tx}


@app.route("/blocks/<block_id:int>")
@jinja.template('explorer/block.html')
async def block(request: Request, block_id):

    b = await Block.get(int(block_id))
    if not b:
        raise NotFound('Block not found')
    has_next_block = bool(await Block.get(int(block_id+1)))

    txs = await Transaction.query.order_by(Transaction.block_id.desc(), Transaction.num_in_block.desc()) \
        .where(Transaction.block_id==b.id).limit(11).gino.all()

    return {
        'b': b, 'has_next_block': has_next_block,
        'txs': txs[:10], 'txs_more': len(txs)==11
    }


@app.route("/blocks")
@jinja.template('explorer/blocks.html')
async def blocks(request: Request):

    query = Block.query

    paginator = await get_paginator(request, query, [
        (Block.id, 'desc', str, int, '\d+')
    ])

    return {'paginator': paginator}


@app.route("/addresses")
@jinja.template('explorer/addresses.html')
async def addresses(request: Request):

    query = Wallet.query

    paginator = await get_paginator(request, query, [
        (Wallet.created_at, 'desc', lambda x: str(int(x.timestamp())), lambda x: datetime.utcfromtimestamp(int(x)).replace(tzinfo=pytz.utc), '\d+'),
        (Wallet.pub_key, 'desc', str, str,'[A-Za-z0-9]+')
    ])

    return {'paginator': paginator}


@app.route("/addresses/<addr:[A-Za-z0-9_]+>")
@jinja.template('explorer/address.html')
async def address(request: Request, addr):

    w = await Wallet.get(addr)
    if not w:
        raise NotFound('Wallet not found')

    txs = await Transaction.query.order_by(Transaction.block_id.desc(), Transaction.num_in_block.desc()) \
        .where((Transaction.wallet_from==w.pub_key) | (Transaction.wallet_to==w.pub_key)).limit(11).gino.all()

    return {
        'w': w,
        'txs': txs[:10], 'txs_more': len(txs)==11
    }
