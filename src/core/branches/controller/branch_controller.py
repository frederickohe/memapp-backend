from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_db
from core.branches.dto.request.branch_requests import (
    AssignPresidentRequest,
    BroadcastMessageRequest,
    CreateBranchRequest,
    CreateRegionRequest,
    UpdateBranchRequest,
    UpdateRegionRequest,
)
from core.branches.dto.response.branch_responses import (
    BranchListResponse,
    BranchResponse,
    BroadcastMessageResponse,
    ProgressOverviewResponse,
    RegionListResponse,
    RegionResponse,
)
from core.branches.service.analytics_service import AnalyticsService
from core.branches.service.branch_service import BranchService
from core.branches.service.message_broadcast_service import MessageBroadcastService
from core.rbac.dependencies import require_permission
from core.rbac.dto.response.api_envelope import ApiEnvelope
from core.user.model.User import User

branch_routes = APIRouter()


@branch_routes.get("/regions", response_model=ApiEnvelope[RegionListResponse])
def list_regions(
    active_only: bool = Query(True),
    _: User = Depends(require_permission("branches.view")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).list_regions(active_only=active_only))


@branch_routes.post("/regions", response_model=ApiEnvelope[RegionResponse])
def create_region(
    request: CreateRegionRequest,
    _: User = Depends(require_permission("branches.create")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).create_region(request))


@branch_routes.put("/regions/{region_id}", response_model=ApiEnvelope[RegionResponse])
def update_region(
    region_id: str,
    request: UpdateRegionRequest,
    _: User = Depends(require_permission("branches.update")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).update_region(region_id, request))


@branch_routes.get("/branches", response_model=ApiEnvelope[BranchListResponse])
def list_branches(
    region_id: Optional[str] = Query(None),
    active_only: bool = Query(True),
    _: User = Depends(require_permission("branches.view")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).list_branches(region_id=region_id, active_only=active_only))


@branch_routes.get("/branches/{branch_id}", response_model=ApiEnvelope[BranchResponse])
def get_branch(
    branch_id: str,
    _: User = Depends(require_permission("branches.view")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).get_branch(branch_id))


@branch_routes.post("/branches", response_model=ApiEnvelope[BranchResponse])
def create_branch(
    request: CreateBranchRequest,
    _: User = Depends(require_permission("branches.create")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).create_branch(request))


@branch_routes.put("/branches/{branch_id}", response_model=ApiEnvelope[BranchResponse])
def update_branch(
    branch_id: str,
    request: UpdateBranchRequest,
    _: User = Depends(require_permission("branches.update")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).update_branch(branch_id, request))


@branch_routes.post("/branches/{branch_id}/president", response_model=ApiEnvelope[BranchResponse])
def assign_branch_president(
    branch_id: str,
    request: AssignPresidentRequest,
    _: User = Depends(require_permission("branches.update")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=BranchService(db).assign_president(branch_id, request))


@branch_routes.get("/analytics/progress", response_model=ApiEnvelope[ProgressOverviewResponse])
def get_progress_overview(
    scope: Optional[str] = Query("national"),
    region_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    _: User = Depends(require_permission("analytics.view")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(
        data=AnalyticsService(db).get_progress_overview(
            scope=scope,
            region_id=region_id,
            branch_id=branch_id,
        )
    )


@branch_routes.post("/messages/broadcast", response_model=ApiEnvelope[BroadcastMessageResponse])
def broadcast_message(
    request: BroadcastMessageRequest,
    _: User = Depends(require_permission("messages.send")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=MessageBroadcastService(db).broadcast(request))
