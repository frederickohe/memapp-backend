"""Receive a WP Webhooks post payload and upsert app news."""
import re
import secrets
from datetime import datetime, timezone
from html import unescape
from typing import Any, Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import settings
from core.news.model.News import ContentType, MediaType, News, NewsMedia
from core.user.model.User import User, UserStatus, UserType

WORDPRESS_AUTHOR_ID = "USR_WORDPRESS"
WORDPRESS_AUTHOR_EMAIL = "wordpress@ymemberapp.com"
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"(?is)<(script|style).*?>.*?</\1>")
_BREAK_RE = re.compile(r"(?i)<br\s*/?>")
_BLOCK_RE = re.compile(r"(?i)</p>")
_SPACE_RE = re.compile(r"[ \t]+")
_BLANK_RE = re.compile(r"\n{3,}")


def html_to_text(value: str) -> str:
    text = _SCRIPT_RE.sub(" ", value or "")
    text = _BREAK_RE.sub("\n", text)
    text = _BLOCK_RE.sub("\n\n", text)
    text = _TAG_RE.sub(" ", text)
    text = unescape(text)
    text = _SPACE_RE.sub(" ", text)
    text = _BLANK_RE.sub("\n\n", text)
    return text.strip()


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _category_slugs(taxonomies: Any) -> set[str]:
    categories = _as_dict(_as_dict(taxonomies).get("category"))
    return {str(slug) for slug in categories.keys()}


def _thumbnail_url(payload: dict) -> str:
    thumb = payload.get("post_thumbnail")
    if isinstance(thumb, str):
        return thumb.strip()
    return ""


def _ensure_author(db: Session) -> User:
    author = db.query(User).filter(User.id == WORDPRESS_AUTHOR_ID).first()
    if author:
        return author
    author = User(
        id=WORDPRESS_AUTHOR_ID,
        fullname="WordPress",
        email=WORDPRESS_AUTHOR_EMAIL,
        hashed_password=_pwd.hash(secrets.token_urlsafe(32)),
        enabled=False,
        user_type=UserType.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(author)
    db.flush()
    return author


def _replace_image(news: News, url: str) -> None:
    news.media.clear()
    if not url:
        return
    news.media.append(
        NewsMedia(
            id="MEDIA_" + secrets.token_hex(6),
            news_id=news.id,
            url=url[:500],
            media_type=MediaType.IMAGE,
            order=0,
        )
    )


def _new_id() -> str:
    return "NEWS_" + secrets.token_hex(6)


class WordpressSync:
    def __init__(self, db: Session):
        self.db = db

    def handle(self, payload: dict, event: str) -> dict:
        post = _as_dict(payload.get("post"))
        post_id = payload.get("post_id") or post.get("ID")
        if post_id is None:
            raise HTTPException(status_code=400, detail="post_id is required")
        wordpress_id = str(post_id)

        existing = (
            self.db.query(News)
            .filter(News.wordpress_post_id == wordpress_id)
            .first()
        )

        if event == "delete":
            if existing:
                self.db.delete(existing)
                self.db.commit()
            return {"status": "deleted", "message": "News removed", "news_id": None}

        post_type = str(post.get("post_type") or "post")
        if post_type != "post":
            return {"status": "ignored", "message": "Not a post", "news_id": None}

        wanted = (settings.WORDPRESS_NEWS_CATEGORY or "").strip()
        if wanted and wanted not in _category_slugs(payload.get("taxonomies")):
            if existing and existing.is_published:
                existing.is_published = False
                self.db.commit()
            return {"status": "ignored", "message": "Category not synced", "news_id": getattr(existing, "id", None)}

        status = str(post.get("post_status") or "")
        published = status == "publish"
        if not published and not existing:
            return {"status": "ignored", "message": "Unpublished post", "news_id": None}

        title = html_to_text(str(post.get("post_title") or "")).strip() or "Untitled"
        content = html_to_text(str(post.get("post_content") or ""))
        excerpt = html_to_text(str(post.get("post_excerpt") or ""))
        summary = (excerpt or content)[:500] or None
        permalink = payload.get("post_permalink") or post.get("guid")
        permalink = str(permalink)[:500] if permalink else None
        image = _thumbnail_url(payload)

        if existing:
            existing.title = title[:255]
            existing.content = content or title
            existing.summary = summary
            existing.wordpress_permalink = permalink
            if published and not existing.is_published:
                existing.published_at = datetime.now(timezone.utc)
            existing.is_published = published
            existing.updated_at = datetime.now(timezone.utc)
            _replace_image(existing, image)
            self.db.commit()
            return {"status": "updated", "message": "News updated", "news_id": existing.id}

        author = _ensure_author(self.db)
        news = News(
            id=_new_id(),
            admin_id=author.id,
            title=title[:255],
            content=content or title,
            summary=summary,
            content_type=ContentType.NEWS,
            is_impact_story=False,
            is_published=True,
            published_at=datetime.now(timezone.utc),
            wordpress_post_id=wordpress_id,
            wordpress_permalink=permalink,
        )
        _replace_image(news, image)
        self.db.add(news)
        self.db.commit()
        return {"status": "created", "message": "News created", "news_id": news.id}
