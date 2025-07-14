from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from utilities.dbconfig import Base
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum

# Profile Category Enum (kept as is)
class ProfileType(str, Enum):
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
    STUDENT = "STUDENT"
    TUTOR = "TUTOR"
    OTHER = "OTHER"

class Profile(Base):
    __tablename__ = "profiles"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # LMS-specific fields
    profile_picture: Mapped[Optional[str]] = mapped_column(String)  # URL to profile image
    category: Mapped[ProfileType] = mapped_column(String, nullable=False, default=ProfileType.STUDENT)
    
    # Student-specific fields
    program: Mapped[Optional[str]] = mapped_column(String(1000))  # For tutor/student introductions
    field_studied: Mapped[Optional[str]] = mapped_column(String(100))  # Field of study
    current_level: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "Beginner", "Intermediate"
    enrollment_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    graduation_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active_student: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    learning_goals: Mapped[Optional[str]] = mapped_column(String(500))  # Student's learning objectives
    
    # Tutor-specific fields
    expertise: Mapped[Optional[str]] = mapped_column(String(200))  # For tutors
    hourly_rate: Mapped[Optional[float]] = mapped_column(Integer)  # For tutors
    is_available: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)  # For tutors
    
    # Common contact information
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Location information
    address: Mapped[Optional[str]] = mapped_column(String(200))
    city: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    # Relationship to courses (if needed)
    # enrolled_courses = relationship("Enrollment", back_populates="student")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, name={self.name}, category={self.category})>"