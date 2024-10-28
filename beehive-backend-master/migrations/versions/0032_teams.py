"""teams

Revision ID: 0032
Revises: 0031
Create Date: 2021-08-11 21:41:50.828172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0032'
down_revision = '0031'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('team',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('admin_user_id', sa.String(length=8), nullable=False),
    sa.ForeignKeyConstraint(['admin_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('task', sa.Column('delegating_team_id', sa.String(length=8), nullable=True))
    op.create_index(op.f('ix_task_delegating_team_id'), 'task', ['delegating_team_id'], unique=False)
    op.create_foreign_key('fk_task_delegating_team_id', 'task', 'team', ['delegating_team_id'], ['id'])
    op.add_column('user', sa.Column('team_id', sa.String(length=8), nullable=True))
    op.create_foreign_key('fk_user_team_id', 'user', 'team', ['team_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_user_team_id', 'user', type_='foreignkey')
    op.drop_column('user', 'team_id')
    op.drop_constraint('fk_task_delegating_team_id', 'task', type_='foreignkey')
    op.drop_index(op.f('ix_task_delegating_team_id'), table_name='task')
    op.drop_column('task', 'delegating_team_id')
    op.drop_table('team')
