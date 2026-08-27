"""Widen profile picture URL column.

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
"""
from alembic import op
import sqlalchemy as sa

revision = "j0k1l2m3n4o5"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "users",
        "profile_picture_url",
        existing_type=sa.String(length=200),
        type_=sa.String(length=500),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "users",
        "profile_picture_url",
        existing_type=sa.String(length=500),
        type_=sa.String(length=200),
        existing_nullable=True,
    )
