"""cuckoo fields and add tags-skills to work-task

Revision ID: 0046
Revises: 0045
Create Date: 2022-05-26 15:57:24.234896

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0067'
down_revision = '0066'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_template_skill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_template_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.id'], ),
    sa.ForeignKeyConstraint(['task_template_id'], ['task_template.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_template_id', 'skill_id', name='_task_template_skill_uc')
    )


def downgrade():
    op.drop_table('task_template_skill')
    
