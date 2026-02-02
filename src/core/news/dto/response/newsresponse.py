from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MediaResponse(BaseModel):
    """Response model for media files"""
    id: str
    news_id: str
    url: str
    media_type: str
    metadata: Optional[dict] = None
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NewsResponse(BaseModel):
    """Response model for a news segment"""
    id: str
    admin_id: str
    title: str
    content: str
    summary: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    media: List[MediaResponse] = []
    
    class Config:
        from_attributes = True


class PagedNewsResponse(BaseModel):
    """Response model for paginated news results"""
    total: int
    page: int
    size: int
    items: List[NewsResponse]
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
    class Config:
        from_attributes = True
