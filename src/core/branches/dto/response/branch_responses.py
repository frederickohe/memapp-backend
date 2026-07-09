from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RegionResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    branch_count: int = 0
    created_at: datetime

    class Config:
        orm_mode = True


class BranchPresidentSummary(BaseModel):
    id: str
    full_name: str
    email: str
    phone: Optional[str] = None


class BranchResponse(BaseModel):
    id: str
    region_id: str
    region_name: str
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    president: Optional[BranchPresidentSummary] = None
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class RegionListResponse(BaseModel):
    regions: List[RegionResponse]


class BranchListResponse(BaseModel):
    branches: List[BranchResponse]


class TopBranchStat(BaseModel):
    branch_id: str
    branch_name: str
    region_name: str
    member_count: int
    member_target: int
    member_progress_pct: int


class RecentRegistration(BaseModel):
    id: str
    name: str
    branch_name: Optional[str] = None
    member_id: Optional[str] = None
    status: str
    created_at: datetime


class ProgressOverviewResponse(BaseModel):
    scope: str
    region_id: Optional[str] = None
    region_name: Optional[str] = None
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    total_members: int
    active_members: int
    inactive_members: int
    member_target: int
    members_remaining: int
    member_progress_pct: int
    active_member_pct: int
    avg_members_per_branch: int
    branches_at_goal: int
    pending_vhs: int
    approved_vhs: int
    branch_count: int
    top_branches: List[TopBranchStat]
    recent_registrations: List[RecentRegistration]


class BroadcastMessageResponse(BaseModel):
    channel: str
    scope: str
    recipients_total: int
    sent_count: int
    failed_count: int
    message: str
