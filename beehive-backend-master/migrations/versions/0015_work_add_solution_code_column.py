"""work add solution code column

Revision ID: 0015
Revises: 0014
Create Date: 2021-01-19 15:23:00.749041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work', sa.Column('solution_code', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('work', 'solution_code')
