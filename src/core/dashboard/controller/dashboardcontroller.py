from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user, get_db
from core.dashboard.dto.response.dashboardresponse import (
    MemberDashboardResponse,
    ProminentProfileResponse,
)
from core.dashboard.service.dashboardservice import DashboardService
from core.rbac.service.member_user_service import MemberUserService
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
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Public list of prominent member profiles for the dashboard"""
    return MemberUserService(db).list_prominent_profiles(limit=limit)
