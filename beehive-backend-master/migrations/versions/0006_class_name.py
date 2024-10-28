"""class_name

Revision ID: 0006
Revises: 0005
Create Date: 2020-09-11 17:33:44.813362

"""
from alembic import op
import sqlalchemy as sa


revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('class_name', sa.String(length=256), nullable=True))


def downgrade():
    op.drop_column('task', 'class_name')
