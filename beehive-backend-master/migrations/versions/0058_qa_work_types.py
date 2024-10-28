"""qa work types

Revision ID: 0058
Revises: 0057
Create Date: 2023-07-19 14:13:44.303802

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0058'
down_revision = '0057'
branch_labels = None
depends_on = None


# WorkType enum types
new_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_REVIEW', 'CUCKOO_QA', name='worktype')
intermediate_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO', 'CUCKOO_CODING', 'CUCKOO_REVIEW', 'CUCKOO_QA', name='worktype')
old_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO', 'CUCKOO_REVIEW', name='worktype')

# TaskType enum types
new_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO_CODING', 'CUCKOO_REVIEW', name='tasktype')
intermediate_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO', 'CUCKOO_CODING', 'CUCKOO_REVIEW', name='tasktype')
old_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO', 'CUCKOO_REVIEW', name='tasktype')

def upgrade():
    # first add the new status values
    op.alter_column('work', 'work_type', existing_type=old_work_type, type_=intermediate_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=old_task_type, type_=intermediate_task_type, nullable=False)

    # then update every work of the old 'CUCKOO' type to the new 'CUCKOO_CODING' type
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work SET work_type=\'CUCKOO_CODING\' WHERE work_type=\'CUCKOO\';'))
    session.execute(text('UPDATE task SET task_type=\'CUCKOO_CODING\' WHERE task_type=\'CUCKOO\';'))
    session.commit()

    # finally remove the old 'CUCKOO' type
    op.alter_column('work', 'work_type', existing_type=intermediate_work_type, type_=new_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=intermediate_task_type, type_=new_task_type, nullable=False)


def downgrade():
    # go back to the intermediate state
    op.alter_column('work', 'work_type', existing_type=new_work_type, type_=intermediate_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=new_task_type, type_=intermediate_task_type, nullable=False)

    # update every task with a type we are removing back to 'CUCKOO' status
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work SET work_type=\'CUCKOO\' WHERE work_type=\'CUCKOO_CODING\';'))
    session.execute(text('UPDATE task SET task_type=\'CUCKOO\' WHERE task_type=\'CUCKOO_CODING\';'))
    session.commit()

    # remove the new types
    op.alter_column('work', 'work_type', existing_type=intermediate_work_type, type_=old_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=intermediate_task_type, type_=old_task_type, nullable=False)

