import re

from sanic.exceptions import NotFound
from sanic.log import logger
from sanic.request import Request

from apps.explorer.models import Transaction, Block
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

    paginator = await get_paginator(request, query, [
        (Transaction.block_id, 'desc', int, '\d+'),
        (Transaction.num_in_block, 'desc', int, '-?\d+'),
    ])

    return {
        'paginator': paginator,

        'block_id': block_id,
        'without_block_url': without_block_url
    }


@app.route("/transactions/<tx_digest:[A-z0-9]+>")
@jinja.template('explorer/transaction.html')
async def transaction(request: Request, tx_digest):

    tx = await Transaction.get(tx_digest)
    if not tx:
        raise NotFound('Transaction not found')

    return {'tx': tx}


@app.route("/blocks/<block_id:int>")
@jinja.template('explorer/block.html')
async def transaction(request: Request, block_id):

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
async def transactions(request: Request):

    query = Block.query

    paginator = await get_paginator(request, query, [
        (Block.id, 'desc', int, '\d+')
    ])

    return {'paginator': paginator}
