"""empty message

Revision ID: 0005
Revises: 0004
Create Date: 2019-01-20 23:25:07.459812

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stat_day',
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('mile_turnover', sa.DECIMAL(precision=30, scale=5), nullable=True),
    sa.Column('xdr_turnover', sa.DECIMAL(precision=30, scale=2), nullable=True),
    sa.Column('tx_count', sa.Integer(), nullable=True),
    sa.Column('blocks_count', sa.Integer(), nullable=True),
    sa.Column('nonempty_blocks_count', sa.Integer(), nullable=True),
    sa.Column('bp_mile_income', sa.DECIMAL(precision=30, scale=5), nullable=True),
    sa.Column('bp_xdr_income', sa.DECIMAL(precision=30, scale=2), nullable=True),
    sa.Column('total_xdr', sa.DECIMAL(precision=30, scale=2), nullable=True),
    sa.Column('active_wallets_count', sa.Integer(), nullable=True),
    sa.Column('wallets_count', sa.Integer(), nullable=True),
    sa.Column('nonempty_wallets_count', sa.Integer(), nullable=True),
    sa.Column('nodes_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('date')
    )
    op.create_table('stat_month',
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('mile_turnover', sa.DECIMAL(precision=30, scale=5), nullable=True),
    sa.Column('xdr_turnover', sa.DECIMAL(precision=30, scale=2), nullable=True),
    sa.Column('tx_count', sa.Integer(), nullable=True),
    sa.Column('blocks_count', sa.Integer(), nullable=True),
    sa.Column('nonempty_blocks_count', sa.Integer(), nullable=True),
    sa.Column('bp_mile_income', sa.DECIMAL(precision=30, scale=5), nullable=True),
    sa.Column('bp_xdr_income', sa.DECIMAL(precision=30, scale=2), nullable=True),
    sa.Column('total_xdr', sa.DECIMAL(precision=30, scale=2), nullable=True),
    sa.Column('active_wallets_count', sa.Integer(), nullable=True),
    sa.Column('wallets_count', sa.Integer(), nullable=True),
    sa.Column('nonempty_wallets_count', sa.Integer(), nullable=True),
    sa.Column('nodes_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('date')
    )
    op.add_column('blocks', sa.Column('timestamp_real', postgresql.TIMESTAMP(precision=0), nullable=True))
    op.add_column('transactions', sa.Column('timestamp_real', postgresql.TIMESTAMP(precision=0), nullable=True))
    op.create_index('transactions__is_node', 'wallets', ['is_node'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('transactions__is_node', table_name='wallets')
    op.drop_column('transactions', 'timestamp_real')
    op.drop_column('blocks', 'timestamp_real')
    op.drop_table('stat_month')
    op.drop_table('stat_day')
    # ### end Alembic commands ###
