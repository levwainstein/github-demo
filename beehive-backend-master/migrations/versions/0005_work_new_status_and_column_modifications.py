"""work_new_status_and_column_modifications

Revision ID: 0005
Revises: 0004
Create Date: 2020-09-01 10:44:26.349780

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # create start_time_epoch_ms column, populate it by converting datetime
    # values from start_time column and then delete start_time column
    op.add_column('work', sa.Column('start_time_epoch_ms', sa.BigInteger(), nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work SET start_time_epoch_ms=UNIX_TIMESTAMP(start_time)*1000;'))
    session.commit()
    op.drop_column('work', 'start_time')

    # first add the column with a server default value of 'SOLVED' so existing
    # rows get that value and then remove the default values so new rows have
    # to be set a status
    op.add_column('work', sa.Column('status', sa.Enum('IN_PROCESS', 'SOLVED', 'CANCELLED', 'FEEDBACK', name='workstatus'), nullable=False, server_default='SOLVED'))
    op.alter_column('work', 'status', server_default=None)

    op.alter_column('work', 'duration_seconds',
               existing_type=mysql.INTEGER(),
               nullable=True)


def downgrade():
    # re-create start_time column, populate it by converting start_time_epoch_ms
    # values and set it to not-null and remove start_time_epoch_ms column
    op.add_column('work', sa.Column('start_time', mysql.DATETIME(), nullable=True))
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work SET start_time=FROM_UNIXTIME(start_time_epoch_ms/1000);'))
    session.commit()
    op.alter_column('work', 'start_time', existing_type=mysql.DATETIME(), nullable=False)
    op.drop_column('work', 'start_time_epoch_ms')

    op.alter_column('work', 'duration_seconds',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_column('work', 'status')
