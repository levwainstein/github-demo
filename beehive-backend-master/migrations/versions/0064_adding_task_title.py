from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0064'
down_revision = '0063'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('title', sa.String(length=256), nullable=True))

def downgrade():
    op.drop_column('task', 'title')
