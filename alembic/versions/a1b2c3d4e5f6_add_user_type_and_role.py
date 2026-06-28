"""Add user_type and role columns to users table."""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "38e1bbf57622"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("user_type", sa.String(), nullable=False, server_default="MEMBER"),
    )
    op.add_column(
        "users",
        sa.Column("role", sa.String(), nullable=True),
    )
    op.alter_column("users", "user_type", server_default=None)


def downgrade():
    op.drop_column("users", "role")
    op.drop_column("users", "user_type")
