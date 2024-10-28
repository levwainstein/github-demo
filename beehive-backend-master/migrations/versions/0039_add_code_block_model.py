"""add code block model

Revision ID: 0039
Revises: 0038
Create Date: 2022-01-05 11:28:14.126370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0039'
down_revision = '0038'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('code_block',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('block_file', sa.Text(), nullable=False),
    sa.Column('start_index', sa.Integer(), nullable=False),
    sa.Column('end_index', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_block_task_id'), 'code_block', ['task_id'], unique=False)


def downgrade():
    # dropping the table should also drop the created index
    op.drop_table('code_block')
