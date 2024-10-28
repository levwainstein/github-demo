"""notify contributors

Revision ID: 0036
Revises: 0035
Create Date: 2021-11-03 12:10:42.046040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0036'
down_revision = '0035'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('notifications', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('user', 'notifications')
