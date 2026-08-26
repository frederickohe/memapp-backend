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


class FormResponse(BaseModel):
    """Response model for a form"""
    id: str
    admin_id: str
    title: str
    description: Optional[str] = None
    assignment_type: str
    program_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    fields: List[FormFieldResponse]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FormDetailResponse(BaseModel):
    """Detailed response model for a form with response counts"""
    id: str
    admin_id: str
    title: str
    description: Optional[str] = None
    assignment_type: str
    program_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    fields: List[FormFieldResponse]
    is_active: bool
    response_count: int = 0
    submitted: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FormResponseDataResponse(BaseModel):
    """Response model for a form submission"""
    id: str
    form_id: str
    user_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    data: Dict[str, Any]
    notes: Optional[str] = None
    is_submitted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FieldOptionCount(BaseModel):
    """Count of responses per option for choice fields"""
    option: str
    count: int


class FieldAnalytics(BaseModel):
    """Analytics for a single form field"""
    name: str
    label: str
    field_type: str
    total_answered: int = 0
    option_counts: Optional[List[FieldOptionCount]] = None


class DailyResponseCount(BaseModel):
    """Response count grouped by date"""
    date: str
    count: int


class FormAnalyticsResponse(BaseModel):
    """Analytics summary for a form"""
    form_id: str
    form_title: str
    total_responses: int
    responses_last_7_days: int
    responses_last_30_days: int
    daily_counts: List[DailyResponseCount]
    field_analytics: List[FieldAnalytics]
    
    class Config:
        from_attributes = True


class FormResponsesListResponse(BaseModel):
    """Response model for paginated form responses"""
    form_id: str
    form_title: str
    total_responses: int
    page: int
    size: int
    responses: List[FormResponseDataResponse]
    
    class Config:
        from_attributes = True


class PagedFormResponse(BaseModel):
    """Response model for paginated forms"""
    total: int
    page: int
    size: int
    items: List[FormDetailResponse]
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
    class Config:
        from_attributes = True
