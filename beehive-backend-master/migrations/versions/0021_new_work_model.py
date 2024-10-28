"""new work model

Revision ID: 0021
Revises: 0020
Create Date: 2021-02-17 17:01:04.218517

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '0021'
down_revision = '0020'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('work',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(length=8), nullable=False),
    sa.Column('status', sa.Enum('AVAILABLE', 'UNAVAILABLE', 'COMPLETE', 'PENDING_PACKAGE', name='workstatus'), nullable=False),
    sa.Column('work_type', sa.Enum('CREATE_FUNCTION', 'UPDATE_FUNCTION', 'DESCRIBE_FUNCTION', 'REVIEW_TASK', name='worktype'), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('work_input', sa.JSON(), nullable=False),
    sa.Column('chain', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_task_id'), 'work', ['task_id'], unique=False)

    # migrate old data into new table
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('INSERT INTO work (task_id, status, work_type, description, work_input, created, updated) SELECT id, CASE WHEN status = \'PENDING\' THEN \'AVAILABLE\' WHEN status = \'PENDING_PACKAGE\' THEN \'PENDING_PACKAGE\' ELSE \'UNAVAILABLE\' END, task_type, description, JSON_OBJECT(\'code\', original_code, \'context\', IF(context IS NULL, JSON_OBJECT(), JSON_EXTRACT(context, \'$\'))), created, updated FROM task WHERE status != \'NEW\' AND (status != \'INVALID\' OR feedback IS NOT NULL);'))
    session.commit()


def downgrade():
    op.drop_constraint(constraint_name='work_ibfk_1', table_name='work', type_='foreignkey')
    op.drop_index(op.f('ix_work_task_id'), table_name='work')
    op.drop_table('work')
