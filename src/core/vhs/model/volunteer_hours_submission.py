from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utilities.dbconfig import Base


class VhsStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VolunteerHoursSubmission(Base):
    __tablename__ = "volunteer_hours_submissions"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)

    hours: Mapped[float] = mapped_column(Float, nullable=False)
    activity_name: Mapped[str] = mapped_column(String(200), nullable=False)
    activity_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    volunteer_date: Mapped[date] = mapped_column(Date, nullable=False)
    proof_document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=VhsStatus.PENDING)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    points_awarded: Mapped[Optional[int]] = mapped_column(nullable=True)

    reviewed_by: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    member: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="volunteer_hours_submissions",
    )
    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[reviewed_by],
    )

    def __repr__(self) -> str:
        return f"<VolunteerHoursSubmission(id={self.id}, user_id={self.user_id}, status={self.status})>"
