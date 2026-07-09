from datetime import datetime, timezone
import secrets
import string
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from fastapi import HTTPException, status
from core.news.model.News import News, NewsMedia, MediaType, ContentType
from core.user.model.User import User
from core.news.dto.response.newsresponse import NewsResponse, MediaResponse, PagedNewsResponse, MessageResponse


class NewsService:
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_news_id(self) -> str:
        """Generate a unique news ID"""
        return "NEWS_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def _generate_media_id(self) -> str:
        """Generate a unique media ID"""
        return "MEDIA_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    def _add_media(self, news: News, media_list: List[dict]) -> None:
        for idx, media_data in enumerate(media_list):
            media = NewsMedia(
                id=self._generate_media_id(),
                news_id=news.id,
                url=media_data.get("url"),
                media_type=media_data.get("media_type", MediaType.IMAGE),
                media_metadata=media_data.get("metadata"),
                order=media_data.get("order", idx),
            )
            news.media.append(media)
    
    def create_news(
        self,
        admin_id: str,
        title: str,
        content: str,
        summary: Optional[str] = None,
        content_type: str = ContentType.NEWS,
        is_impact_story: bool = False,
        event_date: Optional[datetime] = None,
        event_location: Optional[str] = None,
        is_published: bool = False,
        media_list: Optional[List[dict]] = None,
    ) -> NewsResponse:
        """Create a new news segment"""
        admin = self.db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        news = News(
            id=self._generate_news_id(),
            admin_id=admin_id,
            title=title,
            content=content,
            summary=summary,
            content_type=content_type,
            is_impact_story=is_impact_story,
            event_date=event_date,
            event_location=event_location,
            is_published=is_published,
            published_at=datetime.now(timezone.utc) if is_published else None,
        )
        
        if media_list:
            self._add_media(news, media_list)
        
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
    
    def get_news(self, news_id: str) -> NewsResponse:
        """Get a specific news segment by ID"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        return NewsResponse.from_orm(news)
    
    def _published_query(
        self,
        content_type: Optional[str] = None,
        impact_only: bool = False,
    ):
        query = self.db.query(News).filter(News.is_published == True)
        if content_type:
            query = query.filter(News.content_type == content_type)
        if impact_only:
            query = query.filter(News.is_impact_story == True)
        return query

    def get_all_published_news(
        self,
        page: int = 1,
        size: int = 10,
        sort_by: str = "published_at",
        content_type: Optional[str] = None,
    ) -> PagedNewsResponse:
        """Get all published news with pagination"""
        query = self._published_query(content_type=content_type)
        
        if sort_by == "published_at":
            query = query.order_by(desc(News.published_at))
        elif sort_by == "created_at":
            query = query.order_by(desc(News.created_at))
        elif sort_by == "event_date":
            query = query.order_by(desc(News.event_date))
        else:
            query = query.order_by(desc(News.published_at))
        
        total = query.count()
        skip = (page - 1) * size
        items = query.offset(skip).limit(size).all()
        
        return PagedNewsResponse(
            total=total,
            page=page,
            size=size,
            items=[NewsResponse.from_orm(item) for item in items],
        )

    def get_impact_stories(self, limit: int = 5) -> List[NewsResponse]:
        """Get published impact stories for member dashboards"""
        items = (
            self._published_query(impact_only=True)
            .order_by(desc(News.published_at))
            .limit(limit)
            .all()
        )
        return [NewsResponse.from_orm(item) for item in items]

    def get_upcoming_events(self, limit: int = 10) -> List[NewsResponse]:
        """Get published upcoming events sorted by event date"""
        now = datetime.now(timezone.utc)
        items = (
            self._published_query(content_type=ContentType.EVENT)
            .filter(News.event_date >= now)
            .order_by(News.event_date.asc())
            .limit(limit)
            .all()
        )
        return [NewsResponse.from_orm(item) for item in items]
    
    def get_admin_news(
        self,
        admin_id: str,
        page: int = 1,
        size: int = 10,
        published_only: bool = False,
    ) -> PagedNewsResponse:
        """Get news posted by a specific admin"""
        admin = self.db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        query = self.db.query(News).filter(News.admin_id == admin_id)
        
        if published_only:
            query = query.filter(News.is_published == True)
        
        query = query.order_by(desc(News.created_at))
        total = query.count()
        skip = (page - 1) * size
        items = query.offset(skip).limit(size).all()
        
        return PagedNewsResponse(
            total=total,
            page=page,
            size=size,
            items=[NewsResponse.from_orm(item) for item in items],
        )

    def get_all_news(
        self,
        page: int = 1,
        size: int = 10,
        content_type: Optional[str] = None,
        published_only: Optional[bool] = None,
        impact_only: Optional[bool] = None,
    ) -> PagedNewsResponse:
        """Get all news for admin management"""
        query = self.db.query(News)

        if content_type:
            query = query.filter(News.content_type == content_type)
        if published_only is not None:
            query = query.filter(News.is_published == published_only)
        if impact_only is not None:
            query = query.filter(News.is_impact_story == impact_only)

        query = query.order_by(desc(News.created_at))
        total = query.count()
        skip = (page - 1) * size
        items = query.offset(skip).limit(size).all()

        return PagedNewsResponse(
            total=total,
            page=page,
            size=size,
            items=[NewsResponse.from_orm(item) for item in items],
        )
    
    def update_news(
        self,
        news_id: str,
        admin_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        content_type: Optional[str] = None,
        is_impact_story: Optional[bool] = None,
        event_date: Optional[datetime] = None,
        event_location: Optional[str] = None,
        is_published: Optional[bool] = None,
        media_list: Optional[List[dict]] = None,
    ) -> NewsResponse:
        """Update a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this news")
        
        if title is not None:
            news.title = title
        if content is not None:
            news.content = content
        if summary is not None:
            news.summary = summary
        if content_type is not None:
            news.content_type = content_type
        if is_impact_story is not None:
            news.is_impact_story = is_impact_story
        if event_date is not None:
            news.event_date = event_date
        if event_location is not None:
            news.event_location = event_location
        
        if is_published is not None and is_published != news.is_published:
            news.is_published = is_published
            if is_published:
                news.published_at = datetime.now(timezone.utc)
        
        if media_list is not None:
            for media in news.media:
                self.db.delete(media)
            self._add_media(news, media_list)
        
        news.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
    
    def delete_news(self, news_id: str, admin_id: str) -> MessageResponse:
        """Delete a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this news")
        
        self.db.delete(news)
        self.db.commit()
        
        return MessageResponse(message="News deleted successfully")
    
    def publish_news(self, news_id: str, admin_id: str) -> NewsResponse:
        """Publish a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to publish this news")
        
        news.is_published = True
        news.published_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
    
    def unpublish_news(self, news_id: str, admin_id: str) -> NewsResponse:
        """Unpublish a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to unpublish this news")
        
        news.is_published = False
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
