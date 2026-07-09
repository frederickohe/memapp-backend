from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from core.auth.dependencies import get_current_user, get_db, require_admin
from core.user.model.User import User
from core.news.dto.response.newsresponse import NewsResponse, PagedNewsResponse, MessageResponse
from core.news.dto.request.newsrequest import NewsCreateRequest, NewsUpdateRequest
from core.news.service.newsservice import NewsService

news_routes = APIRouter()


# ============= PUBLIC ROUTES =============

@news_routes.get("/", response_model=PagedNewsResponse)
def get_published_news(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    sort_by: str = Query("published_at", regex="^(published_at|created_at|event_date)$"),
    content_type: Optional[str] = Query(None, regex="^(NEWS|EVENT)$"),
    db=Depends(get_db),
):
    """Get all published news and events with pagination"""
    news_service = NewsService(db)
    return news_service.get_all_published_news(
        page=page, size=size, sort_by=sort_by, content_type=content_type
    )


@news_routes.get("/impact-stories", response_model=List[NewsResponse])
def get_impact_stories(
    limit: int = Query(5, ge=1, le=20),
    db=Depends(get_db),
):
    """Get published impact stories for member dashboards"""
    news_service = NewsService(db)
    return news_service.get_impact_stories(limit=limit)


@news_routes.get("/events/upcoming", response_model=List[NewsResponse])
def get_upcoming_events(
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_db),
):
    """Get published upcoming events"""
    news_service = NewsService(db)
    return news_service.get_upcoming_events(limit=limit)


@news_routes.get("/{news_id}", response_model=NewsResponse)
def get_news_detail(news_id: str, db=Depends(get_db)):
    """Get a specific news segment"""
    news_service = NewsService(db)
    return news_service.get_news(news_id)


# ============= ADMIN ROUTES =============

@news_routes.post("/admin/create", response_model=NewsResponse)
def create_news(
    news_data: NewsCreateRequest,
    user: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Create a new news segment or event (Admin only)"""
    media_list = [media.dict() for media in news_data.media] if news_data.media else []

    news_service = NewsService(db)
    return news_service.create_news(
        admin_id=user.id,
        title=news_data.title,
        content=news_data.content,
        summary=news_data.summary,
        content_type=news_data.content_type,
        is_impact_story=news_data.is_impact_story,
        event_date=news_data.event_date,
        event_location=news_data.event_location,
        is_published=news_data.is_published,
        media_list=media_list,
    )


@news_routes.get("/admin/all", response_model=PagedNewsResponse)
def get_all_news(
    page: int = Query(1, ge=1),
    size: int = Query(15, ge=1, le=50),
    content_type: Optional[str] = Query(None, regex="^(NEWS|EVENT)$"),
    published_only: Optional[bool] = None,
    impact_only: Optional[bool] = None,
    _: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Get all news for admin management"""
    news_service = NewsService(db)
    return news_service.get_all_news(
        page=page,
        size=size,
        content_type=content_type,
        published_only=published_only,
        impact_only=impact_only,
    )


@news_routes.get("/admin/my-posts", response_model=PagedNewsResponse)
def get_my_news(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    published_only: bool = Query(False),
    user: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Get all news posted by the current admin"""
    news_service = NewsService(db)
    return news_service.get_admin_news(
        admin_id=user.id,
        page=page,
        size=size,
        published_only=published_only,
    )


@news_routes.get("/admin/user/{admin_id}", response_model=PagedNewsResponse)
def get_admin_news(
    admin_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    published_only: bool = Query(True),
    db=Depends(get_db),
):
    """Get all published news posted by a specific admin"""
    news_service = NewsService(db)
    return news_service.get_admin_news(
        admin_id=admin_id,
        page=page,
        size=size,
        published_only=published_only,
    )


@news_routes.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: str,
    news_data: NewsUpdateRequest,
    user: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Update a news segment (Admin only)"""
    media_list = [media.dict() for media in news_data.media] if news_data.media else None

    news_service = NewsService(db)
    return news_service.update_news(
        news_id=news_id,
        admin_id=user.id,
        title=news_data.title,
        content=news_data.content,
        summary=news_data.summary,
        content_type=news_data.content_type,
        is_impact_story=news_data.is_impact_story,
        event_date=news_data.event_date,
        event_location=news_data.event_location,
        is_published=news_data.is_published,
        media_list=media_list,
    )


@news_routes.post("/{news_id}/publish", response_model=NewsResponse)
def publish_news(
    news_id: str,
    user: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Publish a news segment (Admin only)"""
    news_service = NewsService(db)
    return news_service.publish_news(news_id=news_id, admin_id=user.id)


@news_routes.post("/{news_id}/unpublish", response_model=NewsResponse)
def unpublish_news(
    news_id: str,
    user: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Unpublish a news segment (Admin only)"""
    news_service = NewsService(db)
    return news_service.unpublish_news(news_id=news_id, admin_id=user.id)


@news_routes.delete("/{news_id}", response_model=MessageResponse)
def delete_news(
    news_id: str,
    user: User = Depends(require_admin),
    db=Depends(get_db),
):
    """Delete a news segment (Admin only)"""
    news_service = NewsService(db)
    return news_service.delete_news(news_id=news_id, admin_id=user.id)
