from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator


OPTIONAL_STRING_FIELDS = {
    "phone_number",
    "profile_picture_url",
    "nationality",
    "gender",
    "address",
    "membership_type",
    "current_branch",
    "member_id",
    "facebook_url",
    "whatsapp_number",
    "linkedin_url",
    "twitter_url",
    "instagram_url",
    "occupation",
    "organization_workplace",
}


class UserCreateRequest(BaseModel):
    fullname: str
    email: EmailStr
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

    # Timestamps — server fills this if the client omits it
    created_at: Optional[datetime] = None

    @validator("email", pre=True)
    def normalize_email(cls, value):
        if value is None:
            return value
        return str(value).strip().lower()

    @validator("fullname")
    def normalize_fullname(cls, value):
        name = (value or "").strip()
        if not name:
            raise ValueError("Full name is required")
        return name

    @validator("date_of_birth", pre=True)
    def empty_date_to_none(cls, value):
        if value == "" or value is None:
            return None
        return value

    @validator(*OPTIONAL_STRING_FIELDS, pre=True)
    def empty_string_to_none(cls, value):
        if value is None:
            return None
        text = str(value).strip()
        return text or None
