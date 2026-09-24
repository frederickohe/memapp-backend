"""Add collects_dues flag on branches.

Revision ID: o5p6q7r8s9
Revises: n4o5p6q7r8
"""
from alembic import op
import sqlalchemy as sa


revision = "o5p6q7r8s9"
down_revision = "n4o5p6q7r8"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "branches",
        sa.Column(
            "collects_dues",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade():
    op.drop_column("branches", "collects_dues")
