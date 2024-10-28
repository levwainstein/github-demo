"""task templates

Revision ID: 0025
Revises: 0024
Create Date: 2021-03-10 21:27:46.523991

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0025'
down_revision = '0024'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_template',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), unique=True, nullable=False),
    sa.Column('task_description', sa.Text(), nullable=False),
    sa.Column('task_type', sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', name='tasktype'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_template_name'), 'task_template', ['name'], unique=False)
    op.alter_column('task', 'func_name',
               existing_type=mysql.VARCHAR(collation='utf8_bin', length=256),
               nullable=True)


def downgrade():
    op.alter_column('task', 'func_name',
               existing_type=mysql.VARCHAR(collation='utf8_bin', length=256),
               nullable=False)
    op.drop_index(op.f('ix_task_template_name'), table_name='task_template')
    op.drop_table('task_template')
