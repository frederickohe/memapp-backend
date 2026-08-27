from typing import Optional

from pydantic import BaseModel, Field


class ProminentProfileCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    headline: Optional[str] = Field(None, max_length=200)
    bio: str = Field(..., min_length=1)
    photo_url: Optional[str] = Field(None, max_length=500)
    country: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    era: Optional[str] = Field(None, max_length=80)
    category: str = Field("WORLD", pattern="^(GHANA|WORLD)$")
    sort_order: int = 0
    is_published: bool = True


class ProminentProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    country: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    era: Optional[str] = Field(None, max_length=80)
    category: Optional[str] = Field(None, pattern="^(GHANA|WORLD)$")
    sort_order: Optional[int] = None
    is_published: Optional[bool] = None
