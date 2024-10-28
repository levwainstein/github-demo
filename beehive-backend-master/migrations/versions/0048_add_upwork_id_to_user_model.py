"""add upwork id to user model

Revision ID: 0048
Revises: 0047
Create Date: 2022-12-26 14:47:57.393534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0048'
down_revision = '0047'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('upwork_user', sa.String(length=256), nullable=True))


def downgrade():
    op.drop_column('user', 'upwork_user')
