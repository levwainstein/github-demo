"""quest delegation

Revision ID: 0079
Revises: 0078
Create Date: 2024-06-21 10:33:22.793863

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0079'
down_revision = '0078'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('success_criteria',
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('quest_id', sa.String(length=8), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['quest_id'], ['quest.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('success_criteria', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_success_criteria_quest_id'), ['quest_id'], unique=False)

    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.add_column(sa.Column('delegation_time_seconds', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_quest_project_id'), ['project_id'], unique=False)
        batch_op.drop_constraint('quest_project_c', type_='foreignkey')
        batch_op.create_foreign_key(None, 'project', ['project_id'], ['id'], ondelete='SET NULL')


def downgrade():
    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.drop_column('delegation_time_seconds')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('quest_project_c', 'project', ['project_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_index(batch_op.f('ix_quest_project_id'))

    with op.batch_alter_table('success_criteria', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_success_criteria_quest_id'))

    op.drop_table('success_criteria')
