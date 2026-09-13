"""Seed sample Y Social impact and story posts from existing members."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

import utilities.dbmodels  # noqa: F401

from datetime import datetime, timedelta, timezone

from core.social.model.social import SocialPost, SocialPostKind
from core.user.model.User import User, UserType
from utilities.dbconfig import SessionLocal
import secrets
import string

SAMPLES = [
    {
        "kind": SocialPostKind.STORY,
        "caption": "Branch outreach today — serving with the team.",
        "media_url": "https://ymcaghana.org/wp-content/uploads/2026/04/transform.jpeg",
        "hours_ago": 6,
    },
    {
        "kind": SocialPostKind.IMPACT,
        "caption": "Youth leadership camp was full of energy and new friendships.",
        "media_url": "https://ymcaghana.org/wp-content/uploads/2026/09/DSF3343-1024x567.jpg",
        "hours_ago": 20,
    },
    {
        "kind": SocialPostKind.STORY,
        "caption": "Smart Girl session complete. Proud of these young leaders.",
        "media_url": "https://ymcaghana.org/wp-content/uploads/2026/06/smart.jpg",
        "hours_ago": 10,
    },
    {
        "kind": SocialPostKind.IMPACT,
        "caption": "Green Ideas clean-up at the community park.",
        "media_url": "https://ymcaghana.org/wp-content/uploads/2026/06/green.jpg",
        "hours_ago": 30,
    },
]


def _id():
    return "POST_" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))


def main():
    db = SessionLocal()
    try:
        members = (
            db.query(User)
            .filter(User.user_type == UserType.MEMBER)
            .order_by(User.created_at.asc())
            .limit(4)
            .all()
        )
        if not members:
            raise SystemExit("No members found to seed social posts")

        posts = db.query(SocialPost).order_by(SocialPost.created_at.asc()).all()
        unsplash_posts = [post for post in posts if "unsplash.com" in (post.media_url or "")]
        if unsplash_posts:
            for index, post in enumerate(unsplash_posts):
                sample = SAMPLES[index % len(SAMPLES)]
                post.media_url = sample["media_url"]
                print(f"Updated image for {post.kind} post {post.id}")
            db.commit()
            print(f"Social image refresh complete. updated={len(unsplash_posts)}")
            return

        if posts:
            print(f"Social posts already present ({len(posts)}). Skipping.")
            return

        now = datetime.now(timezone.utc)
        for index, sample in enumerate(SAMPLES):
            member = members[index % len(members)]
            post = SocialPost(
                id=_id(),
                user_id=member.id,
                caption=sample["caption"],
                media_url=sample["media_url"],
                media_type="IMAGE",
                kind=sample["kind"],
                created_at=now - timedelta(hours=sample["hours_ago"]),
            )
            db.add(post)
            print(f"Seeded {sample['kind']} for {member.fullname}")
        db.commit()
        print("Social seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
