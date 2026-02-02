from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class FormFieldResponse(BaseModel):
    """Response model for form field"""
    name: str
    label: str
    field_type: str
    required: bool
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ProgramFormResponse(BaseModel):
    """Response model for a form within a program"""
    id: str
    title: str
    description: Optional[str] = None
    fields: List[FormFieldResponse] = []
    
    class Config:
        from_attributes = True


class UserBasicResponse(BaseModel):
    """Basic user information"""
    id: str
    fullname: str
    email: str
    profile_picture_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProgramResponse(BaseModel):
    """Response model for a program"""
    id: str
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
    status: str
    is_published: bool
    allow_registration: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgramDetailResponse(BaseModel):
    """Detailed response model for a program with forms and participants"""
    id: str
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
    status: str
    is_published: bool
    allow_registration: bool
    created_by: str
    forms: List[ProgramFormResponse] = []
    participant_count: int = 0
    participants: List[UserBasicResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PagedProgramResponse(BaseModel):
    """Response model for paginated programs"""
    total: int
    page: int
    size: int
    items: List[ProgramDetailResponse]
    
    class Config:
        from_attributes = True


class ProgramEnrollmentResponse(BaseModel):
    """Response model for program enrollment (form response)"""
    id: str
    program_id: Optional[str] = None
    user_id: str
    status: str
    completion_percentage: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    dropped_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProgramEnrollmentsListResponse(BaseModel):
    """Response model for list of enrollments in a program"""
    program_id: str
    program_title: str
    total_enrollments: int
    page: int
    size: int
    enrollments: List[ProgramEnrollmentResponse]
    
    class Config:
        from_attributes = True


class UserProgramsResponse(BaseModel):
    """Response model for programs a user is participating in"""
    total: int
    page: int
    size: int
    programs: List[ProgramResponse]
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
    class Config:
        from_attributes = True
