"""add upwork user name

Revision ID: 0053
Revises: 0052
Create Date: 2023-03-21 23:46:52.252663

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0053'
down_revision = '0052'
branch_labels = None
depends_on = None


def upgrade():

    op.drop_constraint('_upwork_diary_uc', 'upwork_diary', type_='unique')
    op.drop_index('ix_upwork_diary_upwork_user', table_name='upwork_diary')
    op.alter_column('upwork_diary',
                     column_name = 'upwork_user',
                     new_column_name = 'upwork_user_id',
                     existing_type = sa.String(256),
                     existing_nullable = False)
    op.add_column('upwork_diary', sa.Column('upwork_user_name', sa.String(length=256), nullable=False))
    op.create_index(op.f('ix_upwork_diary_upwork_user_id'), 'upwork_diary', ['upwork_user_id'], unique=False)
    op.create_index(op.f('ix_upwork_diary_upwork_user_name'), 'upwork_diary', ['upwork_user_name'], unique=False)
    op.create_unique_constraint('_upwork_diary_uc', 'upwork_diary', ['upwork_user_id', 'start_time_epoch_ms'])


def downgrade():
    op.drop_constraint('_upwork_diary_uc', 'upwork_diary', type_='unique')
    op.drop_index(op.f('ix_upwork_diary_upwork_user_name'), table_name='upwork_diary')
    op.drop_index(op.f('ix_upwork_diary_upwork_user_id'), table_name='upwork_diary')
    op.drop_column('upwork_diary', 'upwork_user_name')
    op.alter_column('upwork_diary',
                     column_name = 'upwork_user_id',
                     new_column_name = 'upwork_user',
                     existing_type = sa.String(256),
                     existing_nullable = False)
    op.create_index('ix_upwork_diary_upwork_user', 'upwork_diary', ['upwork_user'], unique=False)
    op.create_unique_constraint('_upwork_diary_uc', 'upwork_diary', ['upwork_user', 'start_time_epoch_ms', 'end_time_epoch_ms'])
