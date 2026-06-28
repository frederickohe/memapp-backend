"""Add volunteer hours submissions and member volunteer points."""
from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("volunteer_points", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )

    op.create_table(
        "volunteer_hours_submissions",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.String(length=20), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("activity_name", sa.String(length=200), nullable=False),
        sa.Column("activity_description", sa.Text(), nullable=True),
        sa.Column("branch", sa.String(length=100), nullable=True),
        sa.Column("volunteer_date", sa.Date(), nullable=False),
        sa.Column("proof_document_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("points_awarded", sa.Integer(), nullable=True),
        sa.Column("reviewed_by", sa.String(length=20), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )

    op.alter_column("users", "volunteer_points", server_default=None)


def downgrade():
    op.drop_table("volunteer_hours_submissions")
    op.drop_column("users", "volunteer_points")
