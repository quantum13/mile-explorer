import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP

from apps.mileapi.constants import TX_TYPES_HUMAN
from core.di import db


class Wallet(db.Model):
    __tablename__ = 'wallets'

    pub_key = sa.Column(sa.String(52), primary_key=True)
    tx_count = sa.Column(sa.BigInteger, nullable=False, server_default='0')
    mile_balance = sa.Column(sa.DECIMAL(19, 5), nullable=False, server_default='0')
    mile_staked = sa.Column(sa.DECIMAL(19, 5), nullable=False, server_default='0')
    xdr_balance = sa.Column(sa.DECIMAL(19, 2), nullable=False, server_default='0')
    xdr_staked = sa.Column(sa.DECIMAL(19, 2), nullable=False, server_default='0')
    created_at = sa.Column(TIMESTAMP(precision=0, timezone=False), nullable=False)
    balance_updated_at = sa.Column(TIMESTAMP(precision=0, timezone=False), default=None)
    valid_before_block = sa.Column(sa.BigInteger, nullable=True)

    is_node = sa.Column(sa.Boolean, nullable=False, default=False, server_default='false')
    node_address = sa.Column(sa.String(255), default=None)

    _idx1 = sa.Index('transactions__mile_balance', 'mile_balance')
    _idx2 = sa.Index('transactions__xdr_balance', 'xdr_balance')
    _idx3 = sa.Index('transactions__mile_staked', 'mile_staked')
    _idx4 = sa.Index('transactions__xdr_staked', 'xdr_staked')
    _idx5 = sa.Index('transactions__created_at', 'created_at')
    _idx6 = sa.Index('transactions__valid_before_block', 'valid_before_block')
    _idx7 = sa.Index('transactions__is_node', 'is_node')

    def __str__(self):
        return self.pub_key


class Block(db.Model):
    __tablename__ = 'blocks'

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=False)
    version = sa.Column(sa.SmallInteger, default=1, nullable=False)

    previous_block_digest = sa.Column(sa.String(52), nullable=False)
    merkle_root = sa.Column(sa.String(52), nullable=False)
    timestamp = sa.Column(TIMESTAMP(precision=0, timezone=False), nullable=False)
    timestamp_real = sa.Column(TIMESTAMP(precision=0, timezone=False))
    transactions_count = sa.Column(sa.Integer, nullable=False, server_default='0')
    number_of_signers = sa.Column(sa.Integer, nullable=False, server_default='0')
    round = sa.Column(sa.SmallInteger, nullable=False, server_default='0')
    block_header_digest = sa.Column(sa.String(52), nullable=False)

    main_signer = sa.Column(sa.String(52), nullable=False)

    reindex_needed = sa.Column(sa.Boolean, nullable=False, default=False)

    def __str__(self):
        return str(self.id)


class Transaction(db.Model):
    __tablename__ = 'transactions'

    digest = sa.Column(sa.String(100), primary_key=True)  # 52, for uniquness of fee txs

    block_id = sa.Column(sa.BigInteger, nullable=False)
    num_in_block = sa.Column(sa.Integer, nullable=False)
    timestamp = sa.Column(TIMESTAMP(precision=0, timezone=False), nullable=False)
    timestamp_real = sa.Column(TIMESTAMP(precision=0, timezone=False))

    global_num = sa.Column(sa.DECIMAL(22, 0), nullable=False)
    is_fee = sa.Column(sa.Boolean, nullable=False, default=False)
    type = sa.Column(sa.SmallInteger, nullable=False)
    fee = sa.Column(sa.DECIMAL(19, 5), nullable=False, server_default='0')
    signature = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.String(100000), nullable=False)

    wallet_from = sa.Column(sa.String(52), default=None)
    wallet_to = sa.Column(sa.String(52), default=None)
    mile = sa.Column(sa.DECIMAL(19, 5), nullable=False, server_default='0')
    xdr = sa.Column(sa.DECIMAL(19, 2), nullable=False, server_default='0')

    asset = sa.Column(sa.SmallInteger, default=None)
    node_address = sa.Column(sa.String(255), default=None)
    rate = sa.Column(sa.DECIMAL(19, 5), default=None)

    _idx1 = sa.Index('transactions__block_id__num_in_block__is_fee', 'block_id', 'num_in_block', 'is_fee')
    _idx2 = sa.Index('transactions__from__timestamp', 'wallet_from', 'timestamp')
    _idx3 = sa.Index('transactions__to__timestamp', 'wallet_to', 'timestamp')
    _idx4 = sa.Index('transactions__timestamp', 'timestamp')
    _idx5 = sa.Index('transactions__is_fee', 'is_fee')

    def __str__(self):
        return self.digest

    def human_type(self):
        return TX_TYPES_HUMAN.get(self.type, '')


class DayStat(db.Model):
    __tablename__ = 'stat_day'
    date = sa.Column(sa.DATE, primary_key=True)
    mile_turnover = sa.Column(sa.DECIMAL(30, 5))
    xdr_turnover = sa.Column(sa.DECIMAL(30, 2))
    tx_count = sa.Column(sa.Integer)
    blocks_count = sa.Column(sa.Integer)
    nonempty_blocks_count = sa.Column(sa.Integer)
    bp_mile_income = sa.Column(sa.DECIMAL(30, 5))
    bp_xdr_income = sa.Column(sa.DECIMAL(30, 2))
    total_xdr = sa.Column(sa.DECIMAL(30, 2))
    active_wallets_count = sa.Column(sa.Integer)
    wallets_count = sa.Column(sa.Integer)
    nonempty_wallets_count = sa.Column(sa.Integer)
    nodes_count = sa.Column(sa.Integer)


class MonthStat(db.Model):
    __tablename__ = 'stat_month'
    date = sa.Column(sa.DATE, primary_key=True)
    mile_turnover = sa.Column(sa.DECIMAL(30, 5))
    xdr_turnover = sa.Column(sa.DECIMAL(30, 2))
    tx_count = sa.Column(sa.Integer)
    blocks_count = sa.Column(sa.Integer)
    nonempty_blocks_count = sa.Column(sa.Integer)
    bp_mile_income = sa.Column(sa.DECIMAL(30, 5))
    bp_xdr_income = sa.Column(sa.DECIMAL(30, 2))
    total_xdr = sa.Column(sa.DECIMAL(30, 2))
    active_wallets_count = sa.Column(sa.Integer)
    wallets_count = sa.Column(sa.Integer)
    nonempty_wallets_count = sa.Column(sa.Integer)
    nodes_count = sa.Column(sa.Integer)
