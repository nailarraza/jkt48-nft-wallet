"""Initial migration with simple ticketing

Revision ID: 6735a9377fb5
Revises: 
Create Date: 2025-06-29 17:36:20.784160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6735a9377fb5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('venue', sa.String(length=120), nullable=True),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('ticket_price', sa.Float(), nullable=False),
    sa.Column('tickets_available', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_public_key', sa.String(length=64), nullable=False),
    sa.Column('receiver_public_key', sa.String(length=64), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('signature', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=True),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('nik', sa.String(length=16), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('nik'),
    sa.UniqueConstraint('public_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('nft_id', sa.String(length=64), nullable=False),
    sa.Column('purchase_date', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('qr_code_hash', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nft_id')
    )
    op.create_table('wallets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Float(), nullable=False),
    sa.Column('private_key', sa.String(length=64), nullable=False),
    sa.Column('public_key', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('private_key'),
    sa.UniqueConstraint('public_key')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wallets')
    op.drop_table('tickets')
    op.drop_table('users')
    op.drop_table('transactions')
    op.drop_table('events')
    # ### end Alembic commands ###
