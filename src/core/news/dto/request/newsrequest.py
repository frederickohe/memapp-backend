from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MediaCreateRequest(BaseModel):
    """Request model for creating/updating media"""
    url: str
    media_type: str  # "IMAGE" or "VIDEO"
    metadata: Optional[dict] = None
    order: int = 0
    
    class Config:
        from_attributes = True


class NewsCreateRequest(BaseModel):
    """Request model for creating a news segment"""
    title: str
    content: str
    summary: Optional[str] = None
    is_published: bool = False
    media: List[MediaCreateRequest] = []
    
    class Config:
        from_attributes = True


class NewsUpdateRequest(BaseModel):
    """Request model for updating a news segment"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_published: Optional[bool] = None
    media: Optional[List[MediaCreateRequest]] = None
    
    class Config:
        from_attributes = True
