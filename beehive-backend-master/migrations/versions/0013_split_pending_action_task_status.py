"""split pending action task status

Revision ID: 0013
Revises: 0012
Create Date: 2021-01-12 11:46:30.018163

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()


revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


# TaskStatus enum types
new_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', 'PENDING_CLASS_PARAMS', 'PENDING_PACKAGE', name='taskstatus')
intermediate_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', 'PENDING_ACTION', 'PENDING_CLASS_PARAMS', 'PENDING_PACKAGE', name='taskstatus')
old_type = sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', 'INVALID', 'PENDING_ACTION', name='taskstatus')


def upgrade():
    # first add the new status values
    op.alter_column('task', 'status', existing_type=old_type, type_=intermediate_type, nullable=False)

    # then update every task of the old 'PENDING_ACTION' status to the new 'PENDING_CLASS_PARAMS' status
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE task SET status=\'PENDING_CLASS_PARAMS\' WHERE status=\'PENDING_ACTION\';'))
    session.commit()

    # finally remove the old 'PENDING_ACTION' status
    op.alter_column('task', 'status', existing_type=intermediate_type, type_=new_type, nullable=False)


def downgrade():
    # go back to the intermediate state
    op.alter_column('task', 'status', existing_type=new_type, type_=intermediate_type, nullable=False)

    # update every task with a status we are removing back to 'PENDING_ACTION' status
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE task SET status=\'PENDING_ACTION\' WHERE status in (\'PENDING_CLASS_PARAMS\', \'PENDING_PACKAGE\');'))
    session.commit()

    # remove the new statuses
    op.alter_column('task', 'status', existing_type=intermediate_type, type_=old_type, nullable=False)
