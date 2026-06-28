from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utilities.dbconfig import Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        back_populates="region",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Region(id={self.id}, name={self.name})>"
