"""Allow duplicate member full names.

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
"""
from alembic import op
import sqlalchemy as sa

revision = "g7h8i9j0k1l2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for constraint in inspector.get_unique_constraints("users"):
        if constraint.get("column_names") == ["fullname"]:
            op.drop_constraint(constraint["name"], "users", type_="unique")


def downgrade():
    op.create_unique_constraint("users_fullname_key", "users", ["fullname"])
