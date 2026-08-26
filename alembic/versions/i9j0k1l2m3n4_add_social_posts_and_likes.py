"""Add social posts and likes tables.

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
"""
from alembic import op
import sqlalchemy as sa

revision = "i9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "social_posts" not in tables:
        op.create_table(
            "social_posts",
            sa.Column("id", sa.String(length=20), primary_key=True, nullable=False),
            sa.Column("user_id", sa.String(length=20), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("caption", sa.Text(), nullable=True),
            sa.Column("media_url", sa.String(length=500), nullable=False),
            sa.Column("media_type", sa.String(length=20), nullable=False, server_default="IMAGE"),
            sa.Column("kind", sa.String(length=20), nullable=False, server_default="IMPACT"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_social_posts_user_id", "social_posts", ["user_id"])
        op.create_index("ix_social_posts_created_at", "social_posts", ["created_at"])

    if "social_likes" not in tables:
        op.create_table(
            "social_likes",
            sa.Column("id", sa.String(length=20), primary_key=True, nullable=False),
            sa.Column("user_id", sa.String(length=20), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("target_type", sa.String(length=20), nullable=False),
            sa.Column("target_id", sa.String(length=40), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("user_id", "target_type", "target_id", name="uq_social_like_target"),
        )
        op.create_index("ix_social_likes_user_id", "social_likes", ["user_id"])
        op.create_index("ix_social_likes_target_id", "social_likes", ["target_id"])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "social_likes" in tables:
        op.drop_table("social_likes")
    if "social_posts" in tables:
        op.drop_table("social_posts")
