"""add work record solution rating

Revision ID: 0029
Revises: 0028
Create Date: 2021-05-13 15:05:53.629357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0029'
down_revision = '0028'
branch_labels = None
depends_on = None

# TaskStatus enum types
new_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', 'PENDING_CLASS_PARAMS', 'PENDING_PACKAGE', 'MODIFICATIONS_REQUESTED', name='taskstatus')
old_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', 'PENDING_CLASS_PARAMS', 'PENDING_PACKAGE', name='taskstatus')


def upgrade():
    op.add_column('work_record', sa.Column('solution_feedback', sa.Text(), nullable=True))
    op.add_column('work_record', sa.Column('solution_rating', sa.Enum('INADEQUATE', 'REQUIRES_MODIFICATION', 'ADEQUATE', name='solutionrating'), nullable=True))
    op.alter_column('task', 'status', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.drop_column('work_record', 'solution_rating')
    op.drop_column('work_record', 'solution_feedback')
    op.alter_column('task', 'status', existing_type=new_type, type_=old_type, nullable=False)
