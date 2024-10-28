"""task add total net duration

Revision ID: 0059
Revises: 0058
Create Date: 2023-09-20 14:06:31.591959

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0059'
down_revision = '0058'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('total_net_duration_seconds', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('task', 'total_net_duration_seconds')