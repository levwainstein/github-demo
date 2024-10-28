"""class object

Revision ID: 0007
Revises: 0006
Create Date: 2020-09-15 00:15:05.784955

"""
from alembic import op
import sqlalchemy as sa


revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('class_obj',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('delegating_user_id', sa.String(length=8), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('params', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['delegating_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_class_obj_delegating_user_id'), 'class_obj', ['delegating_user_id'], unique=False)
    op.create_index(op.f('ix_class_obj_name'), 'class_obj', ['name'], unique=False)
    op.add_column('task', sa.Column('class_id', sa.String(length=8), nullable=True))
    op.create_foreign_key(None, 'task', 'class_obj', ['class_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_column('task', 'class_id')
    op.drop_index(op.f('ix_class_obj_name'), table_name='class_obj')
    op.drop_index(op.f('ix_class_obj_delegating_user_id'), table_name='class_obj')
    op.drop_table('class_obj')
