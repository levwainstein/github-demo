"""project manager external worker

Revision ID: 0074
Revises: 0073
Create Date: 2024-05-15 13:05:01.066960

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0074'
down_revision = '0073'
branch_labels = None
depends_on = None

# UserRole enum types
new_type = sa.Enum('CORE_TEAM','TECH_LEAD','QA_CONTRIBUTOR','CONTRIBUTOR', 'PROJECT_MANAGER', name='taskstatus')
old_type = sa.Enum('CORE_TEAM','TECH_LEAD','QA_CONTRIBUTOR','CONTRIBUTOR', name='taskstatus')

def upgrade():
    op.alter_column('external_user_role', 'role', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.alter_column('external_user_role', 'role', existing_type=new_type, type_=old_type, nullable=False)
