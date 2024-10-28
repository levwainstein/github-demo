"""add work priority column
Revision ID: 0049
Revises: 0048
Create Date: 2022-12-13 11:28:43.817038
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '0049'
down_revision = '0048'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('work', sa.Column('priority', sa.SmallInteger(), nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE work w INNER JOIN task t ON w.task_id = t.id SET w.priority = t.priority;'))
    session.commit()


def downgrade():
    op.drop_column('work', 'priority')
