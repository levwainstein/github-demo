from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0065'
down_revision = '0064'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('repository_id', sa.String(length=8), nullable=True))
    op.create_foreign_key('task_repo_c', 'task', 'repository', ['repository_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint('task_repo_c', 'task', type_='foreignkey')
    op.drop_column('task', 'repository_id')

