"""package request

Revision ID: 0012
Revises: 0011
Create Date: 2021-01-11 18:51:30.018163

"""
from alembic import op
import sqlalchemy as sa


revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


# WorkStatus enum types
new_type = sa.Enum('IN_PROCESS', 'SOLVED', 'CANCELLED', 'FEEDBACK', 'PACKAGE_REQUEST', name='workstatus')
old_type = sa.Enum('IN_PROCESS', 'SOLVED', 'CANCELLED', 'FEEDBACK', name='workstatus')


def upgrade():
    op.add_column('work', sa.Column('requested_package', sa.String(length=256), nullable=True))
    op.alter_column('work', 'status', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.drop_column('work', 'requested_package')
    op.alter_column('work', 'status', existing_type=new_type, type_=old_type, nullable=False)
