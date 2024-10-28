"""add user code table

Revision ID: 0014
Revises: 0013
Create Date: 2021-01-18 14:45:41.072346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_code',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=False),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('user_code')
