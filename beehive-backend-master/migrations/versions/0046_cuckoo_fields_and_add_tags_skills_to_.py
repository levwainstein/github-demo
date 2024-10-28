"""cuckoo fields and add tags-skills to work-task

Revision ID: 0046
Revises: 0045
Create Date: 2022-05-26 15:57:24.234896

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0046'
down_revision = '0045'
branch_labels = None
depends_on = None

# TaskType enum types
new_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO', 'CUCKOO_REVIEW', name='tasktype')
old_task_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', name='tasktype')

# WorkType enum types
new_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', 'CUCKOO', 'CUCKOO_REVIEW', name='worktype')
old_work_type = sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', 'OPEN_TASK', 'CREATE_REACT_COMPONENT', 'UPDATE_REACT_COMPONENT', 'CHECK_REUSABILITY', name='worktype')


def upgrade():
    op.create_table('task_skill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id', 'skill_id', name='_task_skill_uc')
    )
    op.create_table('task_tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id', 'tag_id', name='_task_tag_uc')
    )
    op.create_table('work_skill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.id'], ),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('work_id', 'skill_id', name='_work_skill_uc')
    )
    op.create_table('work_tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('work_id', 'tag_id', name='_work_tag_uc')
    )
    op.alter_column('task', 'absolute_target_file',
               existing_type=mysql.TEXT(charset='utf8', collation='utf8_bin'),
               nullable=True)
    op.alter_column('task', 'target_file',
               existing_type=mysql.TEXT(charset='utf8', collation='utf8_bin'),
               nullable=True)
    op.alter_column('work', 'work_input',
               existing_type=mysql.TEXT(charset='utf8', collation='utf8_bin'),
               type_=sa.JSON(),
               nullable=True)
    op.add_column('work_record', sa.Column('result', sa.Text(), nullable=True))
    op.alter_column('task', 'task_type', existing_type=old_task_type, type_=new_task_type, nullable=False)
    op.alter_column('work', 'work_type', existing_type=old_work_type, type_=new_work_type, nullable=False)


def downgrade():
    op.drop_column('work_record', 'result')
    op.alter_column('work', 'work_input',
               existing_type=sa.JSON(),
               type_=mysql.TEXT(charset='utf8', collation='utf8_bin'),
               nullable=False)
    op.alter_column('task', 'target_file',
               existing_type=mysql.TEXT(charset='utf8', collation='utf8_bin'),
               nullable=False)
    op.alter_column('task', 'absolute_target_file',
               existing_type=mysql.TEXT(charset='utf8', collation='utf8_bin'),
               nullable=False)
    op.drop_table('work_tag')
    op.drop_table('work_skill')
    op.drop_table('task_tag')
    op.drop_table('task_skill')
    op.alter_column('work', 'work_type', existing_type=new_work_type, type_=old_work_type, nullable=False)
    op.alter_column('task', 'task_type', existing_type=new_task_type, type_=old_task_type, nullable=False)
