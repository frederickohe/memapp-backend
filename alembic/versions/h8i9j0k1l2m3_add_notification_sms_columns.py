"""Add SMS and updated_at columns to notifications.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
"""
from alembic import op
import sqlalchemy as sa

revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None

COLUMNS = (
    ("sms_sent", sa.Column("sms_sent", sa.Boolean(), nullable=False, server_default=sa.text("false"))),
    ("sms_phone", sa.Column("sms_phone", sa.String(), nullable=True)),
    ("sms_message_id", sa.Column("sms_message_id", sa.String(), nullable=True)),
    ("sms_status", sa.Column("sms_status", sa.String(), nullable=True)),
    ("sms_delivery_status", sa.Column("sms_delivery_status", sa.String(), nullable=True)),
    ("sms_sent_at", sa.Column("sms_sent_at", sa.DateTime(timezone=True), nullable=True)),
    ("sms_delivered_at", sa.Column("sms_delivered_at", sa.DateTime(timezone=True), nullable=True)),
    ("updated_at", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)),
)


def upgrade():
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("notifications")}
    for name, column in COLUMNS:
        if name not in existing:
            op.add_column("notifications", column)


def downgrade():
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("notifications")}
    for name, _ in reversed(COLUMNS):
        if name in existing:
            op.drop_column("notifications", name)
