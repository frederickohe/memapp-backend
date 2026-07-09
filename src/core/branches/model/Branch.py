from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utilities.dbconfig import Base


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    region_id: Mapped[str] = mapped_column(String(20), ForeignKey("regions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    president_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    region: Mapped["Region"] = relationship("Region", back_populates="branches")
    president: Mapped[Optional["User"]] = relationship("User", foreign_keys=[president_id])
    members: Mapped[List["User"]] = relationship(
        "User",
        foreign_keys="User.branch_id",
        back_populates="branch",
    )

    def __repr__(self) -> str:
        return f"<Branch(id={self.id}, name={self.name})>"
