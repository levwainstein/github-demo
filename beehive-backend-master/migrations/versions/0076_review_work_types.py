"""review work types

Revision ID: 0076
Revises: 0075
Create Date: 2024-06-06 12:46:44.303802

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0076'
down_revision = '0075'
branch_labels = None
depends_on = None


# WorkType enum types
new_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_ITERATION', 'CUCKOO_QA', name='worktype')
intermediate_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_ITERATION', 'CUCKOO_QA', 'CUCKOO_REVIEW', name='worktype')
old_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_REVIEW', 'CUCKOO_QA', name='worktype')

# TaskType enum types
new_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_ITERATION', name='tasktype')
intermediate_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY',  'CUCKOO_CODING', 'CUCKOO_REVIEW', 'CUCKOO_ITERATION', name='tasktype')
old_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_REVIEW', name='tasktype')



def upgrade():

    # first add the new status values
    op.alter_column('work', 'work_type', existing_type=old_work_type, type_=intermediate_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=old_task_type, type_=intermediate_task_type, nullable=False)

    # then update every work of the old 'CUCKOO' type to the new 'CUCKOO_CODING' type
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work SET work_type=\'CUCKOO_ITERATION\' WHERE work_type=\'CUCKOO_REVIEW\';'))
    session.execute(text('UPDATE task SET task_type=\'CUCKOO_ITERATION\' WHERE task_type=\'CUCKOO_REVIEW\';'))
    session.commit()

    # finally remove the old 'CUCKOO_REVIEW' type
    op.alter_column('work', 'work_type', existing_type=intermediate_work_type, type_=new_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=intermediate_task_type, type_=new_task_type, nullable=False)

    with op.batch_alter_table('work_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('review_start_time_epoch_ms', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('review_tz_name', sa.String(length=48), nullable=True))
        batch_op.add_column(sa.Column('review_duration_seconds', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('review_user_id', sa.String(length=8), nullable=True))
        batch_op.create_index(batch_op.f('ix_work_record_review_user_id'), ['review_user_id'], unique=False)
        batch_op.create_foreign_key('fk_review_user_id', 'user', ['review_user_id'], ['id'], ondelete='CASCADE')


def downgrade():

    with op.batch_alter_table('work_record', schema=None) as batch_op:
        batch_op.drop_constraint('fk_review_user_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_work_record_review_user_id'))
        batch_op.drop_column('review_user_id')
        batch_op.drop_column('review_duration_seconds')
        batch_op.drop_column('review_tz_name')
        batch_op.drop_column('review_start_time_epoch_ms')

    # go back to the intermediate state
    op.alter_column('work', 'work_type', existing_type=new_work_type, type_=intermediate_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=new_task_type, type_=intermediate_task_type, nullable=False)

    # update every task with a type we are removing back to 'CUCKOO' status
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work SET work_type=\'CUCKOO_REVIEW\' WHERE work_type=\'CUCKOO_ITERATION\';'))
    session.execute(text('UPDATE task SET task_type=\'CUCKOO_REVIEW\' WHERE task_type=\'CUCKOO_ITERATION\';'))
    session.commit()

    # remove the new types
    op.alter_column('work', 'work_type', existing_type=intermediate_work_type, type_=old_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=intermediate_task_type, type_=old_task_type, nullable=False)

