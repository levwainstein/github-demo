from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0063'
down_revision = '0062'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('repository',
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='repository_project_link'),
    )
    op.create_index(op.f('ix_repository_name'), 'repository', ['name'], unique=False)


def downgrade():
    op.drop_constraint('repository_project_link', 'repository', type_='foreignkey')
    op.drop_index(op.f('ix_repository_name'), table_name='repository')
    op.drop_table('repository')

