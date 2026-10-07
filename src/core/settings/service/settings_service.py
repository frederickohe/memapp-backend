from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.settings.model.system_setting import SystemSetting
from core.settings.youtube import canonical_youtube_url

SIGNUP_YOUTUBE_URL_KEY = "signup_youtube_url"
DEFAULT_SIGNUP_YOUTUBE_URL = "https://www.youtube.com/watch?v=6YM8SreJVLQ"

SETTING_CATALOGUE: Dict[str, Dict[str, str]] = {
    SIGNUP_YOUTUBE_URL_KEY: {
        "description": "YouTube video shown on the member app sign-up screens",
        "default": DEFAULT_SIGNUP_YOUTUBE_URL,
    }
}


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def ensure_defaults(self) -> None:
        keys = list(SETTING_CATALOGUE)
        existing = {
            row.key
            for row in self.db.query(SystemSetting)
            .filter(SystemSetting.key.in_(keys))
            .all()
        }
        created = False
        for key, meta in SETTING_CATALOGUE.items():
            if key in existing:
                continue
            self.db.add(
                SystemSetting(
                    key=key,
                    value=meta["default"],
                    description=meta["description"],
                )
            )
            created = True
        if created:
            self.db.commit()

    def _row(self, key: str) -> Optional[SystemSetting]:
        return self.db.query(SystemSetting).filter(SystemSetting.key == key).first()

    def _serialize(self, key: str, row: Optional[SystemSetting]) -> dict:
        meta = SETTING_CATALOGUE[key]
        updated_at = row.updated_at.isoformat() if row and row.updated_at else None
        return {
            "key": key,
            "value": row.value if row is not None else meta["default"],
            "description": meta["description"],
            "allowed_values": None,
            "updated_at": updated_at,
        }

    def list_settings(self) -> List[dict]:
        self.ensure_defaults()
        return [self._serialize(key, self._row(key)) for key in SETTING_CATALOGUE]

    def public_config(self) -> dict:
        try:
            self.ensure_defaults()
            row = self._row(SIGNUP_YOUTUBE_URL_KEY)
            value = row.value if row is not None else DEFAULT_SIGNUP_YOUTUBE_URL
        except SQLAlchemyError:
            self.db.rollback()
            value = DEFAULT_SIGNUP_YOUTUBE_URL
        return {"signup_youtube_url": value or ""}

    def update_setting(self, key: str, value: str) -> dict:
        if key not in SETTING_CATALOGUE:
            raise HTTPException(status_code=404, detail="Setting not found")

        self.ensure_defaults()
        if key == SIGNUP_YOUTUBE_URL_KEY:
            try:
                stored = canonical_youtube_url(value)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
        else:
            stored = (value or "").strip()

        row = self._row(key)
        if row is None:
            row = SystemSetting(
                key=key,
                value=stored,
                description=SETTING_CATALOGUE[key]["description"],
            )
            self.db.add(row)
        else:
            row.value = stored
            row.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(row)
        return {"key": row.key, "value": row.value}
