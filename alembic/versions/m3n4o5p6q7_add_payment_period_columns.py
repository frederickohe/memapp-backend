"""Add billing period columns on payments.

Revision ID: m3n4o5p6q7
Revises: l2m3n4o5p6
"""
from alembic import op
import sqlalchemy as sa

revision = "m3n4o5p6q7"
down_revision = "l2m3n4o5p6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("payments", sa.Column("period_year", sa.Integer(), nullable=True))
    op.add_column("payments", sa.Column("period_month", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE payments
        SET
            period_year = COALESCE(
                NULLIF(payment_metadata->>'period_year', '')::int,
                EXTRACT(YEAR FROM created_at)::int
            ),
            period_month = COALESCE(
                NULLIF(payment_metadata->>'period_month', '')::int,
                EXTRACT(MONTH FROM created_at)::int
            )
        """
    )

    op.alter_column("payments", "period_year", nullable=False)
    op.alter_column("payments", "period_month", nullable=False)

    op.create_index("ix_payments_period_year", "payments", ["period_year"])
    op.create_index("ix_payments_period_month", "payments", ["period_month"])
    op.create_index(
        "ix_payments_user_period",
        "payments",
        ["user_id", "period_year", "period_month"],
    )


def downgrade():
    op.drop_index("ix_payments_user_period", table_name="payments")
    op.drop_index("ix_payments_period_month", table_name="payments")
    op.drop_index("ix_payments_period_year", table_name="payments")
    op.drop_column("payments", "period_month")
    op.drop_column("payments", "period_year")
