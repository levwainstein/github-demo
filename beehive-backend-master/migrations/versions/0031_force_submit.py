"""force_submit

Revision ID: 0031
Revises: 0030
Create Date: 2021-07-18 09:01:51.742447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0031'
down_revision = '0030'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('force_submit_reason', sa.Text(), nullable=True))
    op.add_column('work_record', sa.Column('force_submit_reason', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('work_record', 'force_submit_reason')
    op.drop_column('task', 'force_submit_reason')
