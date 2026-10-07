"""Add two-factor authentication flag on users.

Revision ID: s9t0u1v2w3
Revises: r8s9t0u1v2
"""
import sqlalchemy as sa
from alembic import op

revision = "s9t0u1v2w3"
down_revision = "r8s9t0u1v2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "two_factor_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column("users", "two_factor_enabled")
