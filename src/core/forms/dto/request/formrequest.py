from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class FormFieldRequest(BaseModel):
    """Request model for form field definition"""
    name: str
    label: str
    field_type: str  # "text", "email", "number", "textarea", "select", "checkbox", "radio", "date", etc.
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None  # For select, radio, checkbox fields
    validation: Optional[Dict[str, Any]] = None  # Custom validation rules
    
    class Config:
        from_attributes = True


class FormCreateRequest(BaseModel):
    """Request model for creating a form"""
    title: str
    description: Optional[str] = None
    assignment_type: str  # "PUBLIC", "PROGRAM", or "USER"
    program_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    fields: List[FormFieldRequest]
    is_active: bool = True
    
    class Config:
        from_attributes = True


class FormUpdateRequest(BaseModel):
    """Request model for updating a form"""
    title: Optional[str] = None
    description: Optional[str] = None
    assignment_type: Optional[str] = None
    program_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    fields: Optional[List[FormFieldRequest]] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True


class FormResponseSubmitRequest(BaseModel):
    """Request model for submitting a form response"""
    data: Dict[str, Any]  # Key-value pairs matching form fields
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
