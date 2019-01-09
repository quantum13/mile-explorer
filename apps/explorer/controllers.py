import re

from sanic.exceptions import NotFound
from sanic.log import logger
from sanic.request import Request

from apps.explorer.models import Transaction, Block
from core.config import PAGE_SIZE
from core.di import app, jinja
from core.pagination import get_paginator


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

    paginator = await get_paginator(request, query, [
        (Transaction.block_id, 'desc', int, '\d+'),
        (Transaction.num_in_block, 'desc', int, '-?\d+'),
    ])

    return {'paginator': paginator}


@app.route("/transactions/<tx_digest>")
@jinja.template('explorer/transaction.html')
async def transaction(request: Request, tx_digest):

    tx = await Transaction.get(tx_digest)
    if not tx:
        raise NotFound('Transaction not found')

    return {'tx': tx}


@app.route("/blocks")
@jinja.template('explorer/blocks.html')
async def transactions(request: Request):

    query = Block.query

    paginator = await get_paginator(request, query, [
        (Block.id, 'desc', int, '\d+')
    ])

    return {'paginator': paginator}
