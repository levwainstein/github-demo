"""Review task nullable

Revision ID: 0017
Revises: 0016
Create Date: 2021-01-27 22:17:31.291195

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0017'
down_revision = '0016'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('task', 'review_status',
               existing_type=mysql.ENUM('INADEQUATE', 'ADEQUATE', 'REQUIRES_MODIFICATION', collation='utf8_bin'),
               type_=sa.Enum('INADEQUATE', 'REQUIRES_MODIFICATION', 'ADEQUATE', name='reviewstatus'),
               existing_nullable=True)


def downgrade():
    op.alter_column('task', 'review_status',
               existing_type=sa.Enum('INADEQUATE', 'REQUIRES_MODIFICATION', 'ADEQUATE', name='reviewstatus'),
               type_=mysql.ENUM('INADEQUATE', 'ADEQUATE', 'REQUIRES_MODIFICATION', collation='utf8_bin'),
               existing_nullable=True)
