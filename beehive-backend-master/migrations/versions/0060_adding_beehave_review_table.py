"""Adding beehave-review table

Revision ID: 0060
Revises: 0059
Create Date: 2023-08-30 17:47:28.410608

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0060'
down_revision = '0059'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('beehave_review',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('work_record_id', sa.Integer(), nullable=False),
    sa.Column('review_content', sa.JSON(), nullable=True),
    sa.Column('last_commit_sha', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['work_record_id'], ['work_record.id'], name='beehave_review_ibfk_1'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_beehave_review_work_record_id'), 'beehave_review', ['work_record_id'], unique=False)


def downgrade():
    op.drop_constraint('beehave_review_ibfk_1', 'beehave_review', type_='foreignkey')
    op.drop_index(op.f('ix_beehave_review_work_record_id'), table_name='beehave_review')
    op.drop_table('beehave_review')
