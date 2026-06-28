from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class AdminRoleSummary(BaseModel):
    id: str
    name: str


class AdminUserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    phone: str
    is_active: bool
    reset_required: bool
    last_login_at: Optional[datetime] = None
    role: AdminRoleSummary
    assigned_region: Optional[str] = None
    assigned_branch: Optional[str] = None


class AdminUserListResponse(BaseModel):
    total: int
    page: int
    pages: int
    users: List[AdminUserResponse]
