"""update work and work record models

Revision ID: 0022
Revises: 0021
Create Date: 2021-02-18 18:03:59.430609

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '0022'
down_revision = '0021'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work_record', sa.Column('active', sa.Boolean(), nullable=False))
    op.add_column('work_record', sa.Column('work_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_work_record_work_id'), 'work_record', ['work_id'], unique=False)
    op.drop_constraint('work_record_ibfk_1', 'work_record', type_='foreignkey')
    op.drop_index('ix_work_record_task_id', table_name='work_record')

    # calculate work_id for each work record
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work_record wr INNER JOIN work w ON wr.task_id = w.task_id SET wr.work_id = w.id;'))
    session.commit()

    op.create_foreign_key(None, 'work_record', 'work', ['work_id'], ['id'])
    op.drop_column('work_record', 'task_id')
    op.drop_column('work_record', 'status')


def downgrade():
    op.add_column('work_record', sa.Column('status', mysql.ENUM('IN_PROCESS', 'SOLVED', 'CANCELLED', 'FEEDBACK', 'PACKAGE_REQUEST', collation='utf8_bin'), nullable=False))
    op.add_column('work_record', sa.Column('task_id', mysql.VARCHAR(collation='utf8_bin', length=8), nullable=False))
    op.drop_constraint('work_record_ibfk_3', 'work_record', type_='foreignkey')

    # calculate task_id for each work record
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work_record wr INNER JOIN work w ON wr.work_id = w.id SET wr.task_id = w.task_id;'))
    session.commit()

    op.create_foreign_key('work_record_ibfk_1', 'work_record', 'task', ['task_id'], ['id'])
    op.create_index('ix_work_record_task_id', 'work_record', ['task_id'], unique=False)
    op.drop_index(op.f('ix_work_record_work_id'), table_name='work_record')
    op.drop_column('work_record', 'work_id')
    op.drop_column('work_record', 'active')
