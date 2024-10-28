"""Pending action task type

Revision ID: 0008
Revises: 0007
Create Date: 2020-09-19 21:23:38.681096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None

# TaskStatus enum types
new_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', 'PENDING_ACTION', name='taskstatus')
old_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', name='taskstatus')


def upgrade():
    op.alter_column('task', 'status', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.alter_column('task', 'status', existing_type=new_type, type_=old_type, nullable=False)
