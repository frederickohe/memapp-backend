"""Add prominent_profiles table for featured YMCA figures.

Revision ID: k1l2m3n4o5
Revises: j0k1l2m3n4o5
"""
from alembic import op
import sqlalchemy as sa

revision = "k1l2m3n4o5"
down_revision = "j0k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "prominent_profiles",
        sa.Column("id", sa.String(length=20), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("headline", sa.String(length=200), nullable=True),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("occupation", sa.String(length=200), nullable=True),
        sa.Column("era", sa.String(length=80), nullable=True),
        sa.Column("category", sa.String(length=20), nullable=False, server_default="WORLD"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_prominent_profiles_sort", "prominent_profiles", ["is_published", "sort_order"])


def downgrade():
    op.drop_index("ix_prominent_profiles_sort", table_name="prominent_profiles")
    op.drop_table("prominent_profiles")
