from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SocialAuthor(BaseModel):
    id: str
    name: str
    handle: str
    avatar: Optional[str] = None
    is_org: bool = False
    branch: Optional[str] = None


class SocialFeedItem(BaseModel):
    id: str
    item_type: str
    source_id: str
    title: Optional[str] = None
    caption: str = ""
    media_url: str
    category: Optional[str] = None
    kind: Optional[str] = None
    author: SocialAuthor
    likes: int = 0
    liked: bool = False
    views: int = 0
    viewed: bool = False
    created_at: datetime


class PagedSocialFeed(BaseModel):
    total: int
    page: int
    size: int
    items: List[SocialFeedItem]


class SocialPostCreateRequest(BaseModel):
    caption: Optional[str] = None
    media_url: str
    kind: str = Field(default="IMPACT")


class SocialPostResponse(BaseModel):
    id: str
    user_id: str
    caption: Optional[str] = None
    media_url: str
    media_type: str
    kind: str
    likes: int = 0
    liked: bool = False
    views: int = 0
    viewed: bool = False
    created_at: datetime
    author: SocialAuthor


class SocialLikeRequest(BaseModel):
    item_id: str


class SocialLikeResponse(BaseModel):
    liked: bool
    likes: int


class SocialViewRequest(BaseModel):
    item_id: str


class SocialViewResponse(BaseModel):
    viewed: bool
    views: int


class SocialProfile(BaseModel):
    id: str
    name: str
    handle: str
    avatar: Optional[str] = None
    branch: Optional[str] = None
    occupation: Optional[str] = None
    skills: List[str] = []
    points: int = 0
    post_count: int = 0
    is_self: bool = False
    gender: Optional[str] = None
    date_joined: Optional[datetime] = None
    facebook_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None


class PagedSocialProfiles(BaseModel):
    total: int
    page: int
    size: int
    items: List[SocialProfile]


class MessageResponse(BaseModel):
    message: str
