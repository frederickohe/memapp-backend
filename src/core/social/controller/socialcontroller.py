from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user, get_db
from core.social.dto.social_dto import (
    PagedSocialFeed,
    PagedSocialProfiles,
    SocialFeedItem,
    SocialLikeRequest,
    SocialLikeResponse,
    SocialPostCreateRequest,
    SocialPostResponse,
    SocialProfile,
)
from core.social.service.socialservice import SocialService
from core.user.model.User import User

social_routes = APIRouter()


@social_routes.get("/feed", response_model=PagedSocialFeed)
def get_feed(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).get_feed(current_user.id, page=page, size=size)


@social_routes.get("/stories", response_model=List[SocialFeedItem])
def get_stories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).get_stories(current_user.id)


@social_routes.post("/posts", response_model=SocialPostResponse, status_code=201)
def create_post(
    request: SocialPostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).create_post(
        user=current_user,
        caption=request.caption,
        media_url=request.media_url,
        kind=request.kind,
    )


@social_routes.post("/like", response_model=SocialLikeResponse)
def toggle_like(
    request: SocialLikeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).toggle_like(current_user, request.item_id)


@social_routes.get("/users/search", response_model=PagedSocialProfiles)
def search_users(
    q: Optional[str] = Query(""),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).search_users(q or "", page, size, current_user.id)


@social_routes.get("/users/{user_id}", response_model=SocialProfile)
def get_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).get_profile(user_id, current_user.id)


@social_routes.get("/users/{user_id}/posts", response_model=PagedSocialFeed)
def get_user_posts(
    user_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SocialService(db).get_user_posts(user_id, current_user.id, page, size)
