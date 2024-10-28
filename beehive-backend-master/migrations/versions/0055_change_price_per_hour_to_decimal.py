"""change price per hour to decimal

Revision ID: 0055
Revises: 0054
Create Date: 2023-06-08 10:40:13.788188

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0055'
down_revision = '0054'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'price_per_hour',
               existing_type=mysql.INTEGER(),
               type_=sa.DECIMAL(precision=5, scale=2),
               existing_nullable=True)


def downgrade():
    op.alter_column('user', 'price_per_hour',
               existing_type=sa.DECIMAL(precision=5, scale=2),
               type_=mysql.INTEGER(),
               existing_nullable=True)
