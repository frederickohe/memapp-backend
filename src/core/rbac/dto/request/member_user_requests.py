from typing import Optional

from pydantic import BaseModel, EmailStr


class UpdateMemberUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    member_id: Optional[str] = None
    membership_type: Optional[str] = None
    current_branch: Optional[str] = None
    branch_id: Optional[str] = None
    month_dues_paid_status: Optional[str] = None
    year_affiliation_paid_status: Optional[str] = None
    is_prominent: Optional[bool] = None
    prominent_order: Optional[int] = None
    prominent_headline: Optional[str] = None
