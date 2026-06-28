from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class CreateRoleRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., max_length=255)
    permission_ids: List[str] = Field(default_factory=list)


class UpdateRoleRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class SetRolePermissionsRequest(BaseModel):
    permission_ids: List[str] = Field(default_factory=list)
