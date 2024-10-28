"""test cases as jsons

Revision ID: 0009
Revises: 0008
Create Date: 2020-10-27 18:24:55.026853

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('test_case', 'case_input',
               existing_type=mysql.TEXT(collation='utf8_bin'),
               type_=sa.JSON(),
               existing_nullable=False)


def downgrade():
    op.alter_column('test_case', 'case_input',
               existing_type=sa.JSON(),
               type_=mysql.TEXT(collation='utf8_bin'),
               existing_nullable=False)
