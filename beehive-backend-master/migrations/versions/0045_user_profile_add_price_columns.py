"""user profile add price columns

Revision ID: 0045
Revises: 0044
Create Date: 2022-04-19 12:36:06.031811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0045'
down_revision = '0044'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('price_per_hour', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('price_per_hour_currency', sa.String(length=8), nullable=True))


def downgrade():
    op.drop_column('user', 'price_per_hour_currency')
    op.drop_column('user', 'price_per_hour')
