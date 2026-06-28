from sqlalchemy import Column, ForeignKey, String, Table

from utilities.dbconfig import Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        String(20),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        String(20),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
