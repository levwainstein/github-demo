"""React task template types

Revision ID: 0035
Revises: 0034
Create Date: 2021-11-01 11:41:33.673913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0035'
down_revision = '0034'
branch_labels = None
depends_on = None

# TaskType enum types
new_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', name='tasktype')
old_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', name='tasktype')


def upgrade():
    op.alter_column('task_template', 'task_type', existing_type=old_task_type, type_=new_task_type, nullable=False)


def downgrade():
    op.alter_column('task_template', 'task_type', existing_type=new_task_type, type_=old_task_type, nullable=False)
