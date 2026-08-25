from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from core.notification.model.Notification import NotificationStatus, NotificationType


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    data: Dict[str, Any] = Field(default_factory=dict)
    status: NotificationStatus
    created_at: datetime
    read_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    sms_sent: bool = False
    sms_phone: Optional[str] = None
    sms_message_id: Optional[str] = None
    sms_status: Optional[str] = None
    sms_delivery_status: Optional[str] = None
    sms_sent_at: Optional[datetime] = None
    sms_delivered_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

    @classmethod
    def from_orm(cls, notification):
        loaded = getattr(notification, "__dict__", {}) or {}
        data = loaded.get("data", getattr(notification, "data", None))
        if not isinstance(data, dict):
            data = {}

        created_at = loaded.get("created_at") or notification.created_at

        return cls(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            data=data,
            status=notification.status,
            created_at=created_at,
            read_at=loaded.get("read_at"),
            updated_at=loaded.get("updated_at") or created_at,
            sms_sent=bool(loaded.get("sms_sent", False)),
            sms_phone=loaded.get("sms_phone"),
            sms_message_id=loaded.get("sms_message_id"),
            sms_status=loaded.get("sms_status"),
            sms_delivery_status=loaded.get("sms_delivery_status"),
            sms_sent_at=loaded.get("sms_sent_at"),
            sms_delivered_at=loaded.get("sms_delivered_at"),
        )
