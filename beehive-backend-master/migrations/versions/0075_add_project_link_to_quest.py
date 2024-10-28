"""add_project_link_to_quest

Revision ID: 0075
Revises: 0074
Create Date: 2024-06-03 12:56:26.421682

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0075'
down_revision = '0074'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('quest', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_foreign_key('quest_project_c', 'quest', 'project', ['project_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint('quest_project_c', 'quest', type_='foreignkey')
    op.drop_column('quest', 'project_id')
