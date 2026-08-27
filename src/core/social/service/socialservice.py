from datetime import datetime, timedelta, timezone
import secrets
import string
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, subqueryload

from core.news.model.News import News
from core.programs.model.program import Program
from core.social.dto.social_dto import (
    PagedSocialFeed,
    PagedSocialProfiles,
    SocialAuthor,
    SocialFeedItem,
    SocialLikeResponse,
    SocialPostResponse,
    SocialProfile,
)
from core.social.model.social import SocialLike, SocialPost, SocialPostKind
from core.user.model.User import User, UserStatus, UserType

def _aware(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


YMCA_AUTHOR = SocialAuthor(
    id="ymca",
    name="YMCA Ghana",
    handle="ymcaghana",
    avatar=None,
    is_org=True,
    branch="National",
)

YMCA_PROFILE = SocialProfile(
    id="ymca",
    name="YMCA Ghana",
    handle="ymcaghana",
    avatar=None,
    branch="National",
    occupation="Ghana National Council",
    skills=[],
    points=0,
    post_count=0,
    is_self=False,
)

PLACEHOLDER_IMAGE = (
    "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1400&q=80"
)


def make_handle(user: User) -> str:
    parts = (user.fullname or "member").strip().split()
    if not parts:
        return "member"
    if len(parts) >= 2:
        return f"{parts[0]}{parts[-1][:1]}".lower()
    return parts[0].lower()


def to_author(user: User) -> SocialAuthor:
    return SocialAuthor(
        id=user.id,
        name=user.fullname or "Member",
        handle=make_handle(user),
        avatar=user.profile_picture_url,
        is_org=False,
        branch=user.current_branch,
    )


class SocialService:
    def __init__(self, db: Session):
        self.db = db

    def _id(self, prefix: str) -> str:
        return prefix + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    def _like_counts(self, target_type: str, target_ids: List[str]) -> dict:
        if not target_ids:
            return {}
        rows = (
            self.db.query(SocialLike.target_id, func.count(SocialLike.id))
            .filter(SocialLike.target_type == target_type, SocialLike.target_id.in_(target_ids))
            .group_by(SocialLike.target_id)
            .all()
        )
        return {row[0]: row[1] for row in rows}

    def _liked_set(self, user_id: Optional[str], target_type: str, target_ids: List[str]) -> set:
        if not user_id or not target_ids:
            return set()
        rows = (
            self.db.query(SocialLike.target_id)
            .filter(
                SocialLike.user_id == user_id,
                SocialLike.target_type == target_type,
                SocialLike.target_id.in_(target_ids),
            )
            .all()
        )
        return {row[0] for row in rows}

    def _news_image(self, news: News) -> str:
        media = sorted(news.media or [], key=lambda item: item.order or 0)
        if media and media[0].url:
            return media[0].url
        return PLACEHOLDER_IMAGE

    def create_post(self, user: User, caption: Optional[str], media_url: str, kind: str) -> SocialPostResponse:
        kind_value = (kind or SocialPostKind.IMPACT).upper()
        if kind_value not in (SocialPostKind.IMPACT, SocialPostKind.STORY):
            raise HTTPException(status_code=400, detail="kind must be IMPACT or STORY")
        if not media_url:
            raise HTTPException(status_code=400, detail="media_url is required")

        post = SocialPost(
            id=self._id("POST_"),
            user_id=user.id,
            caption=(caption or "").strip() or None,
            media_url=media_url,
            media_type="IMAGE",
            kind=kind_value,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return self._post_to_response(post, user_id=user.id)

    def get_feed(self, user_id: Optional[str], page: int = 1, size: int = 20) -> PagedSocialFeed:
        posts = (
            self.db.query(SocialPost)
            .order_by(desc(SocialPost.created_at))
            .limit(80)
            .all()
        )
        news_items = (
            self.db.query(News)
            .options(subqueryload(News.media))
            .filter(News.is_published == True)
            .order_by(desc(News.published_at), desc(News.created_at))
            .limit(40)
            .all()
        )
        programs = (
            self.db.query(Program)
            .filter(Program.is_published == True)
            .order_by(desc(Program.created_at))
            .limit(30)
            .all()
        )

        post_ids = [p.id for p in posts]
        news_ids = [n.id for n in news_items]
        program_ids = [p.id for p in programs]
        post_likes = self._like_counts("POST", post_ids)
        news_likes = self._like_counts("NEWS", news_ids)
        program_likes = self._like_counts("PROGRAM", program_ids)
        liked_posts = self._liked_set(user_id, "POST", post_ids)
        liked_news = self._liked_set(user_id, "NEWS", news_ids)
        liked_programs = self._liked_set(user_id, "PROGRAM", program_ids)

        items: List[SocialFeedItem] = []
        for post in posts:
            author = to_author(post.author) if post.author else SocialAuthor(
                id=post.user_id, name="Member", handle="member"
            )
            items.append(
                SocialFeedItem(
                    id=f"POST:{post.id}",
                    item_type="POST",
                    source_id=post.id,
                    title=None,
                    caption=post.caption or "",
                    media_url=post.media_url,
                    category="Impact" if post.kind == SocialPostKind.IMPACT else "Story",
                    kind=post.kind,
                    author=author,
                    likes=post_likes.get(post.id, 0),
                    liked=post.id in liked_posts,
                    created_at=post.created_at,
                )
            )

        for news in news_items:
            category = "Projects" if news.is_impact_story else (
                "Events" if news.content_type == "EVENT" else "News"
            )
            items.append(
                SocialFeedItem(
                    id=f"NEWS:{news.id}",
                    item_type="NEWS",
                    source_id=news.id,
                    title=news.title,
                    caption=news.summary or news.title,
                    media_url=self._news_image(news),
                    category=category,
                    kind=None,
                    author=YMCA_AUTHOR,
                    likes=news_likes.get(news.id, 0),
                    liked=news.id in liked_news,
                    created_at=news.published_at or news.created_at,
                )
            )

        for program in programs:
            items.append(
                SocialFeedItem(
                    id=f"PROGRAM:{program.id}",
                    item_type="PROGRAM",
                    source_id=program.id,
                    title=program.title,
                    caption=program.description or program.title,
                    media_url=program.thumbnail_url or PLACEHOLDER_IMAGE,
                    category=program.category or "Programs",
                    kind=None,
                    author=YMCA_AUTHOR,
                    likes=program_likes.get(program.id, 0),
                    liked=program.id in liked_programs,
                    created_at=program.created_at,
                )
            )

        items.sort(key=lambda item: _aware(item.created_at), reverse=True)
        total = len(items)
        start = (page - 1) * size
        page_items = items[start:start + size]
        return PagedSocialFeed(total=total, page=page, size=size, items=page_items)

    def get_stories(self, user_id: Optional[str]) -> List[SocialFeedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
        posts = (
            self.db.query(SocialPost)
            .filter(SocialPost.kind == SocialPostKind.STORY, SocialPost.created_at >= cutoff)
            .order_by(desc(SocialPost.created_at))
            .limit(30)
            .all()
        )
        seen = set()
        unique = []
        for post in posts:
            if post.user_id in seen:
                continue
            seen.add(post.user_id)
            unique.append(post)

        ids = [p.id for p in unique]
        likes = self._like_counts("POST", ids)
        liked = self._liked_set(user_id, "POST", ids)
        items = []
        for post in unique:
            author = to_author(post.author) if post.author else SocialAuthor(
                id=post.user_id, name="Member", handle="member"
            )
            items.append(
                SocialFeedItem(
                    id=f"POST:{post.id}",
                    item_type="POST",
                    source_id=post.id,
                    caption=post.caption or "",
                    media_url=post.media_url,
                    category="Story",
                    kind=post.kind,
                    author=author,
                    likes=likes.get(post.id, 0),
                    liked=post.id in liked,
                    created_at=post.created_at,
                )
            )
        return items

    def toggle_like(self, user: User, item_id: str) -> SocialLikeResponse:
        if ":" not in item_id:
            raise HTTPException(status_code=400, detail="Invalid item id")
        target_type, target_id = item_id.split(":", 1)
        target_type = target_type.upper()
        if target_type not in ("POST", "NEWS", "PROGRAM"):
            raise HTTPException(status_code=400, detail="Invalid item type")

        existing = (
            self.db.query(SocialLike)
            .filter(
                SocialLike.user_id == user.id,
                SocialLike.target_type == target_type,
                SocialLike.target_id == target_id,
            )
            .first()
        )
        if existing:
            self.db.delete(existing)
            self.db.commit()
            liked = False
        else:
            self.db.add(
                SocialLike(
                    id=self._id("LIKE_"),
                    user_id=user.id,
                    target_type=target_type,
                    target_id=target_id,
                )
            )
            self.db.commit()
            liked = True

        count = (
            self.db.query(func.count(SocialLike.id))
            .filter(SocialLike.target_type == target_type, SocialLike.target_id == target_id)
            .scalar()
        )
        return SocialLikeResponse(liked=liked, likes=int(count or 0))

    def search_users(self, query: str, page: int, size: int, current_user_id: str) -> PagedSocialProfiles:
        q = self.db.query(User).filter(
            User.user_type == UserType.MEMBER,
            User.status != UserStatus.DELETED,
        )
        term = (query or "").strip()
        if term:
            like = f"%{term}%"
            q = q.filter(
                or_(
                    User.fullname.ilike(like),
                    User.member_id.ilike(like),
                    User.current_branch.ilike(like),
                    User.email.ilike(like),
                )
            )
        total = q.count()
        users = q.order_by(User.fullname.asc()).offset((page - 1) * size).limit(size).all()
        return PagedSocialProfiles(
            total=total,
            page=page,
            size=size,
            items=[self._to_profile(user, current_user_id) for user in users],
        )

    def get_profile(self, user_id: str, current_user_id: str) -> SocialProfile:
        if user_id == "ymca":
            return YMCA_PROFILE
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_profile(user, current_user_id)

    def get_user_posts(self, user_id: str, current_user_id: str, page: int, size: int) -> PagedSocialFeed:
        if user_id == "ymca":
            return PagedSocialFeed(total=0, page=page, size=size, items=[])
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        query = self.db.query(SocialPost).filter(SocialPost.user_id == user_id).order_by(desc(SocialPost.created_at))
        total = query.count()
        posts = query.offset((page - 1) * size).limit(size).all()
        ids = [p.id for p in posts]
        likes = self._like_counts("POST", ids)
        liked = self._liked_set(current_user_id, "POST", ids)
        author = to_author(user)
        items = [
            SocialFeedItem(
                id=f"POST:{post.id}",
                item_type="POST",
                source_id=post.id,
                caption=post.caption or "",
                media_url=post.media_url,
                category="Impact" if post.kind == SocialPostKind.IMPACT else "Story",
                kind=post.kind,
                author=author,
                likes=likes.get(post.id, 0),
                liked=post.id in liked,
                created_at=post.created_at,
            )
            for post in posts
        ]
        return PagedSocialFeed(total=total, page=page, size=size, items=items)

    def _to_profile(self, user: User, current_user_id: str) -> SocialProfile:
        post_count = self.db.query(func.count(SocialPost.id)).filter(SocialPost.user_id == user.id).scalar()
        return SocialProfile(
            id=user.id,
            name=user.fullname or "Member",
            handle=make_handle(user),
            avatar=user.profile_picture_url,
            branch=user.current_branch,
            occupation=user.occupation,
            skills=user.skills or [],
            points=user.volunteer_points or 0,
            post_count=int(post_count or 0),
            is_self=user.id == current_user_id,
            gender=getattr(user.gender, "value", user.gender),
            date_joined=user.created_at,
            facebook_url=user.facebook_url,
            whatsapp_number=user.whatsapp_number or user.phone_number,
            linkedin_url=user.linkedin_url,
            twitter_url=user.twitter_url,
            instagram_url=user.instagram_url,
        )

    def _post_to_response(self, post: SocialPost, user_id: str) -> SocialPostResponse:
        likes = self._like_counts("POST", [post.id]).get(post.id, 0)
        liked = post.id in self._liked_set(user_id, "POST", [post.id])
        author = to_author(post.author) if post.author else SocialAuthor(
            id=post.user_id, name="Member", handle="member"
        )
        return SocialPostResponse(
            id=post.id,
            user_id=post.user_id,
            caption=post.caption,
            media_url=post.media_url,
            media_type=post.media_type,
            kind=post.kind,
            likes=likes,
            liked=liked,
            created_at=post.created_at,
            author=author,
        )
