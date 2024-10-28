"""work_record_outcome_column

Revision ID: 0052
Revises: 0051
Create Date: 2023-02-22 12:20:03.137482

"""
from alembic import op
import sqlalchemy as sa

revision = '0052'
down_revision = '0051'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work_record', sa.Column('outcome', sa.Enum('REQUESTED_PACKAGE', 'FEEDBACK', 'SOLVED', 'CANCELLED', 'SKIPPED', 'TASK_CANCELLED', name='workoutcome'), nullable=True))

def downgrade():
    op.drop_column('work_record', 'outcome')
