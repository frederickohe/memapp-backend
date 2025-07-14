from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum
from core.profile.model.Profile import ProfileType

class ProfileUpdateRequest(BaseModel):
    # Basic information
    name: Optional[str] = None
    description: Optional[str] = None
    profile_picture: Optional[str] = None
    category: Optional[ProfileType] = None
    
    # Student-specific fields
    program: Optional[str] = None
    field_studied: Optional[str] = None
    current_level: Optional[str] = None
    enrollment_date: Optional[datetime] = None
    graduation_date: Optional[datetime] = None
    is_active_student: Optional[bool] = None
    learning_goals: Optional[str] = None
    
    # Tutor-specific fields
    expertise: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_available: Optional[bool] = None
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None

    @validator('graduation_date')
    def validate_dates(cls, v, values):
        if 'enrollment_date' in values and v:
            if values['enrollment_date'] and v < values['enrollment_date']:
                raise ValueError("Graduation date must be after enrollment date")
        return v

    @validator('hourly_rate')
    def validate_hourly_rate(cls, v):
        if v is not None and v < 0:
            raise ValueError("Hourly rate cannot be negative")
        return v