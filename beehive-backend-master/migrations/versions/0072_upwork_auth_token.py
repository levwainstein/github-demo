"""upwork auth token

Revision ID: 0072
Revises: 0071
Create Date: 2024-04-10 15:13:45.283797

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0072'
down_revision = '0071'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('upwork_auth_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(length=64), nullable=False),
    sa.Column('refresh_token', sa.String(length=64), nullable=False),
    sa.Column('token_type', sa.String(length=64), nullable=False),
    sa.Column('expires_in', sa.BigInteger(), nullable=False),
    sa.Column('expires_at', sa.Float(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('upwork_auth_token', schema=None) as batch_op:
        batch_op.create_unique_constraint('_upwork_auth_token_uc', ['access_token', 'refresh_token', 'token_type'])

def downgrade():
    with op.batch_alter_table('upwork_auth_token', schema=None) as batch_op:
        batch_op.drop_constraint('_upwork_auth_token_uc', type_='unique')

    op.drop_table('upwork_auth_token')
