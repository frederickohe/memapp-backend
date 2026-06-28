from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_db
from core.rbac.dependencies import require_permission
from core.rbac.dto.request.role_requests import (
    CreateRoleRequest,
    SetRolePermissionsRequest,
    UpdateRoleRequest,
)
from core.rbac.dto.response.api_envelope import ApiEnvelope, ApiMessage
from core.rbac.dto.response.role_responses import (
    PermissionResponse,
    PermissionsListResponse,
    RoleResponse,
    RolesListResponse,
)
from core.rbac.service.permission_service import PermissionService
from core.rbac.service.role_service import RoleService
from core.user.model.User import User

role_routes = APIRouter()


@role_routes.get("/permissions", response_model=ApiEnvelope[PermissionsListResponse])
def list_permissions(
    _: User = Depends(require_permission("roles.view")),
    db: Session = Depends(get_db),
):
    service = PermissionService(db)
    permissions = service.list_permissions()
    return ApiEnvelope(
        data=PermissionsListResponse(
            permissions=[PermissionResponse.from_orm(p) for p in permissions]
        )
    )


@role_routes.get("/roles", response_model=ApiEnvelope[RolesListResponse])
def list_roles(
    include_permissions: bool = Query(True),
    _: User = Depends(require_permission("roles.view")),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    roles = service.list_roles(include_permissions=include_permissions)
    return ApiEnvelope(data=RolesListResponse(roles=roles))


@role_routes.get("/roles/{role_id}", response_model=ApiEnvelope[RoleResponse])
def get_role(
    role_id: str,
    include_permissions: bool = Query(True),
    _: User = Depends(require_permission("roles.view")),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    role = service.get_role(role_id, include_permissions=include_permissions)
    return ApiEnvelope(data=role)


@role_routes.post("/roles", response_model=ApiEnvelope[RoleResponse])
def create_role(
    request: CreateRoleRequest,
    _: User = Depends(require_permission("roles.create")),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    role = service.create_role(request)
    return ApiEnvelope(data=role)


@role_routes.put("/roles/{role_id}", response_model=ApiEnvelope[RoleResponse])
def update_role(
    role_id: str,
    request: UpdateRoleRequest,
    _: User = Depends(require_permission("roles.update")),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    role = service.update_role(role_id, request)
    return ApiEnvelope(data=role)


@role_routes.delete("/roles/{role_id}", response_model=ApiEnvelope[ApiMessage])
def delete_role(
    role_id: str,
    _: User = Depends(require_permission("roles.delete")),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    service.delete_role(role_id)
    return ApiEnvelope(data=ApiMessage(message="Role deleted successfully"))


@role_routes.put("/roles/{role_id}/permissions", response_model=ApiEnvelope[RoleResponse])
def set_role_permissions(
    role_id: str,
    request: SetRolePermissionsRequest,
    _: User = Depends(require_permission("roles.assign_permissions")),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    role = service.set_role_permissions(role_id, request.permission_ids)
    return ApiEnvelope(data=role)
