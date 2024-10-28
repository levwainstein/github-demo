"""add work record feedback column

Revision ID: 0028
Revises: 0027
Create Date: 2021-05-06 11:31:32.421677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0028'
down_revision = '0027'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work_record', sa.Column('feedback', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('work_record', 'feedback')
