"""remove internal tasks

Revision ID: 0061
Revises: 0060
Create Date: 2023-12-21 18:12:18.707934

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0061'
down_revision = '0060'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fk_user_team_id', 'user', type_='foreignkey')
    op.drop_constraint('fk_task_delegating_team_id', 'task', type_='foreignkey')
    op.drop_constraint('task_ibfk_2', 'task', type_='foreignkey')  # class_obj -> class_id

    op.drop_table('test_case')
    op.drop_table('code_block')
    op.drop_table('secret')
    op.drop_table('team')
    op.drop_table('honeycomb_package_dependency')
    op.drop_table('class_obj')
    op.drop_table('package')

    op.drop_index('ix_task_delegating_team_id', table_name='task')
    op.drop_column('task', 'invalid_code')
    op.drop_column('task', 'absolute_target_file')
    op.drop_column('task', 'solution_code')
    op.drop_column('task', 'available_names')
    op.drop_column('task', 'delegating_team_id')
    op.drop_column('task', 'class_id')
    op.drop_column('task', 'invalid_description')
    op.drop_column('task', 'class_init_params')
    op.drop_column('task', 'secret_key')
    op.drop_column('task', 'func_input')
    op.drop_column('task', 'original_code')
    op.drop_column('task', 'solution_packages')
    op.drop_column('task', 'context')
    op.drop_column('task', 'target_file')
    op.drop_column('task', 'class_name')

    op.drop_index('name', table_name='task_template')

    op.drop_column('user', 'team_id')

    op.drop_column('work_record', 'solution_code')
    op.drop_column('work_record', 'installed_packages')
    op.drop_column('work_record', 'requested_package')


def downgrade():
    op.add_column('work_record', sa.Column('requested_package', mysql.VARCHAR(collation='utf8mb3_bin', length=256), nullable=True))
    op.add_column('work_record', sa.Column('installed_packages', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True))
    op.add_column('work_record', sa.Column('solution_code', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))

    op.add_column('user', sa.Column('team_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=True))

    op.create_index('name', 'task_template', ['name'], unique=True)

    op.add_column('task', sa.Column('class_name', mysql.VARCHAR(collation='utf8mb3_bin', length=256), nullable=True))
    op.add_column('task', sa.Column('target_file', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('context', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('solution_packages', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True))
    op.add_column('task', sa.Column('original_code', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('func_input', mysql.VARCHAR(collation='utf8mb3_bin', length=512), nullable=True))
    op.add_column('task', sa.Column('secret_key', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('class_init_params', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True))
    op.add_column('task', sa.Column('invalid_description', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('class_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=True))
    op.add_column('task', sa.Column('delegating_team_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=True))
    op.add_column('task', sa.Column('available_names', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True))
    op.add_column('task', sa.Column('solution_code', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('absolute_target_file', mysql.TEXT(collation='utf8mb3_bin'), nullable=True))
    op.add_column('task', sa.Column('invalid_code', mysql.VARCHAR(collation='utf8mb3_bin', length=64), nullable=True))
    op.create_index('ix_task_delegating_team_id', 'task', ['delegating_team_id'], unique=False)

    op.create_table('package',
        sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
        sa.Column('name', mysql.VARCHAR(collation='utf8mb3_bin', length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_package_name', 'package', ['name'], unique=False)
    op.create_table('class_obj',
        sa.Column('created', mysql.DATETIME(), nullable=False),
        sa.Column('updated', mysql.DATETIME(), nullable=True),
        sa.Column('id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.Column('delegating_user_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.Column('name', mysql.VARCHAR(collation='utf8mb3_bin', length=64), nullable=False),
        sa.Column('params', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True),
        sa.ForeignKeyConstraint(['delegating_user_id'], ['user.id'], name='class_obj_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_class_obj_name', 'class_obj', ['name'], unique=False)
    op.create_index('ix_class_obj_delegating_user_id', 'class_obj', ['delegating_user_id'], unique=False)
    op.create_table('honeycomb_package_dependency',
        sa.Column('honeycomb_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
        sa.Column('package_dependency_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
        sa.Column('package_version', mysql.VARCHAR(collation='utf8mb3_bin', length=64), nullable=False),
        sa.ForeignKeyConstraint(['honeycomb_id'], ['honeycomb.id'], name='honeycomb_package_dependency_ibfk_1'),
        sa.ForeignKeyConstraint(['package_dependency_id'], ['package.id'], name='honeycomb_package_dependency_ibfk_2'),
        sa.PrimaryKeyConstraint('honeycomb_id', 'package_dependency_id', 'package_version'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_table('team',
        sa.Column('created', mysql.DATETIME(), nullable=False),
        sa.Column('updated', mysql.DATETIME(), nullable=True),
        sa.Column('id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.Column('name', mysql.VARCHAR(collation='utf8mb3_bin', length=256), nullable=False),
        sa.Column('admin_user_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['user.id'], name='team_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_table('secret',
        sa.Column('created', mysql.DATETIME(), nullable=False),
        sa.Column('updated', mysql.DATETIME(), nullable=True),
        sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
        sa.Column('task_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.Column('name', mysql.VARCHAR(collation='utf8mb3_bin', length=128), nullable=False),
        sa.Column('encrypted_value', mysql.TEXT(collation='utf8mb3_bin'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], name='secret_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_secret_task_id', 'secret', ['task_id'], unique=False)
    op.create_table('code_block',
        sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
        sa.Column('task_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.Column('block_file', mysql.TEXT(collation='utf8mb3_bin'), nullable=False),
        sa.Column('start_index', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
        sa.Column('end_index', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], name='code_block_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_code_block_task_id', 'code_block', ['task_id'], unique=False)
    op.create_table('test_case',
        sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
        sa.Column('created', mysql.DATETIME(), nullable=False),
        sa.Column('updated', mysql.DATETIME(), nullable=True),
        sa.Column('task_id', mysql.VARCHAR(collation='utf8mb3_bin', length=8), nullable=False),
        sa.Column('case_input', mysql.LONGTEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=False),
        sa.Column('case_output', mysql.TEXT(collation='utf8mb3_bin'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], name='test_case_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb3_bin',
        mysql_default_charset='utf8mb3',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_test_case_task_id', 'test_case', ['task_id'], unique=False)

    op.create_foreign_key('fk_user_team_id', 'user', 'team', ['team_id'], ['id'])
    op.create_foreign_key('fk_task_delegating_team_id', 'task', 'team', ['delegating_team_id'], ['id'])
    op.create_foreign_key('task_ibfk_2', 'task', 'class_obj', ['class_id'], ['id'])
