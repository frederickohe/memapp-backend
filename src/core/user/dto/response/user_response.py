from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional, List


class UserResponse(BaseModel):
    id: str
    fullname: str
    email: str
    phone_number: Optional[str] = None
    
    # Personal Information
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Membership Information
    membership_type: Optional[str] = None
    current_branch: Optional[str] = None
    member_id: Optional[str] = None
    month_dues_paid_status: Optional[str] = None
    year_affiliation_paid_status: Optional[str] = None
    
    # Professional Information
    occupation: Optional[str] = None
    organization_workplace: Optional[str] = None
    skills: Optional[List[str]] = None
    experiences: Optional[List[str]] = None
    
    # Connected Users
    connected_users: Optional[List[str]] = None
    
    # Social Media Profiles
    facebook_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    
    # Notification Preferences
    profile_sharing: Optional[str] = None
    in_app_notification: Optional[str] = None
    sms_notification: Optional[str] = None
    
    # Status and Timestamps
    status: str
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True