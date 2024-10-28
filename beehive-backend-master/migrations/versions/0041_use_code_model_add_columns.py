"""use code model add columns

Revision ID: 0041
Revises: 0040
Create Date: 2022-02-23 17:10:39.277094

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0041'
down_revision = '0040'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_code', sa.Column('code_type', sa.Enum('REGISTRATION', 'RESET_PASSWORD', name='usercodetype'), nullable=False))
    op.add_column('user_code', sa.Column('user_id', sa.String(length=8), nullable=True))
    op.create_foreign_key(
        constraint_name='user_code_ibfk_1',
        source_table='user_code',
        referent_table='user',
        local_cols=['user_id'],
        remote_cols=['id']
    )

    # make all current codes of type 'REGISTRATION' because that's what they actually are
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE user_code SET code_type = \'REGISTRATION\';'))
    session.commit()


def downgrade():
    op.drop_constraint(
        constraint_name='user_code_ibfk_1',
        table_name='user_code',
        type_='foreignkey'
    )
    op.drop_column('user_code', 'user_id')
    op.drop_column('user_code', 'code_type')
