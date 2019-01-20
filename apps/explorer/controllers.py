import re
from datetime import datetime
from decimal import Decimal

import pytz
from sanic.exceptions import NotFound
from sanic.request import Request
from sanic.response import redirect

from apps.explorer.models import Transaction, Block, Wallet
from core.di import app, jinja
from core.logging import setup_logging
from core.pagination import get_paginator
from core.utils import url_without_qs_param


logger = setup_logging('explorer.controllers')


#################################################################################


@app.exception(NotFound)
@jinja.template('error404.html')
async def error_page(request, exception):
    return {}


@app.exception(Exception)
@jinja.template('error.html')
async def error_page(request, exception):
    try:
        logger.error(str(exception))
    except:
        pass

    return {}


#################################################################################


@app.route("/")
@jinja.template('index.html')
async def main(request):
    return {
        'main': 'hello'
    }


#################################################################################


@app.route("/transactions")
@jinja.template('explorer/transactions.html')
async def transactions(request: Request):

    query = Transaction.query

    with_fee = request.raw_args.get('fee')
    if with_fee:
        without_fee_url = url_without_qs_param(request.url, ['fee', 'after', 'before'])
        with_fee_url = None
    else:
        query = query.where(Transaction.is_fee==False)
        with_fee = without_fee_url = None
        with_fee_url = url_without_qs_param(request.url, ['after', 'before'], {'fee': 1})

    block_id = request.raw_args.get('block_id')
    if block_id and re.match('^\d+$', block_id):
        query = query.where(Transaction.block_id==int(block_id))

        block_id = int(block_id)
        without_block_url = url_without_qs_param(request.url, ['block_id', 'after', 'before'])
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
        'without_addr_url': without_addr_url,
        'with_fee': with_fee,
        'without_fee_url': without_fee_url,
        'with_fee_url': with_fee_url
    }


@app.route("/transactions/<tx_digest:[A-Za-z0-9_]+>")
@jinja.template('explorer/transaction.html')
async def transaction(request: Request, tx_digest):

    tx = await Transaction.get(tx_digest)
    if not tx:
        raise NotFound('Transaction not found')

    return {'tx': tx}


#################################################################################


@app.route("/blocks")
@jinja.template('explorer/blocks.html')
async def blocks(request: Request):

    query = Block.query

    paginator = await get_paginator(request, query, [
        (Block.id, 'desc', str, int, '\d+')
    ])

    return {'paginator': paginator}


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


#################################################################################


@app.route("/addresses")
@jinja.template('explorer/addresses.html')
async def addresses(request: Request):

    query = Wallet.query

    with__is_node = request.raw_args.get('is_node')
    if with__is_node:
        query = query.where(Wallet.is_node==True)
        without__is_node__url = url_without_qs_param(request.url, ['is_node', 'after', 'before'])
        with__is_node__url = None
    else:
        with__is_node = without__is_node__url = None
        with__is_node__url = url_without_qs_param(request.url, ['after', 'before'], {'is_node': 1})

    paginator = await get_paginator(request, query, [
        (Wallet.created_at, 'desc', lambda x: str(int(x.replace(tzinfo=pytz.utc).timestamp())), lambda x: datetime.utcfromtimestamp(int(x)), '\d+'),
        (Wallet.pub_key, 'desc', str, str,'[A-Za-z0-9]+')
    ])

    return {
        'paginator': paginator,
        'without__is_node__url': without__is_node__url,
        'with__is_node__url': with__is_node__url,
        'with__is_node': with__is_node
    }


@app.route("/addresses/top/miles")
@jinja.template('explorer/addresses.html')
async def addresses(request: Request):

    query = Wallet.query

    paginator = await get_paginator(request, query, [
        (Wallet.mile_balance, 'desc', str, lambda x: Decimal(x), '\d+\.\d+|\d+'),
        (Wallet.pub_key, 'desc', str, str,'[A-Za-z0-9]+')
    ])

    return {'paginator': paginator, 'type': 'top_miles'}


@app.route("/addresses/top/xdr")
@jinja.template('explorer/addresses.html')
async def addresses(request: Request):

    query = Wallet.query

    paginator = await get_paginator(request, query, [
        (Wallet.xdr_balance, 'desc', str, lambda x: Decimal(x), '\d+\.\d+|\d+'),
        (Wallet.pub_key, 'desc', str, str,'[A-Za-z0-9]+')
    ])

    return {'paginator': paginator, 'type': 'top_xdr'}


@app.route("/addresses/<addr:[A-Za-z0-9_]+>")
@jinja.template('explorer/address.html')
async def address(request: Request, addr):

    w = await Wallet.get(addr)
    if not w:
        raise NotFound('Wallet not found')

    txs = await Transaction.query.order_by(Transaction.block_id.desc(), Transaction.num_in_block.desc()) \
        .where((Transaction.wallet_from==w.pub_key) | (Transaction.wallet_to==w.pub_key)).limit(11).gino.all()

    first_tx: Transaction = await Transaction.query.order_by(Transaction.block_id.asc()) \
        .where((Transaction.wallet_from == w.pub_key) | (Transaction.wallet_to == w.pub_key)).limit(1).gino.first()

    return {
        'w': w,
        'txs': txs[:10], 'txs_more': len(txs)==11,
        'first_block_id': first_tx.block_id
    }


#################################################################################


@app.route("/search")
@jinja.template('explorer/search.html')
async def address(request: Request):
    q = request.raw_args.get('q')

    if re.match('^\d+$', q):
        block = await Block.get(int(q))
        if block:
            return redirect(f"/blocks/{block.id}")

    tx = await Transaction.get(q)
    if tx:
        return redirect(f"/transactions/{tx.digest}")

    w = await Wallet.get(q)
    if w:
        return redirect(f"/addresses/{w.pub_key}")

    return {
        'q': q,
        'result': {}
    }
