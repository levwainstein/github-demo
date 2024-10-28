"""add upwork duration columns

Revision ID: 0051
Revises: 0050
Create Date: 2023-02-16 14:37:22.758611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0051'
down_revision = '0050'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work_record_upwork_diary', sa.Column('upwork_cost', sa.DECIMAL(precision=12, scale=2), nullable=True))
    op.add_column('work_record_upwork_diary', sa.Column('upwork_duration_seconds', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('work_record_upwork_diary', 'upwork_duration_seconds')
    op.drop_column('work_record_upwork_diary', 'upwork_cost')
