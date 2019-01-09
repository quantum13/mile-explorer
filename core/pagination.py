import re
from urllib.parse import urlparse, parse_qs, urlencode

from sanic.request import Request
from sqlalchemy.sql import Select

from core.config import PAGE_SIZE


class Paginator:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


async def get_paginator(request: Request, query: Select, columns):
    assert len(columns) > 0

    need_reverse = False

    pattern = '_'.join([column[3] for column in columns])

    if 'after' in request.raw_args and re.match(f"^{pattern}$", request.raw_args['after']):
        cols_vals = request.raw_args['after'].split('_')
        col, order, type, _ = columns[0]
        order_by = []
        if order=='desc':
            condition = col <= type(cols_vals[0])
            order_by.append(col.desc())
        else:
            condition = col >= type(cols_vals[0])
            order_by.append(col.asc())

        if len(columns) > 1:
            col2, order2, type2, _ = columns[1]

            if order2 == 'desc':
                condition |= (col == type(cols_vals[0])) & (col2 <= type(cols_vals[1]))
                order_by.append(col2.desc())
            else:
                condition |= (col == type(cols_vals[0])) & (col2 >= type(cols_vals[1]))
                order_by.append(col2.asc())

        query = query.where(condition).order_by(*order_by)

        limit = PAGE_SIZE+2
        slice_from = 1


    elif 'before' in request.raw_args and re.match(f"^{pattern}$", request.raw_args['before']):
        cols_vals = request.raw_args['before'].split('_')
        col, order, type, _ = columns[0]
        order_by = []
        if order == 'desc':
            condition = col >= type(cols_vals[0])
            order_by.append(col.asc())
        else:
            condition = col <= type(cols_vals[0])
            order_by.append(col.desc())

        if len(columns) > 1:
            col2, order2, type2, _ = columns[1]

            if order2 == 'desc':
                condition |= (col == type(cols_vals[0])) & (col2 >= type(cols_vals[1]))
                order_by.append(col2.asc())
            else:
                condition |= (col == type(cols_vals[0])) & (col2 <= type(cols_vals[1]))
                order_by.append(col2.desc())

        query = query.where(condition).order_by(*order_by)

        limit = PAGE_SIZE+2
        slice_from = 1
        need_reverse = True


    else:
        col, order, _, _ = columns[0]
        order_by = [ getattr(col, order)() ]
        if len(columns) > 1:
            col2, order2, _, _ = columns[1]
            order_by.append(getattr(col2, order2)())

        query = query.order_by(*order_by)
        limit = PAGE_SIZE + 1
        slice_from = 0

    query = query.limit(limit)

    all_items = await query.gino.all()
    items = all_items[slice_from:PAGE_SIZE+slice_from]

    after = before = None
    if need_reverse:
        items = list(reversed(items))
        after = True
        if len(all_items) == limit:
            before = True

    else:
        if slice_from == 1:
            before = True

        if len(all_items) == limit:
            after = True

    url = urlparse(request.url)
    query = parse_qs(url.query)

    if after:
        after = '_'.join([str(getattr(items[-1], col[0].name)) for col in columns])
        query.pop('before', None)
        query['after'] = after
        after = f"{url.path}?{urlencode(query, True)}"

    if before:
        before = '_'.join([str(getattr(items[0], col[0].name)) for col in columns])
        query.pop('after', None)
        query['before'] = before
        before = f"{url.path}?{urlencode(query, True)}"

    return Paginator(
        items=items,
        after=after,
        before=before
    )
