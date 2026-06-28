"""Add payments and paystack_sessions tables."""
from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "payments",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.String(length=20), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=False),
        sa.Column("payment_type", sa.String(length=30), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("method", sa.String(length=30), nullable=True),
        sa.Column("amount_ghs", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="GHS"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("gateway_response", sa.String(length=500), nullable=True),
        sa.Column("payment_metadata", sa.JSON(), nullable=True),
        sa.Column("receipt_number", sa.String(length=30), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("reference"),
        sa.UniqueConstraint("receipt_number"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_reference", "payments", ["reference"])
    op.create_index("ix_payments_payment_type", "payments", ["payment_type"])
    op.create_index("ix_payments_status", "payments", ["status"])

    op.create_table(
        "paystack_sessions",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.String(length=20), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=False),
        sa.Column("access_code", sa.String(length=100), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("gateway_response", sa.String(length=200), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("transaction_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    op.create_index("ix_paystack_sessions_user_id", "paystack_sessions", ["user_id"])
    op.create_index("ix_paystack_sessions_reference", "paystack_sessions", ["reference"])


def downgrade():
    op.drop_index("ix_paystack_sessions_reference", table_name="paystack_sessions")
    op.drop_index("ix_paystack_sessions_user_id", table_name="paystack_sessions")
    op.drop_table("paystack_sessions")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_payment_type", table_name="payments")
    op.drop_index("ix_payments_reference", table_name="payments")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_table("payments")
