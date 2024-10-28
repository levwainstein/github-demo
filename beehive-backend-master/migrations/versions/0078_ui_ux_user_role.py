"""ui ux user role

Revision ID: 0078
Revises: 0077
Create Date: 2024-07-29 12:48:01.722304

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0078'
down_revision = '0077'
branch_labels = None
depends_on = None

# UserRole enum types
new_type = sa.Enum('CORE_TEAM','TECH_LEAD','QA_CONTRIBUTOR','CONTRIBUTOR', 'PROJECT_MANAGER', 'UI_UX', name='userrole')
old_type = sa.Enum('CORE_TEAM','TECH_LEAD','QA_CONTRIBUTOR','CONTRIBUTOR', 'PROJECT_MANAGER', name='userrole')

def upgrade():
    op.alter_column('external_user_role', 'role', existing_type=old_type, type_=new_type, nullable=False)


def downgrade():
    op.alter_column('external_user_role', 'role', existing_type=new_type, type_=old_type, nullable=False)
