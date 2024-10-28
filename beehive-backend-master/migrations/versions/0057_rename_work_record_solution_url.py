"""rename work record solution url

Revision ID: 0057
Revises: 0056
Create Date: 2023-07-17 16:05:07.267694

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0057'
down_revision = '0056'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('work_record', 'result', new_column_name='solution_url', existing_type=mysql.TEXT(charset='utf8mb3', collation='utf8_bin'))


def downgrade():
    op.alter_column('work_record', 'solution_url', new_column_name='result', existing_type=mysql.TEXT(charset='utf8mb3', collation='utf8_bin'))