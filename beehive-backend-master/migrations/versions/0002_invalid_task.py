"""invalid_task

Revision ID: 0002
Revises: 0001
Create Date: 2020-08-09 13:31:29.109081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


# TaskStatus enum types
old_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', name='taskstatus')
new_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', name='taskstatus')


def upgrade():
    op.alter_column('task', 'status', existing_type=old_type, type_=new_type, nullable=False)
    op.add_column('task', sa.Column('invalid_code', sa.String(length=64), nullable=True))
    op.add_column('task', sa.Column('invalid_description', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('task', 'invalid_description')
    op.drop_column('task', 'invalid_code')
    op.alter_column('task', 'status', existing_type=new_type, type_=old_type, nullable=False)
