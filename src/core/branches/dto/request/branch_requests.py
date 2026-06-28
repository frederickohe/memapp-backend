from typing import Optional

from pydantic import BaseModel, Field


class CreateRegionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class UpdateRegionRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class CreateBranchRequest(BaseModel):
    region_id: str
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=300)
    lat: Optional[float] = None
    lng: Optional[float] = None
    president_id: Optional[str] = None


class UpdateBranchRequest(BaseModel):
    region_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=300)
    lat: Optional[float] = None
    lng: Optional[float] = None
    president_id: Optional[str] = None
    is_active: Optional[bool] = None


class AssignPresidentRequest(BaseModel):
    president_id: Optional[str] = None


class BroadcastMessageRequest(BaseModel):
    channel: str = Field(..., regex="^(sms|email)$")
    scope: str = Field(..., regex="^(national|region|branch)$")
    region_id: Optional[str] = None
    branch_id: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
