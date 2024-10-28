"""add task review completed column

Revision ID: 0042
Revises: 0041
Create Date: 2022-03-22 18:01:19.673835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0042'
down_revision = '0041'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('review_completed', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade():
    op.drop_column('task', 'review_completed')
