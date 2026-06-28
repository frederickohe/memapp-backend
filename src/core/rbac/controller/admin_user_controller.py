from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_db, require_admin
from core.rbac.dependencies import require_permission
from core.rbac.dto.request.admin_user_requests import (
    CreateAdminUserRequest,
    ResetAdminUserPasswordRequest,
    UpdateAdminUserRequest,
)
from core.rbac.dto.response.admin_user_responses import AdminUserListResponse, AdminUserResponse
from core.rbac.dto.response.api_envelope import ApiEnvelope, ApiMessage
from core.rbac.service.admin_user_service import AdminUserService
from core.user.model.User import User

admin_user_routes = APIRouter()


@admin_user_routes.get("/users", response_model=ApiEnvelope[AdminUserListResponse])
def list_admin_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _: User = Depends(require_permission("admin_users.view")),
    db: Session = Depends(get_db),
):
    service = AdminUserService(db)
    return ApiEnvelope(data=service.list_admin_users(page=page, limit=limit))


@admin_user_routes.get("/users/{user_id}", response_model=ApiEnvelope[AdminUserResponse])
def get_admin_user(
    user_id: str,
    _: User = Depends(require_permission("admin_users.view")),
    db: Session = Depends(get_db),
):
    service = AdminUserService(db)
    return ApiEnvelope(data=service.get_admin_user(user_id))


@admin_user_routes.post("/users", response_model=ApiEnvelope[AdminUserResponse])
def create_admin_user(
    request: CreateAdminUserRequest,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AdminUserService(db)
    return ApiEnvelope(data=service.create_admin_user(request, actor=actor))


@admin_user_routes.put("/users/{user_id}", response_model=ApiEnvelope[AdminUserResponse])
def update_admin_user(
    user_id: str,
    request: UpdateAdminUserRequest,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AdminUserService(db)
    return ApiEnvelope(data=service.update_admin_user(user_id, request, actor))


@admin_user_routes.post("/users/{user_id}/deactivate", response_model=ApiEnvelope[ApiMessage])
def deactivate_admin_user(
    user_id: str,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AdminUserService(db)
    service.deactivate_admin_user(user_id, actor)
    return ApiEnvelope(data=ApiMessage(message="Admin user deactivated successfully"))


@admin_user_routes.post(
    "/users/{user_id}/reset-password",
    response_model=ApiEnvelope[ApiMessage],
)
def reset_admin_password(
    user_id: str,
    request: ResetAdminUserPasswordRequest,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AdminUserService(db)
    service.reset_admin_password(user_id, request, actor)
    return ApiEnvelope(data=ApiMessage(message="Password reset successfully"))
