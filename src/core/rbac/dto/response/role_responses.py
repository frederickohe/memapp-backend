from typing import List, Optional

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: str
    name: str
    group: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class RolePermissionSummary(BaseModel):
    id: str
    name: str
    group: str

    class Config:
        orm_mode = True


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str
    is_system: bool
    is_active: bool
    permissions: Optional[List[RolePermissionSummary]] = None

    class Config:
        orm_mode = True


class PermissionsListResponse(BaseModel):
    permissions: List[PermissionResponse]


class RolesListResponse(BaseModel):
    roles: List[RoleResponse]
