import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import settings
from core.branches.dto.request.branch_requests import BroadcastMessageRequest
from core.branches.dto.response.branch_responses import BroadcastMessageResponse
from core.branches.model.Branch import Branch
from core.branches.service.scope_helper import apply_member_scope, resolve_scope
from core.notification.model.Notification import Notification, NotificationStatus, NotificationType
from core.notification.service.notification_service import NotificationService
from core.user.model.User import User, UserType
from utilities.id_helper import generate_id

logger = logging.getLogger(__name__)


class MessageBroadcastService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def broadcast(self, request: BroadcastMessageRequest) -> BroadcastMessageResponse:
        if request.channel == "email" and not request.subject:
            raise HTTPException(status_code=400, detail="subject is required for email broadcasts")

        if request.scope == "users":
            user_ids = list(dict.fromkeys(request.user_ids or []))
            if not user_ids:
                raise HTTPException(status_code=400, detail="user_ids is required for user-targeted messages")

            query = self.db.query(User).filter(
                User.user_type == UserType.MEMBER,
                User.enabled.is_(True),
                User.id.in_(user_ids),
            )
            scope = "users"
        else:
            scope, region_id, branch_id = resolve_scope(request.scope, request.region_id, request.branch_id)

            if scope == "region" and not region_id:
                raise HTTPException(status_code=400, detail="region_id is required for regional broadcasts")
            if scope == "branch" and not branch_id:
                raise HTTPException(status_code=400, detail="branch_id is required for branch broadcasts")

            query = self.db.query(User).filter(
                User.user_type == UserType.MEMBER,
                User.enabled.is_(True),
            )
            query = apply_member_scope(query, self.db, scope, region_id, branch_id)

        if request.channel == "sms":
            query = query.filter(User.phone_number.isnot(None), User.phone_number != "")
        else:
            query = query.filter(User.email.isnot(None), User.email != "")

        recipients = query.all()
        sent_count = 0
        failed_count = 0

        for user in recipients:
            try:
                if request.channel == "sms":
                    self._send_sms(user, request.message)
                else:
                    self._send_email(user, request.subject or "YMCA Ghana", request.message)
                self._record_notification(user.id, request)
                sent_count += 1
            except Exception as exc:
                logger.error(f"Failed to send {request.channel} to user {user.id}: {exc}")
                failed_count += 1

        return BroadcastMessageResponse(
            channel=request.channel,
            scope=scope,
            recipients_total=len(recipients),
            sent_count=sent_count,
            failed_count=failed_count,
            message=f"Broadcast sent to {sent_count} of {len(recipients)} recipients",
        )

    def _send_sms(self, user: User, message: str) -> None:
        phone = user.phone_number
        if not phone:
            raise ValueError("No phone number")
        self.notification_service.create_notification(
            user_id=user.id,
            notification_type=NotificationType.INFO,
            data={"message": message[:160], "source": "admin_broadcast"},
            send_sms=True,
            sms_phone=phone,
        )

    def _send_email(self, user: User, subject: str, body: str) -> None:
        smtp_host = settings.ZEPTOMAIL_SMTP_HOST
        smtp_port = settings.ZEPTOMAIL_SMTP_PORT
        smtp_username = settings.ZEPTOMAIL_SMTP_USERNAME
        smtp_password = settings.ZEPTOMAIL_SMTP_PASSWORD
        sender_domain = getattr(settings, "ZEPTOMAIL_SENDER_DOMAIN", "ymcaghana.org")
        from_email = settings.ZEPTOMAIL_FROM_EMAIL or f"no-reply@{sender_domain}"

        if not smtp_password:
            raise ValueError("Email service not configured")

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = user.email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(from_email, user.email, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                server.sendmail(from_email, user.email, msg.as_string())

    def _record_notification(self, user_id: str, request: BroadcastMessageRequest) -> None:
        notification = Notification(
            id=generate_id(),
            user_id=user_id,
            type=NotificationType.INFO,
            data={
                "message": request.message,
                "channel": request.channel,
                "scope": request.scope,
                "source": "admin_broadcast",
            },
            status=NotificationStatus.UNREAD,
        )
        self.db.add(notification)
        self.db.commit()
