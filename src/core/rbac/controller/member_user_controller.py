from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_db
from core.rbac.dependencies import require_permission
from core.rbac.dto.request.member_user_requests import UpdateMemberUserRequest
from core.rbac.dto.response.api_envelope import ApiEnvelope, ApiMessage
from core.rbac.dto.response.member_user_responses import (
    MemberUserListResponse,
    MemberUserOverviewResponse,
    MemberUserResponse,
)
from core.rbac.service.member_user_service import MemberUserService
from core.user.model.User import User

member_user_routes = APIRouter()


@member_user_routes.get("/members/overview", response_model=ApiEnvelope[MemberUserOverviewResponse])
def get_members_overview(
    scope: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    _: User = Depends(require_permission("members.view")),
    db: Session = Depends(get_db),
):
    service = MemberUserService(db)
    return ApiEnvelope(data=service.get_overview(scope=scope, region_id=region_id, branch_id=branch_id))


@member_user_routes.get("/members", response_model=ApiEnvelope[MemberUserListResponse])
def list_member_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    branch: Optional[str] = None,
    branch_id: Optional[str] = None,
    region_id: Optional[str] = None,
    scope: Optional[str] = None,
    membership_type: Optional[str] = None,
    prominent_only: Optional[bool] = None,
    _: User = Depends(require_permission("members.view")),
    db: Session = Depends(get_db),
):
    service = MemberUserService(db)
    return ApiEnvelope(
        data=service.list_member_users(
            page=page,
            limit=limit,
            search=search,
            status=status,
            branch=branch,
            branch_id=branch_id,
            region_id=region_id,
            scope=scope,
            membership_type=membership_type,
            prominent_only=prominent_only,
        )
    )


@member_user_routes.get("/members/{user_id}", response_model=ApiEnvelope[MemberUserResponse])
def get_member_user(
    user_id: str,
    _: User = Depends(require_permission("members.view")),
    db: Session = Depends(get_db),
):
    service = MemberUserService(db)
    return ApiEnvelope(data=service.get_member_user(user_id))


@member_user_routes.put("/members/{user_id}", response_model=ApiEnvelope[MemberUserResponse])
def update_member_user(
    user_id: str,
    request: UpdateMemberUserRequest,
    _: User = Depends(require_permission("members.update")),
    db: Session = Depends(get_db),
):
    service = MemberUserService(db)
    return ApiEnvelope(data=service.update_member_user(user_id, request))


@member_user_routes.post("/members/{user_id}/deactivate", response_model=ApiEnvelope[ApiMessage])
def deactivate_member_user(
    user_id: str,
    _: User = Depends(require_permission("members.delete")),
    db: Session = Depends(get_db),
):
    service = MemberUserService(db)
    service.deactivate_member_user(user_id)
    return ApiEnvelope(data=ApiMessage(message="User deactivated successfully"))
