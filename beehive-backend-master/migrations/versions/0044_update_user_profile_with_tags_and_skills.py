"""add skills and tags

Revision ID: 0044
Revises: 0043
Create Date: 2022-04-05 17:02:24.028777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0044'
down_revision = '0043'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('skill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_name'), 'skill', ['name'], unique=False)
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_name'), 'tag', ['name'], unique=False)
    op.create_table('user_skill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=8), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'skill_id', name='_user_skill_uc')
    )
    op.create_table('user_tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=8), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'tag_id', name='_user_tag_uc')
    )


def downgrade():
    op.drop_table('user_tag')
    op.drop_table('user_skill')
    op.drop_index(op.f('ix_tag_name'), table_name='tag')
    op.drop_table('tag')
    op.drop_index(op.f('ix_skill_name'), table_name='skill')
    op.drop_table('skill')
