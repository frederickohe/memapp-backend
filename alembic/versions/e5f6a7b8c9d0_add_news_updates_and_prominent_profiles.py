"""Add news content types, impact stories, and prominent profile fields."""
from alembic import op
import sqlalchemy as sa

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "news",
        sa.Column("content_type", sa.String(), nullable=False, server_default="NEWS"),
    )
    op.add_column(
        "news",
        sa.Column("is_impact_story", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "news",
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "news",
        sa.Column("event_location", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("is_prominent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "users",
        sa.Column("prominent_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("prominent_headline", sa.String(length=200), nullable=True),
    )


def downgrade():
    op.drop_column("users", "prominent_headline")
    op.drop_column("users", "prominent_order")
    op.drop_column("users", "is_prominent")
    op.drop_column("news", "event_location")
    op.drop_column("news", "event_date")
    op.drop_column("news", "is_impact_story")
    op.drop_column("news", "content_type")
