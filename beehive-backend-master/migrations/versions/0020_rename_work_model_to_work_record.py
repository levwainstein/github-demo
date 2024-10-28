"""rename work model to work record

Revision ID: 0020
Revises: 0019
Create Date: 2021-02-17 15:55:36.810272

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0020'
down_revision = '0019'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(constraint_name='work_ibfk_1', table_name='work', type_='foreignkey')
    op.drop_constraint(constraint_name='work_ibfk_2', table_name='work', type_='foreignkey')
    op.drop_index('ix_work_task_id', table_name='work')
    op.drop_index('ix_work_user_id', table_name='work')

    op.rename_table('work', 'work_record')

    op.create_foreign_key(
        constraint_name='work_record_ibfk_1',
        source_table='work_record',
        referent_table='task',
        local_cols=['task_id'],
        remote_cols=['id']
    )
    op.create_foreign_key(
        constraint_name='work_record_ibfk_2',
        source_table='work_record',
        referent_table='user',
        local_cols=['user_id'],
        remote_cols=['id']
    )
    op.create_index(op.f('ix_work_record_task_id'), 'work_record', ['task_id'], unique=False)
    op.create_index(op.f('ix_work_record_user_id'), 'work_record', ['user_id'], unique=False)


def downgrade():
    op.drop_constraint(constraint_name='work_record_ibfk_1', table_name='work_record', type_='foreignkey')
    op.drop_constraint(constraint_name='work_record_ibfk_2', table_name='work_record', type_='foreignkey')
    op.drop_index('ix_work_record_task_id', table_name='work_record')
    op.drop_index('ix_work_record_user_id', table_name='work_record')

    op.rename_table('work_record', 'work')

    op.create_foreign_key(
        constraint_name='work_ibfk_1',
        source_table='work',
        referent_table='task',
        local_cols=['task_id'],
        remote_cols=['id']
    )
    op.create_foreign_key(
        constraint_name='work_ibfk_2',
        source_table='work',
        referent_table='user',
        local_cols=['user_id'],
        remote_cols=['id']
    )
    op.create_index(op.f('ix_work_task_id'), 'work', ['task_id'], unique=False)
    op.create_index(op.f('ix_work_user_id'), 'work', ['user_id'], unique=False)
