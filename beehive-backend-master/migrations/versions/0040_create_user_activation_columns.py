"""create user activation columns

Revision ID: 0040
Revises: 0039
Create Date: 2022-02-13 14:22:49.750507

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '0040'
down_revision = '0039'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('activated', sa.Boolean(), nullable=False))
    op.add_column('user', sa.Column('activation_token', sa.String(length=32), nullable=False))
    op.create_index(op.f('ix_user_activation_token'), 'user', ['activation_token'], unique=False)

    # make all current users activated. uuid4 mysql "function" taken from:
    # https://stackoverflow.com/a/61110222/4925989
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text('UPDATE user SET activated = true, activation_token = concat(substr(sha2(rand(), 256), 1, 12), \'4\', substr(sha2(rand(), 256), 1,  3), \'8\', substr(sha2(concat(rand(), rand()), 256), 1, 15));'))
    session.commit()


def downgrade():
    op.drop_index(op.f('ix_user_activation_token'), table_name='user')
    op.drop_column('user', 'activation_token')
    op.drop_column('user', 'activated')
