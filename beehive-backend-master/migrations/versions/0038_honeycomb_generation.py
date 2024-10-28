"""honeycomb generation

Revision ID: 0038
Revises: 0037
Create Date: 2021-12-01 23:31:21.047532

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0038'
down_revision = '0037'
branch_labels = None
depends_on = None

# TaskType enum types
new_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', name='tasktype')
old_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', name='tasktype')

# WorkType enum types
new_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', name='worktype')
old_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', name='worktype')


def upgrade():
    op.alter_column('task', 'task_type', existing_type=old_task_type, type_=new_task_type, nullable=False)
    op.alter_column('work', 'work_type', existing_type=old_work_type, type_=new_work_type, nullable=False)

    # create honeycomb generation user
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('INSERT INTO user (id, created, email, hashed_password, admin, team_id, notifications, first_name, last_name) VALUES ("00000000", NOW(), "system@beehivesoftware.com", "", FALSE, NULL, FALSE, "System", "User");'))
    session.commit()


def downgrade():
    # remove honeycomb generation user
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('DELETE FROM user where id="00000000";'))
    session.commit()

    op.alter_column('work', 'work_type', existing_type=new_work_type, type_=old_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=new_task_type, type_=old_task_type, nullable=False)
