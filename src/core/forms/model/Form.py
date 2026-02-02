from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from utilities.dbconfig import Base
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum as PythonEnum


class FormAssignmentType(str, PythonEnum):
    """Enum for form assignment types"""
    PUBLIC = "PUBLIC"
    PROGRAM = "PROGRAM"
    USER = "USER"


class Form(Base):
    """Model for storing forms created by admins"""
    __tablename__ = "forms"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    
    # Admin who created the form
    admin_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)
    
    # Form metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Form assignment type: PUBLIC, PROGRAM, or USER
    assignment_type: Mapped[FormAssignmentType] = mapped_column(String, nullable=False, default=FormAssignmentType.PUBLIC)
    
    # Optional: ID of the program this form is assigned to (if assignment_type is PROGRAM)
    program_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Optional: ID of the user this form is assigned to (if assignment_type is USER)
    assigned_user_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("users.id"), nullable=True)
    
    # Form configuration - stores the form fields as JSON
    # Example: [{"name": "email", "label": "Email", "type": "email", "required": true}, ...]
    fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default={})
    
    # Form status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    admin: Mapped["User"] = relationship("User", foreign_keys=[admin_id], back_populates="created_forms")
    assigned_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_user_id], back_populates="assigned_forms")
    responses: Mapped[List["FormResponse"]] = relationship("FormResponse", back_populates="form", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Form(id={self.id}, title={self.title}, admin_id={self.admin_id}, assignment_type={self.assignment_type})>"


class FormResponse(Base):
    """Model for storing form submissions/responses"""
    __tablename__ = "form_responses"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    
    # The form this response belongs to
    form_id: Mapped[str] = mapped_column(String(20), ForeignKey("forms.id"), nullable=False)
    
    # User who submitted the response
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)
    
    # The actual response data - stores key-value pairs of field names and their values
    # Example: {"email": "user@example.com", "name": "John Doe", ...}
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default={})
    
    # Optional: Notes or comments about this submission
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status flags
    is_submitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form: Mapped[Form] = relationship("Form", back_populates="responses")
    user: Mapped["User"] = relationship("User", back_populates="form_responses")
    
    def __repr__(self):
        return f"<FormResponse(id={self.id}, form_id={self.form_id}, user_id={self.user_id})>"
