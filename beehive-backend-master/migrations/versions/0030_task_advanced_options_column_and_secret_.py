"""task advanced options column and secret-task fk

Revision ID: 0030
Revises: 0029
Create Date: 2021-06-29 18:30:07.667027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0030'
down_revision = '0029'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(None, 'secret', 'task', ['task_id'], ['id'])
    op.add_column('task', sa.Column('advanced_options', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('task', 'advanced_options')
    op.drop_constraint(None, 'secret', type_='foreignkey')
