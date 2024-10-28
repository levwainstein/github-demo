from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0069'
down_revision = '0068'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('delegation_time_seconds', sa.Integer(), nullable=True))
    op.add_column('task_template', sa.Column('task_classification', sa.Enum(
        'CREATE_COMPONENT',
        'MODIFY_COMPONENT',
        'CREATE_PAGE',
        'MODIFY_PAGE',
        'MODIFY_DESIGN',
        'CREATE_ANIMATION',
        'CREATE_EVENT',
        'CREATE_DATA_MODEL',
        'CREATE_ENDPOINT',
        'CREATE_DJANGO_VIEW',
        'MODIFY_DJANGO_VIEW',
        'CREATE_ALGORITHM',
        'CREATE_SCRAPER',
        'CREATE_API_CONNECTOR',
        'REFACTOR_CODE',
        'CREATE_TEST_CASE',
        'CREATE_AUTH',
        'OTHER',
        'UNCERTAIN', name='taskclassification'), nullable=True))
    
    

def downgrade():
    op.drop_column('task', 'delegation_time_seconds')
    op.drop_column('task_template', 'task_classification')
    
