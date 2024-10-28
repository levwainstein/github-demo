"""package support

Revision ID: 0003
Revises: 0002
Create Date: 2020-08-21 19:03:24.796422

"""
from alembic import op
import sqlalchemy as sa
# from ...src.models.package import Package

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    package_table = op.create_table('package',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_package_name'), 'package', ['name'], unique=False)

    op.bulk_insert(package_table,
    [
        { 'name': 'urllib3' },
        { 'name': 'six' },
        { 'name': 'botocore' },
        { 'name': 'requests' },
        { 'name': 'python-dateutil' },
        { 'name': 'certifi' },
        { 'name': 's3transfer' },
        { 'name': 'idna' },
        { 'name': 'docutils' },
        { 'name': 'chardet' },
        { 'name': 'setuptools' },
        { 'name': 'pyyaml' },
        { 'name': 'jmespath' },
        { 'name': 'pyasn1' },
        { 'name': 'rsa' },
        { 'name': 'pytz' },
        { 'name': 'boto3' },
        { 'name': 'numpy' },
        { 'name': 'awscii' },
        { 'name': 'colorama' },
        { 'name': 'wheel' },
        { 'name': 'markupsafe' },
        { 'name': 'protobuf' },
        { 'name': 'jinja2' },
        { 'name': 'simplejson' },
        { 'name': 'cffi' },
        { 'name': 'cryptography' },
        { 'name': 'attrs' },
        { 'name': 'click' },
        { 'name': 'importlib-matadata' },
        { 'name': 'pyasn1-modules' },
        { 'name': 'semanticscholar' },
        { 'name': 'zipp' },
        { 'name': 'pandas' },
        { 'name': 'pyparsing' },
        { 'name': 'cachetools' },
        { 'name': 'pycparser' },
        { 'name': 'oauthlib' },
        { 'name': 'google-auth' },
        { 'name': 'requests-oauthlib' },
        { 'name': 'werkzeug' },
        { 'name': 'decorator' },
        { 'name': 'scipy' },
        { 'name': 'packaging' },
        { 'name': 'google-api-core' },
        { 'name': 'wcwidth' },
        { 'name': 'more-itertools' },
        { 'name': 'grpcio' },
        { 'name': 'googleapis-common-protos' },
        { 'name': 'pytest' },
        { 'name': 'jsonschema' },
        { 'name': 'enum34' },
        { 'name': 'google-cloud-core' },
        { 'name': 'py' },
        { 'name': 'pluggy' },
        { 'name': 'pygments' },
        { 'name': 'psutil' },
        { 'name': 'flask' },
        { 'name': 'pyjwt' },
        { 'name': 'coverage' },
        { 'name': 'scikit-learn' },
        { 'name': 'itsdangerous' },
        { 'name': 'pillow' },
        { 'name': 'google-cloud-storage' },
        { 'name': 'virtualenv' },
        { 'name': 'ipaddress' },
        { 'name': 'websocket-client' },
        { 'name': 'matplotlib' },
        { 'name': 'google-api-python-client' },
        { 'name': 'boto' },
        { 'name': 'beautifulsoup4' },
        { 'name': 'argparse' },
        { 'name': 'seaborn' },
        { 'name': 'lxml' },
    ]
)

def downgrade():
    op.drop_index(op.f('ix_package_name'), table_name='package')
    op.drop_table('package')
