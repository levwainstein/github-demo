"""task_add_available_names_column

Revision ID: 0011
Revises: 0010
Create Date: 2021-01-04 12:11:34.259028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('available_names', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('task', 'available_names')
