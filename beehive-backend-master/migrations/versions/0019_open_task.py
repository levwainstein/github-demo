"""Open task

Revision ID: 0019
Revises: 0018
Create Date: 2021-02-13 19:57:33.673913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0019'
down_revision = '0018'
branch_labels = None
depends_on = None

# TaskType enum types
new_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', name='tasktype')
old_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', name='tasktype')


def upgrade():
    op.alter_column('task', 'task_type', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.alter_column('task', 'task_type', existing_type=new_type, type_=old_type, nullable=False)
