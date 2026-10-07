"""Add system settings and seed the sign-up YouTube video.

Revision ID: r8s9t0u1v2
Revises: q7r8s9t0u1
"""
import sqlalchemy as sa
from alembic import op

revision = "r8s9t0u1v2"
down_revision = "q7r8s9t0u1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(length=100), primary_key=True, nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.execute(
        sa.text(
            """
            INSERT INTO system_settings (key, value, description)
            VALUES (
                'signup_youtube_url',
                'https://www.youtube.com/watch?v=6YM8SreJVLQ',
                'YouTube video shown on the member app sign-up screens'
            )
            """
        )
    )


def downgrade():
    op.drop_table("system_settings")
