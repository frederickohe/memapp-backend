from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from core.auth.service.sessiondriver import SessionDriver, TokenData
from fastapi_jwt_auth import AuthJWT
from core.exceptions import *
import jwt

from utilities.dbconfig import SessionLocal
from sqlalchemy.orm import Session
import logging
from core.news.model.News import News
from core.user.model.User import User

# DTO Models
from core.news.dto.response.newsresponse import NewsResponse, PagedNewsResponse, MessageResponse
from core.news.dto.request.newsrequest import NewsCreateRequest, NewsUpdateRequest

from core.news.service.newsservice import NewsService
from fastapi_jwt_auth.exceptions import MissingTokenError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Helper functions
def validate_token(authjwt: AuthJWT = Depends()):
    try:
        authjwt.jwt_required()
        return authjwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token expired. Please log in again."
        )
    except MissingTokenError:
        raise HTTPException(
            status_code=401,
            detail="No token found. Please create an account and log in.",
        )
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_role(user: User) -> User:
    """Check if user has admin role"""
    # You may want to add a role field to User model for this
    # For now, we'll assume admins are determined by your business logic
    # You can modify this based on your actual admin determination
    return user


# Router
news_routes = APIRouter(prefix="/news", tags=["News"])


# ============= PUBLIC ROUTES =============

@news_routes.get("/", response_model=PagedNewsResponse)
def get_published_news(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    sort_by: str = Query("published_at", regex="^(published_at|created_at)$"),
    db: Session = Depends(get_db)
):
    """Get all published news segments with pagination"""
    news_service = NewsService(db)
    return news_service.get_all_published_news(page=page, size=size, sort_by=sort_by)


@news_routes.get("/{news_id}", response_model=NewsResponse)
def get_news_detail(
    news_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific news segment"""
    news_service = NewsService(db)
    return news_service.get_news(news_id)


# ============= ADMIN ROUTES =============

@news_routes.post("/admin/create", response_model=NewsResponse)
def create_news(
    news_data: NewsCreateRequest,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Create a new news segment (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == current_user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert media request objects to dicts
    media_list = [media.dict() for media in news_data.media] if news_data.media else []
    
    news_service = NewsService(db)
    return news_service.create_news(
        admin_id=user.id,
        title=news_data.title,
        content=news_data.content,
        summary=news_data.summary,
        is_published=news_data.is_published,
        media_list=media_list
    )


@news_routes.get("/admin/my-posts", response_model=PagedNewsResponse)
def get_my_news(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    published_only: bool = Query(False),
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Get all news posted by the current admin"""
    current_user_email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == current_user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    news_service = NewsService(db)
    return news_service.get_admin_news(
        admin_id=user.id,
        page=page,
        size=size,
        published_only=published_only
    )


@news_routes.get("/admin/user/{admin_id}", response_model=PagedNewsResponse)
def get_admin_news(
    admin_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    published_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all published news posted by a specific admin"""
    news_service = NewsService(db)
    return news_service.get_admin_news(
        admin_id=admin_id,
        page=page,
        size=size,
        published_only=published_only
    )


@news_routes.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: str,
    news_data: NewsUpdateRequest,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Update a news segment (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == current_user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert media request objects to dicts
    media_list = [media.dict() for media in news_data.media] if news_data.media else None
    
    news_service = NewsService(db)
    return news_service.update_news(
        news_id=news_id,
        admin_id=user.id,
        title=news_data.title,
        content=news_data.content,
        summary=news_data.summary,
        is_published=news_data.is_published,
        media_list=media_list
    )


@news_routes.post("/{news_id}/publish", response_model=NewsResponse)
def publish_news(
    news_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Publish a news segment (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == current_user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    news_service = NewsService(db)
    return news_service.publish_news(news_id=news_id, admin_id=user.id)


@news_routes.post("/{news_id}/unpublish", response_model=NewsResponse)
def unpublish_news(
    news_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Unpublish a news segment (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == current_user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    news_service = NewsService(db)
    return news_service.unpublish_news(news_id=news_id, admin_id=user.id)


@news_routes.delete("/{news_id}", response_model=MessageResponse)
def delete_news(
    news_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Delete a news segment (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == current_user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    news_service = NewsService(db)
    return news_service.delete_news(news_id=news_id, admin_id=user.id)
