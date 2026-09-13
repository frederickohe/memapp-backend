"""Replace stock/Unsplash images with official Ghana YMCA photographs."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

import utilities.dbmodels  # noqa: F401

from datetime import datetime, timezone

from core.dashboard.model.ProminentProfile import ProminentProfile
from core.news.model.News import ContentType, MediaType, News, NewsMedia
from core.news.service.newsservice import NewsService
from core.programs.model.program import Program
from core.social.model.social import SocialPost
from core.user.model.User import User
from utilities.dbconfig import SessionLocal

GH = "https://ymcaghana.org/wp-content/uploads"
ADMIN_ID = "ymD3MaEjEkbOmtxv8fye"

PROFILE_PHOTOS = {
    "PROF_Kufuor0001": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/John_Kufuor_080915-A-8817J-090.JPG/640px-John_Kufuor_080915-A-8817J-090.JPG",
    "PROF_Coffie0001": f"{GH}/2026/08/WhatsApp-Image-2026-08-25-at-8.37.14-AM.jpeg",
    "PROF_Williams01": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Sir_George_Williams_by_John_Collier.jpg/640px-Sir_George_Williams_by_John_Collier.jpg",
    "PROF_Sanvee0001": "https://www.ymca.int/wp-content/uploads/2024/02/3.png",
    "PROF_AbbeyGhana": f"{GH}/2026/05/ourstory.jpg",
    "PROF_Dunant0001": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Henry_Dunant-young.jpg/640px-Henry_Dunant-young.jpg",
    "PROF_Naismith01": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Dr._James_Naismith.jpg/640px-Dr._James_Naismith.jpg",
    "PROF_Addae00001": f"{GH}/2026/08/475298333_636645385695481_3264611505373035510_n.jpg",
    "PROF_JohnRMott1": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/John_Raleigh_Mott.jpg/640px-John_Raleigh_Mott.jpg",
    "PROF_Habiah0001": f"{GH}/2026/09/DSC03297-square-speaker.jpg",
    "PROF_WGMorgan01": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/William_G._Morgan.jpg/640px-William_G._Morgan.jpg",
    "PROF_AmoaAwuah1": "https://africaymca.org/wp-content/uploads/2021/10/council-1.jpg",
    "PROF_Amaning001": f"{GH}/2026/04/hostel_.png",
    "PROF_GyimahAkwa": f"{GH}/2026/08/WhatsApp-Image-2026-08-25-at-8.07.29-AM.jpeg",
}

PROGRAM_THUMBS = {
    "Digital Film School Africa": f"{GH}/2026/04/DFSABanner-1024x683.jpg",
    "Smart Girl Project": f"{GH}/2026/04/Smart-Girl-Cover--1024x683.jpg",
    "Youth Justice III": f"{GH}/2026/04/Youth-Justice-iii-cover-1024x683.jpg",
    "Green Ideas": f"{GH}/2026/04/Green-Ideas-cover-1024x683.jpg",
    "Moving Beyond": f"{GH}/2026/06/coverMoving-Beyond-1024x683.jpg",
    "Resilience Africa": f"{GH}/2026/06/Resilience-Africa-cover-1024x683.jpg",
}

NEWS_IMAGES = {
    "NEWS_ImpactAward1": f"{GH}/2026/08/WhatsApp-Image-2026-07-23-at-10.41.38-PM-1.jpeg",
    "NEWS_PresidentElc": f"{GH}/2026/08/WhatsApp-Image-2026-08-25-at-8.37.14-AM.jpeg",
    "NEWS_SmartGirl001": f"{GH}/2026/06/smart.jpg",
    "NEWS_YouthJustic1": f"{GH}/2026/04/Youth-Justice-iii.jpg",
    "NEWS_GreenIdeas01": f"{GH}/2026/06/green.jpg",
    "NEWS_Resilience01": f"{GH}/2026/06/Resilience-Africa-cover2.jpg",
    "NEWS_FilmSchool01": f"{GH}/2026/05/dfs-1024x683.jpg",
    "NEWS_EarthDay0001": f"{GH}/2025/07/mother.jpg",
}

EVENT_IMAGES = {
    "Youth Leadership Camp 2026": f"{GH}/2026/09/DSF3343-1024x567.jpg",
    "Community Outreach & Health Day": f"{GH}/2026/04/transform.jpeg",
    "New Member Orientation": f"{GH}/2026/08/WhatsApp-Image-2026-08-26-at-4.27.23-AM-2.jpeg",
}

SOCIAL_BY_CAPTION = {
    "Branch outreach today — serving with the team.": f"{GH}/2026/04/transform.jpeg",
    "Youth leadership camp was full of energy and new friendships.": f"{GH}/2026/09/DSF3343-1024x567.jpg",
    "Smart Girl session complete. Proud of these young leaders.": f"{GH}/2026/06/smart.jpg",
    "Green Ideas clean-up at the community park.": f"{GH}/2026/06/green.jpg",
}

EXTRA_NEWS = [
    {
        "id": "NEWS_BritishCoun1",
        "title": "Ghana YMCA Leadership Pays Courtesy Visit to British Council",
        "summary": "National President George Dela Coffie, Executive Director Kwabena Nketia Addae, and Programmes Director Samuel Asamoah visited the British Council in Accra.",
        "content": (
            "The National President of the Ghana YMCA, Mr. George Dela Coffie, together with the "
            "Executive Director, Mr. Kwabena Nketia Addae, and the National Programmes Director, "
            "Mr. Samuel Asamoah, paid a courtesy visit to the Country Director of the British Council, "
            "Mr. Nii Doodo Dodoo.\n\n"
            "The visit focused on strengthening collaboration and exploring opportunities for "
            "strategic partnership between Ghana YMCA and the British Council, particularly in "
            "areas that advance youth development and empowerment."
        ),
        "published_at": datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc),
        "is_impact_story": False,
        "image": f"{GH}/2026/09/CS1A0584-1024x683.jpg",
        "media_id": "MEDIA_BritishCoun1",
    },
    {
        "id": "NEWS_YouthConf001",
        "title": "Ghana YMCA Holds 23rd National Youth Conference in Takoradi",
        "summary": "Delegates from across Ghana met in Takoradi for the 23rd National Youth Conference, a week of leadership, fellowship, and service.",
        "content": (
            "Young people from branches across Ghana gathered in Takoradi for the 23rd National "
            "Youth Conference, a flagship gathering of fellowship, leadership formation, and service.\n\n"
            "Delegates took part in plenaries, workshops, worship, and community outreach. The "
            "conference renewed the movement’s call for youth to lead with integrity and to carry "
            "practical projects back to their regions."
        ),
        "published_at": datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc),
        "is_impact_story": True,
        "image": f"{GH}/2026/09/DSF3343-1024x567.jpg",
        "media_id": "MEDIA_YouthConf001",
    },
    {
        "id": "NEWS_CVJMInterns1",
        "title": "Ghana YMCA Welcomes Two Interns from CVJM Westbund",
        "summary": "Two interns from partner movement CVJM Westbund have arrived to serve with Ghana YMCA staff and branches.",
        "content": (
            "Ghana YMCA has welcomed two interns from long-standing partner CVJM Westbund. The "
            "interns will serve alongside staff and volunteers at national headquarters and selected branches.\n\n"
            "The exchange continues a partnership that has supported programmes such as Smart Girl "
            "and youth leadership development."
        ),
        "published_at": datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc),
        "is_impact_story": False,
        "image": f"{GH}/2026/08/WhatsApp-Image-2026-08-26-at-4.27.23-AM-2.jpeg",
        "media_id": "MEDIA_CVJMInterns1",
    },
    {
        "id": "NEWS_ClinicDonat1",
        "title": "Ghana YMCA Donates Medical Equipment to YMCA Clinic at Akpafu Odomi",
        "summary": "Ghana YMCA delivered medical equipment and supplies to the YMCA clinic at Akpafu Odomi to support community healthcare.",
        "content": (
            "Ghana YMCA has donated medical equipment and essential supplies to the YMCA clinic at "
            "Akpafu Odomi, strengthening healthcare access for families in the community.\n\n"
            "The donation is part of the Association’s long commitment to community wellbeing."
        ),
        "published_at": datetime(2025, 10, 8, 12, 0, tzinfo=timezone.utc),
        "is_impact_story": True,
        "image": f"{GH}/2025/09/558963013_1262604602573430_2295677114338709682_n-1024x536.jpg",
        "media_id": "MEDIA_ClinicDonat1",
    },
    {
        "id": "NEWS_NuhuFamily01",
        "title": "Ghana YMCA Has Given Me a Family I Can Rely On Forever — Nuhu",
        "summary": "Member Nuhu shares how Ghana YMCA became a family, offering belonging, mentoring, and a place to grow.",
        "content": (
            "Nuhu, a Ghana YMCA member, says the Association gave him a family he can rely on. "
            "Through branch life, mentoring, and programmes, he found belonging, skills, and people "
            "who walked with him through difficult seasons."
        ),
        "published_at": datetime(2025, 8, 20, 12, 0, tzinfo=timezone.utc),
        "is_impact_story": True,
        "image": f"{GH}/2020/08/672674096_1420527290114493_5055487864127650862_n-1024x768.jpg",
        "media_id": "MEDIA_NuhuFamily01",
    },
    {
        "id": "NEWS_FilmTour0001",
        "title": "Ghana YMCA Concludes Cross-Country Filmmaking Training Tour",
        "summary": "A cross-country filmmaking tour equipped young storytellers in communities across Ghana, ending with a certificate ceremony in Accra.",
        "content": (
            "Ghana YMCA has concluded a cross-country filmmaking training tour that took practical "
            "media education to young people beyond Accra.\n\n"
            "At the Accra certificate ceremony, Executive Director Kwabena Nketia Addae thanked "
            "partners for staying the course and said the project gave young filmmakers hope and "
            "skills they can use for work and peacebuilding."
        ),
        "published_at": datetime(2026, 5, 12, 12, 0, tzinfo=timezone.utc),
        "is_impact_story": True,
        "image": f"{GH}/2026/05/702893555_1452629283570960_7183772618461304906_n-1-1024x766.jpg",
        "media_id": "MEDIA_FilmTour0001",
    },
]


def _set_news_image(db, news_id: str, url: str) -> None:
    media = (
        db.query(NewsMedia)
        .filter(NewsMedia.news_id == news_id)
        .order_by(NewsMedia.order.asc())
        .first()
    )
    if media:
        media.url = url
        return
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        return
    NewsService(db)._add_media(
        news,
        [{"url": url, "media_type": MediaType.IMAGE, "order": 0}],
    )


def refresh() -> None:
    db = SessionLocal()
    try:
        profiles_updated = 0
        for profile_id, url in PROFILE_PHOTOS.items():
            profile = db.query(ProminentProfile).filter(ProminentProfile.id == profile_id).first()
            if not profile:
                continue
            profile.photo_url = url
            profiles_updated += 1
            print(f"Profile photo: {profile.full_name}")

        programs_updated = 0
        for title, url in PROGRAM_THUMBS.items():
            program = db.query(Program).filter(Program.title == title).first()
            if not program:
                continue
            program.thumbnail_url = url
            programs_updated += 1
            print(f"Program image: {title}")

        news_updated = 0
        for news_id, url in NEWS_IMAGES.items():
            if db.query(News).filter(News.id == news_id).first():
                _set_news_image(db, news_id, url)
                news_updated += 1
                print(f"News image: {news_id}")

        events_updated = 0
        for title, url in EVENT_IMAGES.items():
            event = db.query(News).filter(News.title == title).first()
            if not event:
                continue
            _set_news_image(db, event.id, url)
            events_updated += 1
            print(f"Event image: {title}")

        social_updated = 0
        for post in db.query(SocialPost).all():
            next_url = SOCIAL_BY_CAPTION.get(post.caption or "")
            if not next_url and "unsplash.com" in (post.media_url or ""):
                next_url = f"{GH}/2026/09/BJ6A6479-1024x683.jpg"
            if next_url and post.media_url != next_url:
                post.media_url = next_url
                social_updated += 1
                print(f"Social image: {post.id}")

        admin = db.query(User).filter(User.id == ADMIN_ID).first() or db.query(User).first()
        extra_created = 0
        if admin:
            for item in EXTRA_NEWS:
                existing = db.query(News).filter(News.id == item["id"]).first()
                if existing:
                    _set_news_image(db, existing.id, item["image"])
                    print(f"Extra news image: {item['id']}")
                    continue
                news = News(
                    id=item["id"],
                    admin_id=admin.id,
                    title=item["title"],
                    content=item["content"],
                    summary=item["summary"],
                    content_type=ContentType.NEWS,
                    is_impact_story=item["is_impact_story"],
                    is_published=True,
                    created_at=item["published_at"],
                    updated_at=item["published_at"],
                    published_at=item["published_at"],
                )
                news.media.append(
                    NewsMedia(
                        id=item["media_id"],
                        news_id=item["id"],
                        url=item["image"],
                        media_type=MediaType.IMAGE,
                        order=0,
                    )
                )
                db.add(news)
                extra_created += 1
                print(f"Created news: {item['title']}")

        db.commit()
        print(
            "Image refresh complete: "
            f"profiles={profiles_updated}, programs={programs_updated}, "
            f"news={news_updated}, events={events_updated}, "
            f"social={social_updated}, extra_news={extra_created}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    refresh()
