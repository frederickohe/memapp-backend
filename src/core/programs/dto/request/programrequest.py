from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProgramCreateRequest(BaseModel):
    """Request model for creating a program"""
    title: str
    description: Optional[str] = None
    starting_date: datetime
    end_date: datetime
    register_url: Optional[str] = None
    youtube_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    form_ids: Optional[List[str]] = None  # IDs of forms to attach
    is_published: bool = False
    allow_registration: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ProgramUpdateRequest(BaseModel):
    """Request model for updating a program"""
    title: Optional[str] = None
    description: Optional[str] = None
    starting_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    register_url: Optional[str] = None
    youtube_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    form_ids: Optional[List[str]] = None
    is_published: Optional[bool] = None
    allow_registration: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ProgramEnrollmentRequest(BaseModel):
    """Request model for enrolling a user in a program"""
    user_id: str
    form_id: str  # ID of the form to submit for enrollment
    form_data: Dict[str, Any]  # The form submission data
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProgramEnrollmentUpdateRequest(BaseModel):
    """Request model for updating form response data"""
    completion_percentage: Optional[int] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
