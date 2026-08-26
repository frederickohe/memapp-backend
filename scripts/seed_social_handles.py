"""Fill blank member social handles so Y Social profiles can be messaged."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

import utilities.dbmodels  # noqa: F401

from core.user.model.User import User, UserType
from utilities.dbconfig import SessionLocal


def main():
    db = SessionLocal()
    try:
        members = db.query(User).filter(User.user_type == UserType.MEMBER).all()
        updated = 0
        for user in members:
            if user.whatsapp_number or not user.phone_number:
                continue
            user.whatsapp_number = user.phone_number[:20]
            updated += 1
            print(f"Set WhatsApp for {user.fullname} from phone")
        db.commit()
        print(f"Social handle seed complete. updated={updated}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
