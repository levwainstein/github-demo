"""update modified relationships

Revision ID: 0062
Revises: 0061
Create Date: 2024-01-02 19:01:44.213505

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0062'
down_revision = '0061'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('project_delegator', schema=None) as batch_op:
        batch_op.drop_constraint('project_delegator_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('revoked_token', schema=None) as batch_op:
        batch_op.drop_constraint('revoked_token_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('task_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['delegating_user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('task_classification', schema=None) as batch_op:
        batch_op.drop_index('_task_classification_uc')

    with op.batch_alter_table('user_code', schema=None) as batch_op:
        batch_op.drop_constraint('user_code_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('user_skill', schema=None) as batch_op:
        batch_op.drop_constraint('user_skill_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('user_tag', schema=None) as batch_op:
        batch_op.drop_constraint('user_tag_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('work', schema=None) as batch_op:
        batch_op.drop_constraint('work_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['reserved_worker_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('work_record', schema=None) as batch_op:
        batch_op.drop_constraint('work_record_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('work_record', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('work_record_ibfk_2', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('work', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('work_ibfk_2', 'user', ['reserved_worker_id'], ['id'])

    with op.batch_alter_table('user_tag', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('user_tag_ibfk_2', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user_skill', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('user_skill_ibfk_2', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user_code', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('user_code_ibfk_1', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('task_classification', schema=None) as batch_op:
        batch_op.create_index('_task_classification_uc', ['task_type', 'task_id'], unique=True)

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('task_ibfk_1', 'user', ['delegating_user_id'], ['id'])

    with op.batch_alter_table('revoked_token', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('revoked_token_ibfk_1', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('project_delegator', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('project_delegator_ibfk_2', 'user', ['user_id'], ['id'])
