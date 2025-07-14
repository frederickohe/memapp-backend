from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from utilities.dbconfig import Base
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum

# Business Category Enum
class BusinessCategory(str, Enum):
    TECHNOLOGY = "TECHNOLOGY"
    HEALTHCARE = "HEALTHCARE"
    FINANCE = "FINANCE"
    EDUCATION = "EDUCATION"
    RETAIL = "RETAIL"
    MANUFACTURING = "MANUFACTURING"
    CONSULTING = "CONSULTING"
    OTHER = "OTHER"

class Business(Base):
    __tablename__ = "businesses"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    category: Mapped[BusinessCategory] = mapped_column(String, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(String(200))
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    tax_id: Mapped[Optional[str]] = mapped_column(String(50))
    registration_number: Mapped[Optional[str]] = mapped_column(String(50))
    established_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="business")
    
    def __repr__(self):
        return f"<Business(id={self.id}, name={self.name}, category={self.category})>"