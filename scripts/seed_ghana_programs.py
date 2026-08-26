"""Seed Ghana YMCA programs, application forms, and upcoming events."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

import utilities.dbmodels  # noqa: F401  load all SQLAlchemy mappers

from datetime import datetime, timezone

from core.forms.model.Form import Form
from core.forms.service.formservice import FormService
from core.news.model.News import ContentType, MediaType
from core.news.service.newsservice import NewsService
from core.programs.model.program import Program
from core.programs.service.programservice import ProgramService
from core.user.model.User import User
from utilities.dbconfig import SessionLocal

ADMIN_ID = "ymD3MaEjEkbOmtxv8fye"

COMMON_FIELDS = [
    {
        "name": "full_name",
        "label": "Full name",
        "field_type": "text",
        "required": True,
        "placeholder": "Your full name",
    },
    {
        "name": "email",
        "label": "Email",
        "field_type": "email",
        "required": True,
        "placeholder": "you@example.com",
    },
    {
        "name": "phone",
        "label": "Phone number",
        "field_type": "text",
        "required": True,
        "placeholder": "+233...",
    },
    {
        "name": "date_of_birth",
        "label": "Date of birth",
        "field_type": "date",
        "required": True,
    },
    {
        "name": "gender",
        "label": "Gender",
        "field_type": "select",
        "required": True,
        "options": ["Female", "Male", "Other"],
    },
    {
        "name": "region",
        "label": "Region",
        "field_type": "select",
        "required": True,
        "options": [
            "Greater Accra",
            "Ashanti",
            "Eastern",
            "Western",
            "Central",
            "Northern",
            "Volta",
            "Other",
        ],
    },
    {
        "name": "why_join",
        "label": "Why do you want to join this program?",
        "field_type": "textarea",
        "required": True,
        "placeholder": "Tell us about your interest and goals",
    },
    {
        "name": "consent",
        "label": "I agree to be contacted by Ghana YMCA about this application",
        "field_type": "checkbox",
        "required": True,
    },
]

FORMS = [
    {
        "key": "general",
        "title": "Program Application Form",
        "description": "Apply to join a Ghana YMCA program. Complete all required fields.",
        "extra_fields": [],
    },
    {
        "key": "film",
        "title": "Digital Film School Africa Application",
        "description": "Apply for Digital Film School Africa, a digital-first film education programme co-hosted by YMCA Ghana.",
        "extra_fields": [
            {
                "name": "experience_level",
                "label": "Filmmaking experience",
                "field_type": "select",
                "required": True,
                "options": ["Beginner", "Intermediate", "Advanced"],
            },
            {
                "name": "portfolio_url",
                "label": "Portfolio or sample work URL",
                "field_type": "text",
                "required": False,
                "placeholder": "https://",
            },
        ],
    },
    {
        "key": "smart_girl",
        "title": "Smart Girl Project Application",
        "description": "Apply to participate in or support the Smart Girl menstrual health and leadership programme.",
        "extra_fields": [
            {
                "name": "community",
                "label": "Community / school",
                "field_type": "text",
                "required": True,
            },
            {
                "name": "role",
                "label": "How would you like to take part?",
                "field_type": "select",
                "required": True,
                "options": ["Participant", "Mentor", "Volunteer"],
            },
        ],
    },
]

PROGRAMS = [
    {
        "title": "Digital Film School Africa",
        "form_key": "film",
        "category": "Education",
        "location": "Accra · Online",
        "thumbnail_url": "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=1400&q=80",
        "description": (
            "Digital Film School Africa is a digital-first film education programme co-hosted by "
            "YMCA Ghana and the African University of Communications and Business (AUCB), in "
            "partnership with WELTFILME e.V. and funded by GIZ/BMZ.\n\n"
            "Each year an open call is announced across community radio, notice boards, and online "
            "spaces. Interested applicants complete this form to express interest. Once admitted, "
            "students register on the Atingi platform where courses are hosted."
        ),
        "starting_date": datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
        "end_date": datetime(2026, 12, 15, 17, 0, tzinfo=timezone.utc),
    },
    {
        "title": "Smart Girl Project",
        "form_key": "smart_girl",
        "category": "Youth",
        "location": "Communities across Ghana",
        "thumbnail_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1400&q=80",
        "description": (
            "Smart Girl Project expands access to menstrual health education and life skills "
            "training for girls across communities. The programme provides practical learning in "
            "confidence building, leadership development, and personal hygiene.\n\n"
            "It connects mentors and learners through community sessions and school outreach, "
            "helping girls grow, stay informed, and reach their full potential."
        ),
        "starting_date": datetime(2026, 2, 1, 9, 0, tzinfo=timezone.utc),
        "end_date": datetime(2027, 1, 31, 17, 0, tzinfo=timezone.utc),
    },
    {
        "title": "Youth Justice III",
        "form_key": "general",
        "category": "Justice",
        "location": "National · Ghana",
        "thumbnail_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1400&q=80",
        "description": (
            "Youth Justice III promotes fairness, protection, and equal opportunities for young "
            "people through advocacy, inclusive education, legal awareness, and community-driven "
            "support systems that help youth thrive and access justice."
        ),
        "starting_date": datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc),
        "end_date": datetime(2026, 11, 30, 17, 0, tzinfo=timezone.utc),
    },
    {
        "title": "Green Ideas",
        "form_key": "general",
        "category": "Environment",
        "location": "Ghana YMCA branches",
        "thumbnail_url": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=80",
        "description": (
            "Green Ideas provides science-based climate change education, promotes environmental "
            "sustainability and eco-friendly practices, and empowers young people to take "
            "community action on climate and conservation."
        ),
        "starting_date": datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc),
        "end_date": datetime(2026, 10, 31, 17, 0, tzinfo=timezone.utc),
    },
    {
        "title": "Moving Beyond",
        "form_key": "film",
        "category": "Education",
        "location": "Accra",
        "thumbnail_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1400&q=80",
        "description": (
            "Moving Beyond develops young filmmakers through specialized training, mentorship, "
            "and creative storytelling, creating pathways to meaningful careers and positive "
            "social impact through film and media."
        ),
        "starting_date": datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
        "end_date": datetime(2026, 12, 20, 17, 0, tzinfo=timezone.utc),
    },
    {
        "title": "Resilience Africa",
        "form_key": "film",
        "category": "Education",
        "location": "Accra · National",
        "thumbnail_url": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=1400&q=80",
        "description": (
            "The Resilience Africa Film Project provides practical filmmaking training while "
            "empowering young storytellers to build creative skills, confidence, and meaningful "
            "career pathways in the film industry. The programme promotes peacebuilding, social "
            "cohesion, and sustainable livelihoods."
        ),
        "starting_date": datetime(2025, 9, 1, 9, 0, tzinfo=timezone.utc),
        "end_date": datetime(2026, 12, 31, 17, 0, tzinfo=timezone.utc),
    },
]

EVENTS = [
    {
        "title": "Youth Leadership Camp 2026",
        "summary": "A weekend of leadership, service, and community building for Ghana YMCA members.",
        "content": (
            "Join young people from branches across Ghana for a weekend of leadership training, "
            "team challenges, and community service. Participants will work with mentors, practise "
            "public speaking, and plan local impact projects to take back to their branches."
        ),
        "event_date": datetime(2026, 9, 12, 8, 0, tzinfo=timezone.utc),
        "event_location": "YMCA National Headquarters, Accra",
        "image": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1400&q=80",
    },
    {
        "title": "Community Outreach & Health Day",
        "summary": "Free health checks, games, and family activities hosted with local partners.",
        "content": (
            "Ghana YMCA branches will host an outreach day with health screenings, sports, and "
            "family activities. Volunteers are welcome to support registration, games, and "
            "hospitality throughout the day."
        ),
        "event_date": datetime(2026, 10, 4, 9, 0, tzinfo=timezone.utc),
        "event_location": "Selected YMCA branches nationwide",
        "image": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=1400&q=80",
    },
    {
        "title": "New Member Orientation",
        "summary": "Meet your branch, learn how programs work, and get connected with mentors.",
        "content": (
            "This orientation introduces new members to Ghana YMCA programs, volunteer "
            "opportunities, and branch life. Come ready to meet other members and ask questions "
            "about how to get involved."
        ),
        "event_date": datetime(2026, 9, 20, 14, 0, tzinfo=timezone.utc),
        "event_location": "YMCA National Headquarters, Accra",
        "image": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&w=1400&q=80",
    },
]


def ensure_admin(db) -> str:
    admin = db.query(User).filter(User.id == ADMIN_ID).first()
    if admin:
        return admin.id
    admin = db.query(User).filter(User.user_type == "ADMIN").first()
    if not admin:
        raise SystemExit("No admin user found to own seeded programs")
    return admin.id


def main() -> None:
    db = SessionLocal()
    try:
        admin_id = ensure_admin(db)
        form_service = FormService(db)
        program_service = ProgramService(db)
        news_service = NewsService(db)

        form_ids = {}
        for spec in FORMS:
            existing = db.query(Form).filter(Form.title == spec["title"]).first()
            if existing:
                form_ids[spec["key"]] = existing.id
                print(f"Form exists: {spec['title']} ({existing.id})")
                continue
            created = form_service.create_form(
                admin_id=admin_id,
                title=spec["title"],
                description=spec["description"],
                assignment_type="PROGRAM",
                fields=COMMON_FIELDS + spec["extra_fields"],
                is_active=True,
            )
            form_ids[spec["key"]] = created.id
            print(f"Created form: {created.title} ({created.id})")

        for spec in PROGRAMS:
            existing = db.query(Program).filter(Program.title == spec["title"]).first()
            if existing:
                print(f"Program exists: {spec['title']} ({existing.id})")
                continue
            form_id = form_ids[spec["form_key"]]
            created = program_service.create_program(
                created_by=admin_id,
                title=spec["title"],
                description=spec["description"],
                starting_date=spec["starting_date"],
                end_date=spec["end_date"],
                thumbnail_url=spec["thumbnail_url"],
                category=spec["category"],
                location=spec["location"],
                form_ids=[form_id],
                is_published=True,
                allow_registration=True,
                metadata={
                    "actions": [
                        {
                            "label": "Apply now",
                            "type": "form",
                            "form_id": form_id,
                        }
                    ]
                },
            )
            print(f"Created program: {created.title} ({created.id})")

        from core.news.model.News import News

        for spec in EVENTS:
            existing = db.query(News).filter(News.title == spec["title"]).first()
            if existing:
                print(f"Event exists: {spec['title']} ({existing.id})")
                continue
            created = news_service.create_news(
                admin_id=admin_id,
                title=spec["title"],
                content=spec["content"],
                summary=spec["summary"],
                content_type=ContentType.EVENT,
                event_date=spec["event_date"],
                event_location=spec["event_location"],
                is_published=True,
                media_list=[{"url": spec["image"], "media_type": MediaType.IMAGE, "order": 0}],
            )
            print(f"Created event: {created.title} ({created.id})")

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
