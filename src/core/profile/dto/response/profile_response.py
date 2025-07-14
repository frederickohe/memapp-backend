from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.profile.model.Profile import ProfileType

class ProfileResponse(BaseModel):
    # Basic information
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    profile_picture: Optional[str] = None
    category: ProfileType
    
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
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None