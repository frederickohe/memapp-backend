from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class AdminRoleSummary(BaseModel):
    id: str
    name: str


class AdminResponse(BaseModel):
    id: str
    fullname: str
    email: EmailStr
    phone_number: Optional[str] = None
    user_type: str
    role: Optional[AdminRoleSummary] = None
    profile_picture_url: Optional[str] = None
    enabled: bool
    reset_required: bool = False
    status: str
    created_at: datetime
    assigned_region: Optional[str] = None
    assigned_branch: Optional[str] = None

    class Config:
        orm_mode = True
