"""add_installed_packages

Revision ID: 0004
Revises: 0003
Create Date: 2020-08-31 11:11:47.773574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('solution_packages', sa.JSON(), nullable=True))
    op.add_column('work', sa.Column('installed_packages', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('work', 'installed_packages')
    op.drop_column('task', 'solution_packages')
