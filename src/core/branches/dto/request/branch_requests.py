from typing import List, Optional

from pydantic import BaseModel, Field, root_validator


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
    scope: str = Field(..., regex="^(national|region|branch|users)$")
    region_id: Optional[str] = None
    branch_id: Optional[str] = None
    user_ids: Optional[List[str]] = None
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)

    @root_validator
    def validate_scope_requirements(cls, values):
        scope = values.get("scope")
        if scope == "users":
            user_ids = values.get("user_ids") or []
            if not user_ids:
                raise ValueError("user_ids is required when scope is users")
        return values
