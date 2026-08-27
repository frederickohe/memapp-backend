from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class VolunteerMilestoneResponse(BaseModel):
    id: str
    name: str
    title: str
    hours_required: float
    image_key: Optional[str] = None
    level: int
    status: str
    hours_completed: float
    progress: float
    next_id: Optional[str] = None
    next_name: Optional[str] = None
    next_hours_required: Optional[float] = None


class VolunteerContributionResponse(BaseModel):
    id: str
    title: str
    hours: float
    points: Optional[int] = None
    volunteer_date: date
    status: str
    activity_description: Optional[str] = None
    branch: Optional[str] = None


class VolunteerImpactResponse(BaseModel):
    hours_volunteered: float
    volunteer_points: int
    events_attended: int
    community_rank: int
    total_members: int
    rank_title: str
    next_rank_title: Optional[str] = None
    next_rank_progress: float
    points_to_next: int
    current_milestone_id: Optional[str] = None
    milestones: List[VolunteerMilestoneResponse]
    recent_contributions: List[VolunteerContributionResponse]


class VhsSubmissionResponse(BaseModel):
    id: str
    user_id: str
    member_name: str
    member_id: Optional[str] = None
    member_email: Optional[str] = None
    member_phone: Optional[str] = None
    member_avatar_url: Optional[str] = None
    member_branch: Optional[str] = None
    hours: float
    activity_name: str
    activity_description: Optional[str] = None
    branch: Optional[str] = None
    volunteer_date: date
    proof_document_url: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    points_awarded: Optional[int] = None
    points_to_award: Optional[int] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


class VhsSubmissionListResponse(BaseModel):
    total: int
    page: int
    pages: int
    submissions: List[VhsSubmissionResponse]
