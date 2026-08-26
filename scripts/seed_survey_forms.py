"""Seed public survey/feedback forms for the member app."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

import utilities.dbmodels  # noqa: F401

from core.forms.model.Form import Form
from core.forms.service.formservice import FormService
from core.user.model.User import User, UserType
from utilities.dbconfig import SessionLocal

ADMIN_ID = "ymD3MaEjEkbOmtxv8fye"

SURVEYS = [
    {
        "title": "Annual Member Satisfaction Survey 2026",
        "description": "Help us improve programs, branches, and member services. Takes about 3 minutes.",
        "fields": [
            {
                "name": "overall_rating",
                "label": "How would you rate your overall YMCA experience?",
                "field_type": "radio",
                "required": True,
                "options": ["Excellent", "Good", "Fair", "Poor"],
            },
            {
                "name": "branch",
                "label": "Which branch do you visit most often?",
                "field_type": "select",
                "required": True,
                "options": [
                    "Accra",
                    "Kumasi",
                    "Takoradi",
                    "Tamale",
                    "Cape Coast",
                    "Other",
                ],
            },
            {
                "name": "programs_used",
                "label": "Which programs have you joined this year?",
                "field_type": "checkbox",
                "required": False,
                "options": [
                    "Youth leadership",
                    "Fitness / sports",
                    "Skills training",
                    "Community outreach",
                    "None yet",
                ],
            },
            {
                "name": "improve",
                "label": "What should we improve?",
                "field_type": "textarea",
                "required": True,
                "placeholder": "Share your suggestions",
            },
        ],
    },
    {
        "title": "New Fitness Center Equipment Feedback",
        "description": "Tell us how the new equipment is working for you.",
        "fields": [
            {
                "name": "used_new_equipment",
                "label": "Have you used the new fitness equipment?",
                "field_type": "radio",
                "required": True,
                "options": ["Yes", "Not yet"],
            },
            {
                "name": "condition",
                "label": "How would you rate the condition of the equipment?",
                "field_type": "radio",
                "required": True,
                "options": ["Excellent", "Good", "Needs attention"],
            },
            {
                "name": "comments",
                "label": "Anything else we should know?",
                "field_type": "textarea",
                "required": False,
                "placeholder": "Comments or requests",
            },
        ],
    },
    {
        "title": "Quick Feedback",
        "description": "Share a short note about your visit or a recent program.",
        "fields": [
            {
                "name": "rating",
                "label": "How was your experience today?",
                "field_type": "radio",
                "required": True,
                "options": ["5 — Excellent", "4 — Good", "3 — Okay", "2 — Poor", "1 — Very poor"],
            },
            {
                "name": "feedback",
                "label": "Tell us more",
                "field_type": "textarea",
                "required": True,
                "placeholder": "Comments, suggestions, or concerns",
            },
        ],
    },
]


def main():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == ADMIN_ID).first()
        if not admin:
            admin = (
                db.query(User)
                .filter(User.user_type == UserType.ADMIN)
                .order_by(User.created_at.asc())
                .first()
            )
        if not admin:
            raise SystemExit("No admin user found to own survey forms")

        service = FormService(db)
        created = 0
        for spec in SURVEYS:
            existing = db.query(Form).filter(Form.title == spec["title"]).first()
            if existing:
                print(f"Form exists: {spec['title']} ({existing.id})")
                continue
            form = service.create_form(
                admin_id=admin.id,
                title=spec["title"],
                description=spec["description"],
                assignment_type="PUBLIC",
                fields=spec["fields"],
                is_active=True,
            )
            created += 1
            print(f"Created survey: {form.title} ({form.id})")
        print(f"Survey seed complete. created={created}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
