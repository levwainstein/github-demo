"""quest feature

Revision ID: 0070
Revises: 0069
Create Date: 2024-02-29 17:50:11.214301

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0070'
down_revision = '0069'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('quest',
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('delegating_user_id', sa.String(length=8), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('NEW', 'IN_PROCESS', 'IN_REVIEW', 'DONE', name='queststatus'), nullable=False),
    sa.Column('quest_type', sa.Enum('FEATURE', 'BUG', name='questtype'), nullable=False),
    sa.Column('links', sa.JSON(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['delegating_user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_quest_delegating_user_id'), ['delegating_user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_quest_status'), ['status'], unique=False)

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quest_id', sa.String(length=8), nullable=True))
        batch_op.create_index(batch_op.f('ix_task_quest_id'), ['quest_id'], unique=False)
        batch_op.create_foreign_key(None, 'quest', ['quest_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_task_quest_id'))
        batch_op.drop_column('quest_id')

    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_quest_status'))
        batch_op.drop_index(batch_op.f('ix_quest_delegating_user_id'))

    op.drop_table('quest')
