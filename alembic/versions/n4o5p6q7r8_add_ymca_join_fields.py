"""Add YMCA join date and past positions on users.

Revision ID: n4o5p6q7r8
Revises: m3n4o5p6q7
"""
from alembic import op
import sqlalchemy as sa


revision = "n4o5p6q7r8"
down_revision = "m3n4o5p6q7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("date_joined_organization", sa.Date(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("past_positions", sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_column("users", "past_positions")
    op.drop_column("users", "date_joined_organization")
