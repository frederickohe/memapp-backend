from sqlalchemy.orm import Session

from core.dashboard.dto.response.dashboardresponse import MemberDashboardResponse
from core.dashboard.service.profileservice import ProminentProfileService
from core.news.service.newsservice import NewsService


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_member_dashboard(self) -> MemberDashboardResponse:
        news_service = NewsService(self.db)
        profile_service = ProminentProfileService(self.db)

        impact_stories = news_service.get_impact_stories(limit=5)
        recent_news_page = news_service.get_all_published_news(
            page=1, size=6, content_type="NEWS"
        )
        upcoming_events = news_service.get_upcoming_events(limit=6)
        prominent = profile_service.list_profiles(limit=12)

        return MemberDashboardResponse(
            impact_stories=impact_stories,
            recent_news=recent_news_page.items,
            upcoming_events=upcoming_events,
            prominent_profiles=prominent,
        )
