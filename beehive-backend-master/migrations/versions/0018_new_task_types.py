"""New task types

Revision ID: 0018
Revises: 0017
Create Date: 2021-01-27 22:43:05.943972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0018'
down_revision = '0017'
branch_labels = None
depends_on = None


# TaskType enum types
new_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', name='tasktype')
old_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', name='tasktype')

def upgrade():
    op.alter_column('task', 'task_type', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.alter_column('task', 'task_type', existing_type=new_type, type_=old_type, nullable=False)
