"""user first and last name

Revision ID: 0037
Revises: 0036
Create Date: 2021-11-10 17:55:33.640878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0037'
down_revision = '0036'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('first_name', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
