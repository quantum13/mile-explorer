import re

from sanic.request import Request
from sqlalchemy.sql import Select

from core.config import PAGE_SIZE
from core.utils import url_without_qs_param


class Paginator:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


async def get_paginator(request: Request, query: Select, columns):
    """columns: column, sort order, from col to url, from url to col, url pattern"""
    assert len(columns) > 0

    need_reverse = False

    pattern = '_'.join([column[4] for column in columns])

    if 'after' in request.raw_args and re.match(f"^{pattern}$", request.raw_args['after']):
        cols_vals = request.raw_args['after'].split('_')
        col, order, to_url, from_url, _ = columns[0]
        order_by = [getattr(col, order)()]

        if len(columns) == 1:
            if order == 'desc':
                condition = col <= from_url(cols_vals[0])
            else:
                condition = col >= from_url(cols_vals[0])

        else:
            col2, order2, to_url2, from_url2, _ = columns[1]
            order_by.append(getattr(col2, order2)())

            if order2 == 'desc':
                condition = (col < from_url(cols_vals[0])) \
                            | (col == from_url(cols_vals[0])) & (col2 <= from_url2(cols_vals[1]))
            else:
                condition = (col > from_url(cols_vals[0])) \
                            | (col == from_url(cols_vals[0])) & (col2 >= from_url2(cols_vals[1]))

        query = query.where(condition).order_by(*order_by)

        limit = PAGE_SIZE+2
        slice_from = 1

    elif 'before' in request.raw_args and re.match(f"^{pattern}$", request.raw_args['before']):
        cols_vals = request.raw_args['before'].split('_')
        col, order, to_url, from_url, _ = columns[0]
        order_by = [col.asc() if order == 'desc' else col.desc()]

        if len(columns) == 1:
            if order == 'desc':
                condition = col >= from_url(cols_vals[0])
            else:
                condition = col <= from_url(cols_vals[0])
        else:
            col2, order2, to_url2, from_url2, _ = columns[1]
            order_by.append(col2.asc() if order2 == 'desc' else col2.desc())

            if order2 == 'desc':
                condition = (col > from_url(cols_vals[0])) \
                            | (col == from_url(cols_vals[0])) & (col2 >= from_url2(cols_vals[1]))
            else:
                condition = (col < from_url(cols_vals[0])) \
                            | (col == from_url(cols_vals[0])) & (col2 <= from_url2(cols_vals[1]))

        query = query.where(condition).order_by(*order_by)

        limit = PAGE_SIZE+2
        slice_from = 1
        need_reverse = True

    else:
        col, order, _, _, _ = columns[0]
        order_by = [ getattr(col, order)() ]
        if len(columns) > 1:
            col2, order2, _, _, _ = columns[1]
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

    if after:
        after = '_'.join([col[2](getattr(items[-1], col[0].name)) for col in columns])
        after = url_without_qs_param(request.url, 'before', {'after': after})

    if before:
        before = '_'.join([col[2](getattr(items[0], col[0].name)) for col in columns])
        before = url_without_qs_param(request.url, 'after', {'before': before})

    return Paginator(
        items=items,
        after=after,
        before=before
    )
