"""Add social views table.

Revision ID: l2m3n4o5p6
Revises: k1l2m3n4o5
"""
from alembic import op
import sqlalchemy as sa

revision = "l2m3n4o5p6"
down_revision = "k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "social_views" not in tables:
        op.create_table(
            "social_views",
            sa.Column("id", sa.String(length=20), primary_key=True, nullable=False),
            sa.Column("user_id", sa.String(length=20), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("target_type", sa.String(length=20), nullable=False),
            sa.Column("target_id", sa.String(length=40), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("user_id", "target_type", "target_id", name="uq_social_view_target"),
        )
        op.create_index("ix_social_views_user_id", "social_views", ["user_id"])
        op.create_index("ix_social_views_target_id", "social_views", ["target_id"])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "social_views" in tables:
        op.drop_table("social_views")
