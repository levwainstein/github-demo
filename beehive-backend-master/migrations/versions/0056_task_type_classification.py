"""task type classification
Revision ID: 0056
Revises: 0055
Create Date: 2023-05-16 16:51:38.849191
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0056'
down_revision = '0055'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('task_classification',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_type', sa.Enum(
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
        'UNCERTAIN', name='tasktypeclassification'), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint('_task_classification_uc', 'task_classification', ['task_type', 'task_id'])    


def downgrade():
    op.drop_constraint('_task_classification_uc', 'task_classification', type_='unique')
    op.drop_table('task_classification')
