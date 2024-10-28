"""add secret model and columns

Revision ID: 0024
Revises: 0023
Create Date: 2021-03-11 14:44:27.808665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0024'
down_revision = '0023'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('secret',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('encrypted_value', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secret_task_id'), 'secret', ['task_id'], unique=False)

    op.add_column('task', sa.Column('secret_key', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('task', 'secret_key')

    op.drop_index(op.f('ix_secret_task_id'), table_name='secret')
    op.drop_table('secret')
