"""update user profile

Revision ID: 0043
Revises: 0042
Create Date: 2022-03-23 13:46:02.968093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0043'
down_revision = '0042'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('availability_weekly_hours', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('github_user', sa.String(length=256), nullable=True))
    op.add_column('user', sa.Column('trello_user', sa.String(length=256), nullable=True))


def downgrade():
    op.drop_column('user', 'trello_user')
    op.drop_column('user', 'github_user')
    op.drop_column('user', 'availability_weekly_hours')
