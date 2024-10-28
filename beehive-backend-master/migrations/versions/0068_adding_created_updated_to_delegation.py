"""make_work

Revision ID: 0068
Revises: 0067
Create Date: 2024-02-20 19:46:14.423530

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0068'
down_revision = '0067'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('updated', sa.DateTime(), nullable=True))


    with op.batch_alter_table('repository', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('updated', sa.DateTime(), nullable=True))


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('repository', schema=None) as batch_op:
        batch_op.drop_column('updated')
        batch_op.drop_column('created')

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('updated')
        batch_op.drop_column('created')

    # ### end Alembic commands ###