"""add user admin flag column

Revision ID: 0026
Revises: 0025
Create Date: 2021-04-13 13:19:03.259568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0026'
down_revision = '0025'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('admin', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('user', 'admin')
