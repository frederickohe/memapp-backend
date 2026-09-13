from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, validator


class UpdateMemberUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    member_id: Optional[str] = None
    membership_type: Optional[str] = None
    date_joined_organization: Optional[date] = None
    past_positions: Optional[List[str]] = None
    current_branch: Optional[str] = None
    branch_id: Optional[str] = None
    month_dues_paid_status: Optional[str] = None
    year_affiliation_paid_status: Optional[str] = None
    is_prominent: Optional[bool] = None
    prominent_order: Optional[int] = None
    prominent_headline: Optional[str] = None

    @validator("date_joined_organization", pre=True)
    def empty_date_to_none(cls, value):
        if value == "" or value is None:
            return None
        return value


class AssignMemberRoleRequest(BaseModel):
    role_id: Optional[str] = None
    assigned_region: Optional[str] = None
    assigned_branch: Optional[str] = None
