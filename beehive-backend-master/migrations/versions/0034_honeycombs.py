"""honeycombs

Revision ID: 0034
Revises: 0033
Create Date: 2021-08-31 12:49:35.330099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0034'
down_revision = '0033'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('honeycomb',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('code', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('honeycomb_dependency',
    sa.Column('honeycomb_id', sa.Integer(), nullable=False),
    sa.Column('honeycomb_dependency_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['honeycomb_dependency_id'], ['honeycomb.id'], ),
    sa.ForeignKeyConstraint(['honeycomb_id'], ['honeycomb.id'], ),
    sa.PrimaryKeyConstraint('honeycomb_id', 'honeycomb_dependency_id')
    )
    op.create_table('honeycomb_package_dependency',
    sa.Column('honeycomb_id', sa.Integer(), nullable=False),
    sa.Column('package_dependency_id', sa.Integer(), nullable=False),
    sa.Column('package_version', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['honeycomb_id'], ['honeycomb.id'], ),
    sa.ForeignKeyConstraint(['package_dependency_id'], ['package.id'], ),
    sa.PrimaryKeyConstraint('honeycomb_id', 'package_dependency_id', 'package_version')
    )


def downgrade():
    op.drop_table('honeycomb_package_dependency')
    op.drop_table('honeycomb_dependency')
    op.drop_table('honeycomb')
