"""Add Forms and FormResponses tables migration."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'forms_migration_001'
down_revision = 'eee5e3f84072'
branch_labels = None
depends_on = None


def upgrade():
    # Create forms table
    op.create_table('forms',
        sa.Column('id', sa.String(20), nullable=False, unique=True),
        sa.Column('admin_id', sa.String(20), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assignment_type', sa.String(), nullable=False),
        sa.Column('program_id', sa.String(20), nullable=True),
        sa.Column('assigned_user_id', sa.String(20), nullable=True),
        sa.Column('fields', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'])
    )
    op.create_index(op.f('ix_forms_id'), 'forms', ['id'], unique=False)
    op.create_index(op.f('ix_forms_admin_id'), 'forms', ['admin_id'], unique=False)
    op.create_index(op.f('ix_forms_assignment_type'), 'forms', ['assignment_type'], unique=False)
    op.create_index(op.f('ix_forms_is_active'), 'forms', ['is_active'], unique=False)

    # Create form_responses table
    op.create_table('form_responses',
        sa.Column('id', sa.String(20), nullable=False, unique=True),
        sa.Column('form_id', sa.String(20), nullable=False),
        sa.Column('user_id', sa.String(20), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_submitted', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index(op.f('ix_form_responses_id'), 'form_responses', ['id'], unique=False)
    op.create_index(op.f('ix_form_responses_form_id'), 'form_responses', ['form_id'], unique=False)
    op.create_index(op.f('ix_form_responses_user_id'), 'form_responses', ['user_id'], unique=False)


def downgrade():
    # Drop form_responses table
    op.drop_index(op.f('ix_form_responses_user_id'), table_name='form_responses')
    op.drop_index(op.f('ix_form_responses_form_id'), table_name='form_responses')
    op.drop_index(op.f('ix_form_responses_id'), table_name='form_responses')
    op.drop_table('form_responses')

    # Drop forms table
    op.drop_index(op.f('ix_forms_is_active'), table_name='forms')
    op.drop_index(op.f('ix_forms_assignment_type'), table_name='forms')
    op.drop_index(op.f('ix_forms_admin_id'), table_name='forms')
    op.drop_index(op.f('ix_forms_id'), table_name='forms')
    op.drop_table('forms')
