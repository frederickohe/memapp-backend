from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreateAdminUserRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=6, max_length=20)
    password: str = Field(..., min_length=8)
    role_id: str
    reset_required: bool = False
    assigned_region: Optional[str] = None
    assigned_branch: Optional[str] = None


class UpdateAdminUserRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=6, max_length=20)
    role_id: Optional[str] = None
    is_active: Optional[bool] = None
    reset_required: Optional[bool] = None
    assigned_region: Optional[str] = None
    assigned_branch: Optional[str] = None


class ResetAdminUserPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
