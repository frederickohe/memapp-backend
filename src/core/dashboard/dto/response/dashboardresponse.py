from typing import List, Optional

from pydantic import BaseModel

from core.news.dto.response.newsresponse import NewsResponse


class ProminentProfileResponse(BaseModel):
    id: str
    full_name: str
    profile_picture_url: Optional[str] = None
    current_branch: Optional[str] = None
    occupation: Optional[str] = None
    prominent_headline: Optional[str] = None
    volunteer_points: int = 0

    class Config:
        from_attributes = True


class MemberDashboardResponse(BaseModel):
    impact_stories: List[NewsResponse]
    recent_news: List[NewsResponse]
    upcoming_events: List[NewsResponse]
    prominent_profiles: List[ProminentProfileResponse]

    class Config:
        from_attributes = True
