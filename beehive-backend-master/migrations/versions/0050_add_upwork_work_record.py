"""add upwork work record

Revision ID: 0050
Revises: 0049
Create Date: 2023-01-11 13:03:11.185383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0050'
down_revision = '0049'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('upwork_diary',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=8), nullable=True),
    sa.Column('upwork_user', sa.String(length=256), nullable=False),
    sa.Column('start_time_epoch_ms', sa.BigInteger(), nullable=False),
    sa.Column('end_time_epoch_ms', sa.BigInteger(), nullable=False),
    sa.Column('duration_min', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_upwork_diary_user_id'), 'upwork_diary', ['user_id'], unique=False)
    op.create_index(op.f('ix_upwork_diary_upwork_user'), 'upwork_diary', ['upwork_user'], unique=False)
    op.create_unique_constraint('_upwork_diary_uc', 'upwork_diary', ['upwork_user', 'start_time_epoch_ms', 'end_time_epoch_ms'])

    op.create_table('work_record_upwork_diary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('work_record_id', sa.Integer(), nullable=False),
    sa.Column('upwork_diary_id', sa.Integer(), nullable=False),
    sa.Column('net_duration_seconds', sa.Integer(), nullable=False),
    sa.Column('cost', sa.DECIMAL(precision=12, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['upwork_diary_id'], ['upwork_diary.id'], ),
    sa.ForeignKeyConstraint(['work_record_id'], ['work_record.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('work_record_id', 'upwork_diary_id', name='_work_record_upwork_diary_uc')
    )


def downgrade():
    op.drop_table('work_record_upwork_diary')
    op.drop_constraint('_upwork_diary_uc', 'upwork_diary', type_='unique')
    op.drop_index(op.f('ix_upwork_diary_upwork_user'), table_name='upwork_diary')
    op.drop_index(op.f('ix_upwork_diary_user_id'), table_name='upwork_diary')
    op.drop_table('upwork_diary')
