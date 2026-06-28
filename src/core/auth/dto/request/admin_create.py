from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AdminCreateRequest(BaseModel):
    fullname: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role_id: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    assigned_region: Optional[str] = None
    assigned_branch: Optional[str] = None
