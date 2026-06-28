from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.auth.dependencies import get_current_user, get_db
from core.rbac.dependencies import require_permission
from core.rbac.dto.response.api_envelope import ApiEnvelope
from core.user.model.User import User
from core.vhs.dto.request.vhs_requests import RejectVhsRequest, SubmitVolunteerHoursRequest
from core.vhs.dto.response.vhs_responses import VhsSubmissionListResponse, VhsSubmissionResponse
from core.vhs.service.vhsservice import VhsService

vhs_member_routes = APIRouter()
vhs_admin_routes = APIRouter()


@vhs_member_routes.post("/submit", response_model=ApiEnvelope[VhsSubmissionResponse])
def submit_volunteer_hours(
    request: SubmitVolunteerHoursRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Member submits volunteer hours for review and points."""
    service = VhsService(db)
    return ApiEnvelope(data=service.submit(user, request))


@vhs_admin_routes.get("/vhs-submissions", response_model=ApiEnvelope[VhsSubmissionListResponse])
def list_vhs_submissions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    _: User = Depends(require_permission("vhs.view")),
    db: Session = Depends(get_db),
):
    service = VhsService(db)
    return ApiEnvelope(
        data=service.list_submissions(
            page=page,
            limit=limit,
            status=status,
            scope=scope,
            region_id=region_id,
            branch_id=branch_id,
        )
    )


@vhs_admin_routes.get("/vhs-submissions/{submission_id}", response_model=ApiEnvelope[VhsSubmissionResponse])
def get_vhs_submission(
    submission_id: str,
    _: User = Depends(require_permission("vhs.view")),
    db: Session = Depends(get_db),
):
    service = VhsService(db)
    return ApiEnvelope(data=service.get_submission(submission_id))


@vhs_admin_routes.post(
    "/vhs-submissions/{submission_id}/approve",
    response_model=ApiEnvelope[VhsSubmissionResponse],
)
def approve_vhs_submission(
    submission_id: str,
    admin: User = Depends(require_permission("vhs.review")),
    db: Session = Depends(get_db),
):
    service = VhsService(db)
    return ApiEnvelope(data=service.approve(submission_id, admin))


@vhs_admin_routes.post(
    "/vhs-submissions/{submission_id}/reject",
    response_model=ApiEnvelope[VhsSubmissionResponse],
)
def reject_vhs_submission(
    submission_id: str,
    request: RejectVhsRequest,
    admin: User = Depends(require_permission("vhs.review")),
    db: Session = Depends(get_db),
):
    service = VhsService(db)
    return ApiEnvelope(data=service.reject(submission_id, admin, request))
