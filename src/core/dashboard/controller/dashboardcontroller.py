from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user, get_db, require_admin
from core.dashboard.dto.request.profilerequest import (
    ProminentProfileCreateRequest,
    ProminentProfileUpdateRequest,
)
from core.dashboard.dto.response.dashboardresponse import (
    MemberDashboardResponse,
    PagedProminentProfilesResponse,
    ProminentProfileMessageResponse,
    ProminentProfileResponse,
)
from core.dashboard.service.dashboardservice import DashboardService
from core.dashboard.service.profileservice import ProminentProfileService
from core.user.model.User import User

dashboard_routes = APIRouter()


@dashboard_routes.get("/", response_model=MemberDashboardResponse)
def get_member_dashboard(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Member dashboard feed: impact stories, news, events, and prominent profiles"""
    return DashboardService(db).get_member_dashboard()


@dashboard_routes.get("/prominent-profiles", response_model=List[ProminentProfileResponse])
def get_prominent_profiles(
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = Query(None, pattern="^(GHANA|WORLD)$"),
    db: Session = Depends(get_db),
):
    """Public list of prominent YMCA profiles for the dashboard"""
    return ProminentProfileService(db).list_profiles(limit=limit, category=category)


@dashboard_routes.get("/admin/prominent-profiles", response_model=PagedProminentProfilesResponse)
def admin_list_prominent_profiles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    category: Optional[str] = Query(None, pattern="^(GHANA|WORLD)$"),
    published_only: Optional[bool] = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin list of all prominent profiles, including drafts"""
    return ProminentProfileService(db).list_admin(
        page=page,
        size=size,
        category=category,
        published_only=published_only,
    )


@dashboard_routes.post("/admin/prominent-profiles", response_model=ProminentProfileResponse)
def admin_create_prominent_profile(
    request: ProminentProfileCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a prominent profile (Admin only)"""
    return ProminentProfileService(db).create_profile(request)


@dashboard_routes.put(
    "/admin/prominent-profiles/{profile_id}",
    response_model=ProminentProfileResponse,
)
def admin_update_prominent_profile(
    profile_id: str,
    request: ProminentProfileUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a prominent profile (Admin only)"""
    return ProminentProfileService(db).update_profile(profile_id, request)


@dashboard_routes.delete(
    "/admin/prominent-profiles/{profile_id}",
    response_model=ProminentProfileMessageResponse,
)
def admin_delete_prominent_profile(
    profile_id: str,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a prominent profile (Admin only)"""
    return ProminentProfileService(db).delete_profile(profile_id)


@dashboard_routes.get(
    "/prominent-profiles/{profile_id}",
    response_model=ProminentProfileResponse,
)
def get_prominent_profile(profile_id: str, db: Session = Depends(get_db)):
    """Public detail for a prominent YMCA profile"""
    return ProminentProfileService(db).get_profile(profile_id)
