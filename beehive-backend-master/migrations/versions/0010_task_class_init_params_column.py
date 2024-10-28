"""task_class_init_params_column

Revision ID: 0010
Revises: 0009
Create Date: 2020-11-04 14:26:25.987576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('class_init_params', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('task', 'class_init_params')
