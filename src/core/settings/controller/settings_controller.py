from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.auth.dependencies import get_db
from core.rbac.dependencies import require_permission
from core.settings.service.settings_service import SettingsService
from core.user.model.User import User

public_app_routes = APIRouter()
settings_admin_routes = APIRouter()


class UpdateSettingRequest(BaseModel):
    value: str = ""


@public_app_routes.get("/app/config")
def get_public_app_config(db: Session = Depends(get_db)):
    """Public app content used before a member signs in."""
    return SettingsService(db).public_config()


@settings_admin_routes.get("/settings")
def list_settings(
    _: User = Depends(require_permission("settings.view")),
    db: Session = Depends(get_db),
):
    return {"data": SettingsService(db).list_settings()}


@settings_admin_routes.put("/settings/{key}")
def update_setting(
    key: str,
    request: UpdateSettingRequest,
    _: User = Depends(require_permission("settings.update")),
    db: Session = Depends(get_db),
):
    return {"data": SettingsService(db).update_setting(key, request.value)}
