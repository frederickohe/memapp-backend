from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class AdminResponse(BaseModel):
    id: str
    fullname: str
    email: EmailStr
    phone_number: Optional[str] = None
    user_type: str
    role: Optional[str] = None
    profile_picture_url: Optional[str] = None
    enabled: bool
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
