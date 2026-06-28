from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class MemberUserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    member_id: Optional[str] = None
    membership_type: Optional[str] = None
    current_branch: Optional[str] = None
    month_dues_paid_status: Optional[str] = None
    year_affiliation_paid_status: Optional[str] = None
    volunteer_points: int = 0
    profile_picture_url: Optional[str] = None
    is_prominent: bool = False
    prominent_order: int = 0
    prominent_headline: Optional[str] = None
    is_active: bool
    status: str
    created_at: datetime


class MemberUserListResponse(BaseModel):
    total: int
    page: int
    pages: int
    users: List[MemberUserResponse]


class MemberUserOverviewResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    dues_pending: int
    affiliation_pending: int
