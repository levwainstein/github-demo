"""manual diary log

Revision ID: 0071
Revises: 0070
Create Date: 2024-03-20 15:33:08.691169

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0071'
down_revision = '0070'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('external_user_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('role', sa.Enum('CORE_TEAM', 'TECH_LEAD', 'QA_CONTRIBUTOR', 'CONTRIBUTOR', name='userrole'), nullable=False),
    sa.Column('price_per_hour', sa.DECIMAL(precision=5, scale=2), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('external_user_role', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_external_user_role_email'), ['email'], unique=False)
        batch_op.create_index(batch_op.f('ix_external_user_role_role'), ['role'], unique=False)

    op.create_table('diary_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('external_user_id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(length=256), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('duration_hours', sa.DECIMAL(precision=5, scale=2), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['external_user_id'], ['external_user_role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('diary_log', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_diary_log_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_diary_log_external_user_id'), ['external_user_id'], unique=False)



def downgrade():

    with op.batch_alter_table('diary_log', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_diary_log_date'))
        batch_op.drop_index(batch_op.f('ix_diary_log_external_user_id'))

    op.drop_table('diary_log')
    with op.batch_alter_table('external_user_role', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_external_user_role_role'))
        batch_op.drop_index(batch_op.f('ix_external_user_role_email'))

    op.drop_table('external_user_role')
