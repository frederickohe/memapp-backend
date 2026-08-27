from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from utilities.dbconfig import Base


class SocialPostKind(str):
    IMPACT = "IMPACT"
    STORY = "STORY"


class SocialPost(Base):
    __tablename__ = "social_posts"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_url: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False, default="IMAGE")
    kind: Mapped[str] = mapped_column(String(20), nullable=False, default=SocialPostKind.IMPACT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="joined")


class SocialLike(Base):
    __tablename__ = "social_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_social_like_target"),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SocialView(Base):
    __tablename__ = "social_views"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_social_view_target"),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
