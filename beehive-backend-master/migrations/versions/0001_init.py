"""init

Revision ID: 0001
Revises: 
Create Date: 2020-07-25 12:35:14.011535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('hashed_password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('revoked_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=8), nullable=False),
    sa.Column('revoked', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_revoked_token_token_id'), 'revoked_token', ['token_id'], unique=False)
    op.create_table('task',
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('delegating_user_id', sa.String(length=8), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('func_name', sa.String(length=256), nullable=False),
    sa.Column('func_input', sa.String(length=512), nullable=True),
    sa.Column('status', sa.Enum('NEW', 'PENDING', 'PAUSED', 'IN_PROCESS', 'SOLVED', 'ACCEPTED', 'CANCELLED', name='taskstatus'), nullable=False),
    sa.Column('solution_code', sa.Text(), nullable=True),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('target_file', sa.Text(), nullable=False),
    sa.Column('absolute_target_file', sa.Text(), nullable=False),
    sa.Column('priority', sa.SmallInteger(), nullable=False),
    sa.Column('task_type', sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', name='tasktype'), nullable=False),
    sa.Column('original_code', sa.Text(), nullable=True),
    sa.Column('context', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['delegating_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_delegating_user_id'), 'task', ['delegating_user_id'], unique=False)
    op.create_index(op.f('ix_task_status'), 'task', ['status'], unique=False)
    op.create_table('test_case',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('case_input', sa.Text(), nullable=False),
    sa.Column('case_output', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_case_task_id'), 'test_case', ['task_id'], unique=False)
    op.create_table('work',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.String(length=8), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('tz_name', sa.String(length=48), nullable=False),
    sa.Column('duration_seconds', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_task_id'), 'work', ['task_id'], unique=False)
    op.create_index(op.f('ix_work_user_id'), 'work', ['user_id'], unique=False)


def downgrade():
    op.drop_table('work')
    op.drop_table('test_case')
    op.drop_table('task')
    op.drop_table('revoked_token')
    op.drop_table('user')
