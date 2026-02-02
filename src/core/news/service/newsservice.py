from datetime import datetime
import secrets
import string
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from fastapi import HTTPException, status
from core.news.model.News import News, NewsMedia, MediaType
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
    
    def create_news(
        self,
        admin_id: str,
        title: str,
        content: str,
        summary: Optional[str] = None,
        is_published: bool = False,
        media_list: Optional[List[dict]] = None
    ) -> NewsResponse:
        """Create a new news segment"""
        # Verify admin exists
        admin = self.db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Create news record
        news = News(
            id=self._generate_news_id(),
            admin_id=admin_id,
            title=title,
            content=content,
            summary=summary,
            is_published=is_published,
            published_at=datetime.utcnow() if is_published else None
        )
        
        # Add media if provided
        if media_list:
            for idx, media_data in enumerate(media_list):
                media = NewsMedia(
                    id=self._generate_media_id(),
                    news_id=news.id,
                    url=media_data.get("url"),
                    media_type=media_data.get("media_type", MediaType.IMAGE),
                    metadata=media_data.get("metadata"),
                    order=media_data.get("order", idx)
                )
                news.media.append(media)
        
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
    
    def get_all_published_news(
        self,
        page: int = 1,
        size: int = 10,
        sort_by: str = "published_at"
    ) -> PagedNewsResponse:
        """Get all published news with pagination"""
        # Query published news only
        query = self.db.query(News).filter(News.is_published == True)
        
        # Sort by specified field in descending order
        if sort_by == "published_at":
            query = query.order_by(desc(News.published_at))
        elif sort_by == "created_at":
            query = query.order_by(desc(News.created_at))
        else:
            query = query.order_by(desc(News.published_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        items = query.offset(skip).limit(size).all()
        
        return PagedNewsResponse(
            total=total,
            page=page,
            size=size,
            items=[NewsResponse.from_orm(item) for item in items]
        )
    
    def get_admin_news(
        self,
        admin_id: str,
        page: int = 1,
        size: int = 10,
        published_only: bool = False
    ) -> PagedNewsResponse:
        """Get news posted by a specific admin"""
        # Verify admin exists
        admin = self.db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Build query
        query = self.db.query(News).filter(News.admin_id == admin_id)
        
        if published_only:
            query = query.filter(News.is_published == True)
        
        # Sort by creation date descending
        query = query.order_by(desc(News.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        items = query.offset(skip).limit(size).all()
        
        return PagedNewsResponse(
            total=total,
            page=page,
            size=size,
            items=[NewsResponse.from_orm(item) for item in items]
        )
    
    def update_news(
        self,
        news_id: str,
        admin_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        is_published: Optional[bool] = None,
        media_list: Optional[List[dict]] = None
    ) -> NewsResponse:
        """Update a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Verify admin ownership
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this news")
        
        # Update fields
        if title is not None:
            news.title = title
        if content is not None:
            news.content = content
        if summary is not None:
            news.summary = summary
        
        # Handle publish status change
        if is_published is not None and is_published != news.is_published:
            news.is_published = is_published
            if is_published:
                news.published_at = datetime.utcnow()
        
        # Update media if provided
        if media_list is not None:
            # Remove old media
            for media in news.media:
                self.db.delete(media)
            
            # Add new media
            for idx, media_data in enumerate(media_list):
                media = NewsMedia(
                    id=self._generate_media_id(),
                    news_id=news.id,
                    url=media_data.get("url"),
                    media_type=media_data.get("media_type", MediaType.IMAGE),
                    metadata=media_data.get("metadata"),
                    order=media_data.get("order", idx)
                )
                news.media.append(media)
        
        news.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
    
    def delete_news(self, news_id: str, admin_id: str) -> MessageResponse:
        """Delete a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Verify admin ownership
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
        
        # Verify admin ownership
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to publish this news")
        
        news.is_published = True
        news.published_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
    
    def unpublish_news(self, news_id: str, admin_id: str) -> NewsResponse:
        """Unpublish a news segment (admin only)"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Verify admin ownership
        if news.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to unpublish this news")
        
        news.is_published = False
        self.db.commit()
        self.db.refresh(news)
        
        return NewsResponse.from_orm(news)
