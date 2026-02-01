from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreateRequest(BaseModel):  
    fullname: str
    email: str
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    password: str = Field(..., min_length=8)
    
    # Personal Information
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    
    # Membership Information
    membership_type: Optional[str] = None
    current_branch: Optional[str] = None
    member_id: Optional[str] = None
    
    # Connection Information
    facebook_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    
    # Professional Information
    occupation: Optional[str] = None
    organization_workplace: Optional[str] = None
    skills: Optional[List[str]] = None
    experiences: Optional[List[str]] = None
    
    # Notification Preferences
    profile_sharing: Optional[bool] = None
    in_app_notification: Optional[bool] = None
    sms_notification: Optional[bool] = None
    
    # Timestamps
    created_at: datetime

    