from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from core.user.model.User import User
from utilities.dbconfig import Base
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum as PythonEnum


class MediaType(str, PythonEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class NewsMedia(Base):
    """Model for storing media files (images/videos) associated with news"""
    __tablename__ = "news_media"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    news_id: Mapped[str] = mapped_column(String(20), ForeignKey("news.id"), nullable=False)
    
    # Media file URL or path
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Type of media: IMAGE or VIDEO
    media_type: Mapped[MediaType] = mapped_column(String, nullable=False)
    
    # Optional: Store metadata like original filename, size, etc.
    media_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Display order
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    news: Mapped["News"] = relationship("News", back_populates="media")
    
    def __repr__(self):
        return f"<NewsMedia(id={self.id}, news_id={self.news_id}, type={self.media_type})>"


class News(Base):
    """Model for storing news segments posted by admins"""
    __tablename__ = "news"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, unique=True)
    
    # Admin who posted the news
    admin_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False)
    
    # News content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional: Summary/excerpt
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status: published or draft
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    admin: Mapped["User"] = relationship("User", back_populates="news_posts")
    media: Mapped[List["NewsMedia"]] = relationship("NewsMedia", back_populates="news", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<News(id={self.id}, title={self.title}, admin_id={self.admin_id})>"
