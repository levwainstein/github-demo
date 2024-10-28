from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0054'
down_revision = '0053'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('repo_link', sa.Text(), nullable=True),
    sa.Column('trello_link', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_name'), 'project', ['name'], unique=False)
    
    op.create_table('project_delegator',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=8), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'project_id', name='_project_delegator_uc')
    )

    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text("insert into project ( select tag.id as id, SUBSTRING(tag.name, 9, 100) as name, 'missing' as trello_link, 'missing' as repo_link from tag where tag.name like 'project:%' );"))
    session.commit()


def downgrade():
    op.drop_table('project_delegator')
    op.drop_index(op.f('ix_project_name'), table_name='project')
    op.drop_table('project')

