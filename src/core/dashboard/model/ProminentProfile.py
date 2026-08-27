from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from utilities.dbconfig import Base


class ProminentProfile(Base):
    """Featured YMCA figures shown on the member dashboard."""

    __tablename__ = "prominent_profiles"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    era: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="WORLD")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self):
        return f"<ProminentProfile(id={self.id}, name={self.full_name})>"
