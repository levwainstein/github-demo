"""React task and work types

Revision ID: 0033
Revises: 0032
Create Date: 2021-08-12 21:41:33.673913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0033'
down_revision = '0032'
branch_labels = None
depends_on = None

# TaskType enum types
new_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', name='tasktype')
old_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', name='tasktype')

# WorkType enum types
new_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', name='worktype')
old_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', name='worktype')


def upgrade():
    op.alter_column('task', 'task_type', existing_type=old_task_type, type_=new_task_type, nullable=False)
    op.alter_column('work', 'work_type', existing_type=old_work_type, type_=new_work_type, nullable=False)


def downgrade():
    op.alter_column('work', 'work_type', existing_type=new_work_type, type_=old_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=new_task_type, type_=old_task_type, nullable=False)
