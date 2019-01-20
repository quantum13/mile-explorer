import asyncio
from datetime import datetime

from apps.mileapi.constants import TransferAssetsTransaction
from core.di import db
from core.logging import setup_logging

logger = setup_logging('indexer_stat')


async def calc_statistics():
    while True:
        await asyncio.sleep(60 * 1)
        start = datetime.now()

        await db.status("delete from stat_day where date < '2018-01-01'")
        await db.status("delete from stat_month where date < '2018-01-01'")

        await calc_turnover()
        await calc__tx__nonempty_blocks__count()
        await calc_blocks_count()
        await calc_bp_income()
        await calc_xdr_count()

        time = (datetime.now() - start).total_seconds()
        logger.info(f"Stat calc finished: {time} seconds")


async def calc_turnover():
    try:
        await db.status(
            """
                insert into stat_day (date, mile_turnover, xdr_turnover)
                    select 
                        date(timestamp) as ts_day, 
                        sum(mile) as mile_turnover, 
                        sum(xdr) as xdr_turnover
                    from 
                        transactions 
                    where 
                        type=$1
                        and is_fee=false
                    group by
                        ts_day
                on conflict (date) 
                do update set 
                    mile_turnover=excluded.mile_turnover,
                    xdr_turnover=excluded.xdr_turnover
            """,
            TransferAssetsTransaction
        )

        await db.status(
            """
                insert into stat_month (date, mile_turnover, xdr_turnover)
                    select 
                        date_trunc('month', timestamp) as ts_month, 
                        sum(mile) as mile_turnover, 
                        sum(xdr) as xdr_turnover
                    from 
                        transactions 
                    where 
                        type=$1
                        and is_fee=false
                    group by
                        ts_month
                on conflict (date) 
                do update set 
                    mile_turnover=excluded.mile_turnover,
                    xdr_turnover=excluded.xdr_turnover
            """,
            TransferAssetsTransaction
        )
    except Exception as e:
        logger.exception(f"turnover: {e}")


async def calc__tx__nonempty_blocks__count():
    try:
        await db.status(
            """
                insert into stat_day (date, tx_count, nonempty_blocks_count, active_wallets_count)
                    select 
                        date(timestamp) as ts_day, 
                        count(digest) as tx_count,
                        count(distinct block_id) as nonempty_blocks_count,
                        count(distinct wallet_from) as active_wallets_count
                    from 
                        transactions 
                    where 
                        is_fee=false
                    group by
                        ts_day
                on conflict (date) 
                do update set 
                    tx_count=excluded.tx_count,
                    nonempty_blocks_count = excluded.nonempty_blocks_count,
                    active_wallets_count = excluded.active_wallets_count
            """
        )

        await db.status(
            """
                insert into stat_month (date, tx_count, nonempty_blocks_count, active_wallets_count)
                    select 
                        date_trunc('month', timestamp) as ts_month, 
                        count(digest) as tx_count,
                        count(distinct block_id) as nonempty_blocks_count,
                        count(distinct wallet_from) as active_wallets_count
                    from 
                        transactions 
                    where 
                        is_fee=false
                    group by
                        ts_month
                on conflict (date) 
                do update set 
                    tx_count=excluded.tx_count,
                    nonempty_blocks_count = excluded.nonempty_blocks_count,
                    active_wallets_count = excluded.active_wallets_count
            """
        )
    except Exception as e:
        logger.exception(f"tx_count: {e}")


async def calc_blocks_count():
    try:
        await db.status(
            """
                insert into stat_day (date, blocks_count)
                    select 
                        date(timestamp) as ts_day, 
                        count(id) as blocks_count
                    from 
                        blocks b
                    group by
                        ts_day
                on conflict (date) 
                do update set 
                    blocks_count=excluded.blocks_count
            """
        )

        await db.status(
            """
                insert into stat_month (date, blocks_count)
                    select 
                        date_trunc('month', timestamp) as ts_month, 
                        count(id) as blocks_count
                    from 
                        blocks b 
                    group by
                        ts_month
                on conflict (date) 
                do update set 
                    blocks_count=excluded.blocks_count
            """
        )
    except Exception as e:
        logger.exception(f"blocks_count: {e}")


async def calc_bp_income():
    try:
        await db.status(
            """
                insert into stat_day (date, bp_mile_income, bp_xdr_income)
                    select 
                        date(timestamp) as ts_day, 
                        sum(mile) as bp_mile_income,
                        sum(xdr) as bp_xdr_income
                    from 
                        transactions 
                    where 
                        is_fee=true
                    group by
                        ts_day
                on conflict (date) 
                do update set 
                    bp_mile_income=excluded.bp_mile_income,
                    bp_xdr_income = excluded.bp_xdr_income
            """
        )

        await db.status(
            """
                insert into stat_month (date, bp_mile_income, bp_xdr_income)
                    select 
                        date_trunc('month', timestamp) as ts_month, 
                        sum(mile) as bp_mile_income,
                        sum(xdr) as bp_xdr_income
                    from 
                        transactions 
                    where 
                        is_fee=true
                    group by
                        ts_month
                on conflict (date) 
                do update set 
                    bp_mile_income=excluded.bp_mile_income,
                    bp_xdr_income = excluded.bp_xdr_income
            """
        )
    except Exception as e:
        logger.exception(f"bp_income: {e}")


async def calc_xdr_count():
    # todo
    try:
        for i in range(15):
            await asyncio.sleep(0.6)
            await db.status(
                """
                    insert into stat_day (date, total_xdr, wallets_count, nonempty_wallets_count, nodes_count)
                        select 
                            date((now() at time zone 'utc')) as ts_day, 
                            sum(xdr_balance) as total_xdr,
                            count(pub_key) as wallets_count,
                            sum(case when mile_balance>0 or xdr_balance>0 then 1 else 0 end) 
                                as nonempty_wallets_count,
                            sum(case when is_node then 1 else 0 end) as nodes_count
                        from 
                            wallets
                        having
                            sum(case when valid_before_block is null then 0 else 1 end) = 0
                    on conflict (date) 
                    do update set 
                        total_xdr=excluded.total_xdr,
                        wallets_count=excluded.wallets_count,
                        nonempty_wallets_count=excluded.nonempty_wallets_count,
                        nodes_count=excluded.nodes_count
                """
            )

            await db.status(
                """
                    insert into stat_month (date, total_xdr, wallets_count, nonempty_wallets_count, nodes_count)
                        select 
                            date_trunc('month', (now() at time zone 'utc')) as ts_month, 
                            sum(xdr_balance) as total_xdr,
                            count(pub_key) as wallets_count,
                            sum(case when mile_balance>0 or xdr_balance>0 then 1 else 0 end) 
                                as nonempty_wallets_count,
                            sum(case when is_node then 1 else 0 end) as nodes_count
                        from 
                            wallets
                        having
                            sum(case when valid_before_block is null then 0 else 1 end) = 0
                    on conflict (date) 
                    do update set 
                        total_xdr=excluded.total_xdr,
                        wallets_count=excluded.wallets_count,
                        nonempty_wallets_count=excluded.nonempty_wallets_count,
                        nodes_count=excluded.nodes_count
                """
            )
    except Exception as e:
        logger.exception(f"calc_xdr_count: {e}")

