from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class SubmitVolunteerHoursRequest(BaseModel):
    hours: float = Field(..., gt=0, le=24)
    activity_name: str = Field(..., min_length=2, max_length=200)
    activity_description: Optional[str] = Field(None, max_length=2000)
    branch: Optional[str] = Field(None, max_length=100)
    volunteer_date: date
    proof_document_url: Optional[str] = Field(None, max_length=500)


class RejectVhsRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)
