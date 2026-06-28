from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from core.user.model.User import AdminRole


class AdminCreateRequest(BaseModel):
    fullname: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: AdminRole
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
