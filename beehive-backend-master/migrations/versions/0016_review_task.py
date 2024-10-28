"""Review task

Revision ID: 0016
Revises: 0015
Create Date: 2021-01-26 20:13:31.561852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('review_feedback', sa.Text(), nullable=True))
    op.add_column('task', sa.Column('review_status', sa.Enum('INADEQUATE', 'ADEQUATE', 'REQUIRES_MODIFICATION', name='reviewstatus'), nullable=True))


def downgrade():
    op.drop_column('task', 'review_status')
    op.drop_column('task', 'review_feedback')
