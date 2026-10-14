from datetime import datetime, timezone
import calendar
import secrets
import string
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session, load_only
from fastapi import HTTPException, status
from core.notification.model.Notification import Notification, NotificationStatus, NotificationType
from core.user.model.User import User, UserStatus, UserType
from core.moolre.service.moolreservice import MoolreException
from core.sms.service.sms_factory import get_sms_service
from config import settings

# DTO Models
from core.notification.dto.response.notification_response import NotificationResponse
from core.notification.dto.response.paged_notifications import PagedNotificationResponse
from core.notification.dto.response.message_response import MessageResponse
import logging

logger = logging.getLogger(__name__)

_NOTIFICATION_CORE_COLUMNS = (
    Notification.id,
    Notification.user_id,
    Notification.type,
    Notification.data,
    Notification.status,
    Notification.created_at,
    Notification.read_at,
)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self._sms_service = None
        self.sms_enabled = getattr(settings, 'SMS_NOTIFICATION_ENABLED', True)

    @property
    def sms_service(self):
        if self._sms_service is None:
            self._sms_service = get_sms_service()
        return self._sms_service

    def _format_sms_message(self, notification_type: NotificationType, data: dict) -> str:
        """Format notification content for SMS based on type and data"""
        message_template = data.get('message', '')
        
        # If message is provided in data, use it
        if message_template:
            return message_template[:160]  # SMS length limit
        
        # Otherwise, create a default message based on notification type
        type_messages = {
            NotificationType.INFO: "Info: {content}",
            NotificationType.WARNING: "Warning: {content}",
            NotificationType.ERROR: "Error: {content}",
            NotificationType.SUCCESS: "Success: {content}",
            NotificationType.PROMOTIONAL: "Special Offer: {content}",
            NotificationType.TRANSACTIONAL: "Transaction Update: {content}",
            NotificationType.OTP: "Your verification code is: {otp}. Valid for {expiry} minutes.",
            NotificationType.ALERT: "Alert: {content}"
        }
        
        template = type_messages.get(notification_type, "{content}")
        
        # Replace placeholders with actual data
        content = data.get('content', 'You have a new notification')
        expiry = data.get('expiry_minutes', 5)
        otp = data.get('otp', '')
        
        message = template.format(
            content=content,
            expiry=expiry,
            otp=otp,
            **data
        )
        
        return message[:160]  # Ensure SMS length limit

    def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        data: dict,
        send_sms: bool = True,
        sms_phone: Optional[str] = None
    ) -> NotificationResponse:
        """Create a new notification for a user and optionally send SMS"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Determine SMS phone number (use provided or from user profile)
        sms_phone_to_use = sms_phone or getattr(user, 'phone_number', None) or getattr(user, 'phone', None)
        
        # Create notification record
        notification = Notification(
            id=self._generate_notification_id(),
            user_id=user_id,
            type=notification_type,
            data=data,
            status=NotificationStatus.UNREAD,
            sms_sent=False,
            sms_phone=sms_phone_to_use
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        # Send SMS if enabled and phone number available
        if send_sms and self.sms_enabled and sms_phone_to_use:
            try:
                self._send_sms_notification(notification.id, sms_phone_to_use, notification_type, data)
            except Exception as e:
                logger.error(f"Failed to send SMS for notification {notification.id}: {str(e)}")
                # Notification still created even if SMS fails

        return NotificationResponse.from_orm(notification)

    def _send_sms_notification(self, notification_id: str, phone: str, 
                               notification_type: NotificationType, data: dict) -> None:
        """Send SMS notification and update notification record"""
        try:
            # Format SMS message
            message = self._format_sms_message(notification_type, data)
            
            result = self.sms_service.send_sms(phone, message)
            
            # Update notification with SMS details
            notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
            if notification:
                notification.sms_sent = result.get('success', False)
                notification.sms_message_id = result.get('msgid')
                notification.sms_status = result.get('status')
                notification.sms_sent_at = datetime.now()
                
                if result.get('success'):
                    logger.info(f"SMS sent successfully for notification {notification_id}, msgid: {result.get('msgid')}")
                else:
                    notification.status = NotificationStatus.FAILED
                    logger.error(f"SMS failed for notification {notification_id}: {result.get('error')}")
                
                self.db.commit()
                
        except MoolreException as e:
            # Update notification with failure
            notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
            if notification:
                notification.sms_sent = False
                notification.sms_status = "FAILED"
                notification.status = NotificationStatus.FAILED
                self.db.commit()
            
            logger.error(f"SMS provider error for notification {notification_id}: {str(e)}")
            raise

    def send_bulk_sms_notifications(self, user_ids: List[str], message: str, 
                                    notification_type: NotificationType = NotificationType.INFO,
                                    data: Optional[dict] = None) -> Dict[str, Any]:
        """Send bulk SMS notifications to multiple users"""
        results = {
            "total": len(user_ids),
            "successful": 0,
            "failed": 0,
            "notifications": []
        }
        
        for user_id in user_ids:
            try:
                user = self.db.query(User).filter(User.id == user_id).first()
                phone = getattr(user, 'phone_number', None) or getattr(user, 'phone', None)
                if user and phone:
                    notification_data = data or {}
                    notification_data['message'] = message
                    
                    notification = self.create_notification(
                        user_id=user_id,
                        notification_type=notification_type,
                        data=notification_data,
                        send_sms=True,
                        sms_phone=phone
                    )
                    
                    results["successful"] += 1
                    results["notifications"].append(notification)
                else:
                    logger.warning(f"User {user_id} has no phone number, skipping SMS")
                    results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to send SMS to user {user_id}: {str(e)}")
                results["failed"] += 1
        
        return results

    def _create_in_app(
        self,
        user_id: str,
        notification_type: NotificationType,
        data: dict,
    ) -> Notification:
        notification = Notification(
            id=self._generate_notification_id(),
            user_id=user_id,
            type=notification_type,
            data=data,
            status=NotificationStatus.UNREAD,
            sms_sent=False,
        )
        self.db.add(notification)
        return notification

    def _has_source(self, user_id: str, source: str) -> bool:
        return (
            self.db.query(Notification.id)
            .filter(
                Notification.user_id == user_id,
                Notification.data["source"].astext == source,
            )
            .first()
            is not None
        )

    def notify_members_once(
        self,
        source: str,
        notification_type: NotificationType,
        data: dict,
    ) -> int:
        """Store one in-app notice per active member. Skip anyone who already has this source."""
        payload = {**data, "source": source}
        already = {
            row[0]
            for row in self.db.query(Notification.user_id)
            .filter(Notification.data["source"].astext == source)
            .all()
        }
        members = (
            self.db.query(User.id)
            .filter(
                User.user_type == UserType.MEMBER,
                User.enabled.is_(True),
                User.status == UserStatus.ACTIVE,
            )
            .all()
        )
        created = 0
        for (user_id,) in members:
            if user_id in already:
                continue
            self._create_in_app(user_id, notification_type, payload)
            created += 1
        if created:
            self.db.commit()
        return created

    def notify_news_published(self, news_id: str, title: str, summary: Optional[str]) -> int:
        message = (summary or "").strip() or "A new update was published."
        if len(message) > 240:
            message = message[:237].rstrip() + "..."
        return self.notify_members_once(
            source=f"news:{news_id}",
            notification_type=NotificationType.INFO,
            data={
                "title": (title or "News update")[:255],
                "message": message,
                "news_id": news_id,
            },
        )

    def ensure_monthly_payment_notice(self, user_id: str) -> None:
        """Create this month's dues notice once, when the member still owes it."""
        now = datetime.now(timezone.utc)
        source = f"monthly_dues:{now.year:04d}-{now.month:02d}"
        if self._has_source(user_id, source):
            return

        user = self.db.query(User).filter(User.id == user_id).first()
        if (
            not user
            or user.user_type != UserType.MEMBER
            or not user.enabled
            or user.status == UserStatus.DELETED
        ):
            return

        from core.payments.service.payment_service import PaymentService

        payments = PaymentService(self.db)
        if not payments._branch_collects_dues(user):
            return
        if (now.year, now.month) < payments._join_period(user):
            return
        if payments._successful_period_payment(user.id, now.year, now.month):
            return

        label = f"{calendar.month_name[now.month]} {now.year}"
        amount = float(settings.MONTHLY_DUES_AMOUNT_GHS or 0)
        self._create_in_app(
            user.id,
            NotificationType.TRANSACTIONAL,
            {
                "title": f"{label} payment due",
                "message": f"Your {label} membership payment of GH₵ {amount:.2f} is due.",
                "source": source,
                "period": f"{now.year:04d}-{now.month:02d}",
            },
        )
        self.db.commit()

    def _ensure_monthly_payment_notice(self, user_id: str) -> None:
        try:
            self.ensure_monthly_payment_notice(user_id)
        except Exception:
            logger.exception("Could not create monthly payment notice for %s", user_id)
            self.db.rollback()

    def get_notification(self, notification_id: str) -> NotificationResponse:
        """Get a specific notification by ID"""
        notification = (
            self.db.query(Notification)
            .options(load_only(*_NOTIFICATION_CORE_COLUMNS))
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return NotificationResponse.from_orm(notification)

    def get_user_notifications_paged(
        self,
        user_id: str,
        page: int,
        size: int,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None
    ) -> PagedNotificationResponse:
        """Get paginated notifications for a user with optional filters"""
        self._ensure_monthly_payment_notice(user_id)
        query = (
            self.db.query(Notification)
            .options(load_only(*_NOTIFICATION_CORE_COLUMNS))
            .filter(Notification.user_id == user_id)
        )

        if status:
            query = query.filter(Notification.status == status)
        if notification_type:
            query = query.filter(Notification.type == notification_type)

        total = query.count()
        notifications = query.order_by(Notification.created_at.desc()) \
                           .offset((page - 1) * size) \
                           .limit(size) \
                           .all()

        return PagedNotificationResponse(
            items=[NotificationResponse.from_orm(n) for n in notifications],
            total=total,
            page=page,
            size=size,
        )

    def count_unread(self, user_id: str) -> int:
        self._ensure_monthly_payment_notice(user_id)
        # COUNT(id) avoids selecting mapped SMS columns that older DBs may lack.
        return (
            self.db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .filter(Notification.status == NotificationStatus.UNREAD)
            .scalar()
            or 0
        )

    def update_notification(
        self,
        notification_id: str,
        status: Optional[NotificationStatus] = None,
        data: Optional[dict] = None
    ) -> NotificationResponse:
        """Update a notification's status and/or data"""
        notification = (
            self.db.query(Notification)
            .options(load_only(*_NOTIFICATION_CORE_COLUMNS))
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if status is not None:
            notification.status = status
            if status == NotificationStatus.READ and notification.read_at is None:
                notification.read_at = datetime.now()

        if data is not None:
            notification.data = data

        self.db.commit()
        return NotificationResponse.from_orm(notification)

    def mark_notification_as_read(self, notification_id: str) -> NotificationResponse:
        """Mark a specific notification as read"""
        return self.update_notification(
            notification_id=notification_id,
            status=NotificationStatus.READ
        )

    def mark_all_notifications_as_read(self, user_id: str) -> MessageResponse:
        """Mark all unread notifications for a user as read"""
        self.db.query(Notification) \
             .filter(Notification.user_id == user_id) \
             .filter(Notification.status == NotificationStatus.UNREAD) \
             .update({
                 Notification.status: NotificationStatus.READ,
                 Notification.read_at: datetime.now()
             }, synchronize_session=False)
        
        self.db.commit()
        return MessageResponse(message="All notifications marked as read")

    def delete_notification(self, notification_id: str) -> None:
        """Delete a notification"""
        notification = (
            self.db.query(Notification)
            .options(load_only(*_NOTIFICATION_CORE_COLUMNS))
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        self.db.delete(notification)
        self.db.commit()
    
    def check_sms_delivery_status(self, notification_id: str) -> Dict[str, Any]:
        """Check SMS delivery status for a notification"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if not notification.sms_message_id:
            return {
                "notification_id": notification_id,
                "sms_sent": notification.sms_sent,
                "message": "No SMS was sent for this notification"
            }
        
        try:
            status_result = self.sms_service.check_message_status(notification.sms_message_id)
            
            # Update notification with delivery status
            if status_result.get('success'):
                notification.sms_delivery_status = status_result.get('status')
                if status_result.get('status') == 'DLV':  # Delivered
                    notification.sms_delivered_at = datetime.now()
                    notification.status = NotificationStatus.DELIVERED
                self.db.commit()
            
            return {
                "notification_id": notification_id,
                "sms_message_id": notification.sms_message_id,
                "delivery_status": status_result,
                "current_status": notification.sms_delivery_status
            }
            
        except Exception as e:
            logger.error(f"Failed to check SMS status for {notification_id}: {str(e)}")
            return {
                "notification_id": notification_id,
                "error": str(e)
            }
    
    def _generate_notification_id(self) -> str:
        """Generate a unique notification ID"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(16))