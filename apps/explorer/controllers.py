import re

from sanic.request import Request

from apps.explorer.models import Transaction
from core.config import PAGE_SIZE
from core.di import app, jinja


@app.route("/")
@jinja.template('index.html')
async def main(request):
    return {
        'main': 'hello'
    }


@app.route("/transactions")
@jinja.template('explorer/transactions.html')
async def main(request: Request):

    query = Transaction.query.where(Transaction.is_fee==False).limit(PAGE_SIZE)

    need_reverse = False
    pagination_has_prev = True

    if 'after' in request.raw_args and re.match('^\d+_-?\d+$', request.raw_args['after']):
        block_id, num_in_block = request.raw_args['after'].split('_')
        query = query.where(
            (Transaction.block_id<int(block_id)) |
            ((Transaction.block_id==int(block_id)) & (Transaction.num_in_block<int(num_in_block)))
        )

        query = query.order_by(
            Transaction.block_id.desc(), Transaction.num_in_block.desc()
        )
    elif 'before' in request.raw_args and re.match('^\d+_-?\d+$', request.raw_args['before']):
        block_id, num_in_block = request.raw_args['before'].split('_')
        query = query.where(
            (Transaction.block_id>int(block_id)) |
            ((Transaction.block_id==int(block_id)) & (Transaction.num_in_block>int(num_in_block)))
        )

        query = query.order_by(
            Transaction.block_id.asc(), Transaction.num_in_block.asc()
        )
        need_reverse = True
    else:
        query = query.order_by(
            Transaction.block_id.desc(), Transaction.num_in_block.desc()
        )
        pagination_has_prev = False

    txs = await query.gino.all()
    if need_reverse:
        txs = reversed(txs)


    return {
        'transactions': list(txs),
        'pagination_has_prev': pagination_has_prev
    }
