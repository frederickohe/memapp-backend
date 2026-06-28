from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


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
