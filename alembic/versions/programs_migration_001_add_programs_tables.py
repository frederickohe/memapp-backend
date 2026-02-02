"""Add Programs and enrollments tables migration."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'programs_migration_001'
down_revision = 'forms_migration_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create program_participants association table
    op.create_table('program_participants',
        sa.Column('program_id', sa.String(20), nullable=False),
        sa.Column('user_id', sa.String(20), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(), default='ACTIVE'),
        sa.PrimaryKeyConstraint('program_id', 'user_id'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index(op.f('ix_program_participants_program_id'), 'program_participants', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_participants_user_id'), 'program_participants', ['user_id'], unique=False)

    # Create program_forms association table
    op.create_table('program_forms',
        sa.Column('program_id', sa.String(20), nullable=False),
        sa.Column('form_id', sa.String(20), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('program_id', 'form_id'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'])
    )
    op.create_index(op.f('ix_program_forms_program_id'), 'program_forms', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_forms_form_id'), 'program_forms', ['form_id'], unique=False)

    # Create programs table
    op.create_table('programs',
        sa.Column('id', sa.String(20), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('starting_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('register_url', sa.String(500), nullable=True),
        sa.Column('youtube_url', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='UPCOMING'),
        sa.Column('created_by', sa.String(20), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, default=False),
        sa.Column('allow_registration', sa.Boolean(), nullable=False, default=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )
    op.create_index(op.f('ix_programs_id'), 'programs', ['id'], unique=False)
    op.create_index(op.f('ix_programs_created_by'), 'programs', ['created_by'], unique=False)
    op.create_index(op.f('ix_programs_status'), 'programs', ['status'], unique=False)
    op.create_index(op.f('ix_programs_is_published'), 'programs', ['is_published'], unique=False)
    op.create_index(op.f('ix_programs_category'), 'programs', ['category'], unique=False)

    # Create program_enrollments table
    op.create_table('program_enrollments',
        sa.Column('id', sa.String(20), nullable=False, unique=True),
        sa.Column('program_id', sa.String(20), nullable=False),
        sa.Column('user_id', sa.String(20), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='ACTIVE'),
        sa.Column('completion_percentage', sa.Integer(), default=0),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dropped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index(op.f('ix_program_enrollments_id'), 'program_enrollments', ['id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_program_id'), 'program_enrollments', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_user_id'), 'program_enrollments', ['user_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_status'), 'program_enrollments', ['status'], unique=False)


def downgrade():
    # Drop program_enrollments table
    op.drop_index(op.f('ix_program_enrollments_status'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_user_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_program_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_id'), table_name='program_enrollments')
    op.drop_table('program_enrollments')

    # Drop programs table
    op.drop_index(op.f('ix_programs_category'), table_name='programs')
    op.drop_index(op.f('ix_programs_is_published'), table_name='programs')
    op.drop_index(op.f('ix_programs_status'), table_name='programs')
    op.drop_index(op.f('ix_programs_created_by'), table_name='programs')
    op.drop_index(op.f('ix_programs_id'), table_name='programs')
    op.drop_table('programs')

    # Drop program_forms table
    op.drop_index(op.f('ix_program_forms_form_id'), table_name='program_forms')
    op.drop_index(op.f('ix_program_forms_program_id'), table_name='program_forms')
    op.drop_table('program_forms')

    # Drop program_participants table
    op.drop_index(op.f('ix_program_participants_user_id'), table_name='program_participants')
    op.drop_index(op.f('ix_program_participants_program_id'), table_name='program_participants')
    op.drop_table('program_participants')
