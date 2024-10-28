"""Add open task to work type

Revision ID: 0023
Revises: 0023
Create Date: 2021-03-06 18:41:08.789856

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0023'
down_revision = '0022'
branch_labels = None
depends_on = None

# TaskType enum types
new_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', name='worktype')
old_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', name='worktype')


def upgrade():
    op.alter_column('work', 'work_type', existing_type=old_type, type_=new_type, nullable=False)

def downgrade():
    op.alter_column('work', 'work_type', existing_type=new_type, type_=old_type, nullable=False)
