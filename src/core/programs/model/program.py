from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean, Enum, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from core.forms.model.Form import Form
from core.user.model.User import User
from utilities.dbconfig import Base
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum as PythonEnum


class ProgramStatus(str, PythonEnum):
    """Enum for program status"""
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Association table for many-to-many relationship between Program and Form
program_forms_association = Table(
    'program_forms',
    Base.metadata,
    Column('program_id', String(20), ForeignKey('programs.id'), primary_key=True),
    Column('form_id', String(20), ForeignKey('forms.id'), primary_key=True),
    Column('added_at', DateTime(timezone=True), server_default=func.now())
)

# Association table for many-to-many relationship between Program and User (participants)
program_participants_association = Table(
    'program_participants',
    Base.metadata,
    Column('program_id', String(20), ForeignKey('programs.id'), primary_key=True),
    Column('user_id', String(20), ForeignKey('users.id'), primary_key=True),
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    Column('status', String, default='ACTIVE')  # ACTIVE, DROPPED, COMPLETED
)


class Program(Base):
    """Model for storing programs/activities/projects in the organization"""
    __tablename__ = "programs"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    
    # Program metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # "about" field
    
    # Program dates
    starting_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Program URLs
    register_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Optional: Image/thumbnail URL
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Program status
    status: Mapped[ProgramStatus] = mapped_column(String, nullable=False, default=ProgramStatus.UPCOMING)
    
    # Admin who created the program
    created_by: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)
    
    # Optional: Program capacity
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Optional: Category/tags for classification
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Program settings
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_registration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Metadata stored as JSON (for flexible additional data)
    program_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], back_populates="created_programs")
    
    # Many-to-many relationship with Form
    forms: Mapped[List["Form"]] = relationship(
        "Form",
        secondary=program_forms_association,
        lazy="selectin"
    )
    
    # Many-to-many relationship with User (participants)
    participants: Mapped[List["User"]] = relationship(
        "User",
        secondary=program_participants_association,
        back_populates="participating_programs",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<Program(id={self.id}, title={self.title}, status={self.status})>"


class ProgramEnrollment(Base):
    """Model for tracking detailed program enrollment information"""
    __tablename__ = "program_enrollments"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    
    # Enrollment references
    program_id: Mapped[str] = mapped_column(String(20), ForeignKey("programs.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)
    
    # Enrollment details
    status: Mapped[str] = mapped_column(String, nullable=False, default='ACTIVE')  # ACTIVE, DROPPED, COMPLETED, PENDING
    completion_percentage: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    # Dates
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    dropped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Optional: Notes or metadata about enrollment
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    program: Mapped[Program] = relationship("Program")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<ProgramEnrollment(id={self.id}, program_id={self.program_id}, user_id={self.user_id}, status={self.status})>"
