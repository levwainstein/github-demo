"""prohibit work

Revision ID: 0047
Revises: 0046
Create Date: 2022-09-30 09:48:03.736600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0047'
down_revision = '0046'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work', sa.Column('prohibited_worker_id', sa.String(length=8), nullable=True))
    op.create_foreign_key(None, 'work', 'user', ['prohibited_worker_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_column('work', 'prohibited_worker_id')
