"""add work reservation columns

Revision ID: 0027
Revises: 0026
Create Date: 2021-04-21 16:23:00.141887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0027'
down_revision = '0026'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work', sa.Column('reserved_until_epoch_ms', sa.BigInteger(), nullable=True))
    op.add_column('work', sa.Column('reserved_worker_id', sa.String(length=8), nullable=True))
    op.create_foreign_key(None, 'work', 'user', ['reserved_worker_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'work', type_='foreignkey')
    op.drop_column('work', 'reserved_worker_id')
    op.drop_column('work', 'reserved_until_epoch_ms')
