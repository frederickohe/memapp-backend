
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import secrets
from core.auth.service.sessiondriver import SessionDriver, TokenData
from fastapi_jwt_auth import AuthJWT
from core.exceptions import *
from utilities.dbconfig import SessionLocal
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session
from core.auth.model.password_reset_token import PasswordResetToken
from core.auth.model.refreshtoken import RefreshToken
from core.branches.model.Branch import Branch
from core.forms.model.Form import Form, FormResponse
from core.histories.model.history import History
from core.notification.model.Notification import Notification
from core.otp.model.otp import OTP
from core.payments.model.Payment import Payment
from core.paystack.model.paystack_session import PaystackSession
from core.programs.model.program import program_participants_association
from core.social.model.social import SocialLike, SocialPost, SocialView
from core.user.model.User import User, UserStatus, UserType
from core.vhs.model.volunteer_hours_submission import VolunteerHoursSubmission
import logging

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# DTO Models
from core.user.dto.request.user_filter_request import UserFilterRequest
from core.user.dto.response.message_response import MessageResponse
from core.user.dto.response.user_response import UserResponse
from core.user.dto.request.user_update_request import UserUpdateRequest
from core.user.service.membership_helpers import resolve_branch, resolve_position

def connected_user_ids(value):
    if not value:
        return None
    if not isinstance(value, list):
        return None
    ids = []
    for item in value:
        if isinstance(item, str) and item:
            ids.append(item)
        elif hasattr(item, "id") and item.id:
            ids.append(item.id)
    return ids or None


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _branch_collects_dues(self, user: User) -> bool:
        if not user.branch_id:
            return True
        branch = user.branch
        if branch is None:
            branch = self.db.query(Branch).filter(Branch.id == user.branch_id).first()
        if branch is None:
            return True
        return bool(branch.collects_dues)

    def _to_response(self, user: User) -> UserResponse:
        collects_dues = self._branch_collects_dues(user)
        return UserResponse(
            id=user.id,
            fullname=user.fullname,
            email=user.email,
            phone_number=user.phone_number,
            nationality=user.nationality,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            address=user.address,
            profile_picture_url=user.profile_picture_url,
            membership_type=user.membership_type,
            current_branch=user.current_branch,
            branch_id=user.branch_id,
            branch_collects_dues=collects_dues,
            member_id=user.member_id,
            date_joined_organization=user.date_joined_organization,
            past_positions=user.past_positions,
            role_id=user.role_id,
            role=user.role,
            position=resolve_position(self.db, user),
            volunteer_points=user.volunteer_points or 0,
            month_dues_paid_status="NOT_REQUIRED" if not collects_dues else user.month_dues_paid_status,
            year_affiliation_paid_status=user.year_affiliation_paid_status,
            occupation=user.occupation,
            organization_workplace=user.organization_workplace,
            skills=user.skills,
            experiences=user.experiences,
            connected_users=connected_user_ids(user.connected_users),
            facebook_url=user.facebook_url,
            whatsapp_number=user.whatsapp_number,
            linkedin_url=user.linkedin_url,
            twitter_url=user.twitter_url,
            instagram_url=user.instagram_url,
            profile_sharing=user.profile_sharing,
            in_app_notification=user.in_app_notification,
            sms_notification=user.sms_notification,
            enabled=user.enabled,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def get_current_user(self, identifier: str) -> UserResponse:
        # Try to find by email first, then by id as a fallback.
        user = self.db.query(User).filter(User.email == identifier).first()
        if not user:
            user = (
                self.db.query(User)
                .filter(User.email.ilike(identifier))
                .first()
            )
        if not user:
            user = self.db.query(User).filter(User.id == identifier).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self._refresh_dues_flags(user)
        return self._to_response(user)

    def _refresh_dues_flags(self, user: User) -> None:
        from core.payments.service.payment_service import PaymentService

        PaymentService(self.db)._sync_member_flags(user)
        self.db.commit()

    def get_user_by_id(self, user_id: str) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_response(user)

    # get user by phone number
    def get_user_by_phone(self, phone_number: str) -> UserResponse:
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_response(user)
    
    def set_user_enabled_status(self, user_id: str, enabled: bool) -> MessageResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.enabled = enabled
        self.db.commit()
        status_msg = "enabled" if enabled else "disabled"
        return MessageResponse(message=f"User {status_msg} successfully")

    def delete_user(self, user_id: str) -> MessageResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.db.delete(user)
        self.db.commit()
        return MessageResponse(message="User deleted successfully")

    def _find_user(self, identifier: str) -> User:
        user = self.db.query(User).filter(User.email == identifier).first()
        if not user:
            user = self.db.query(User).filter(User.email.ilike(identifier)).first()
        if not user:
            user = self.db.query(User).filter(User.id == identifier).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def delete_own_account(self, identifier: str) -> MessageResponse:
        """Permanently close the signed-in account and remove personal data.

        Payment, receipt, and volunteer-hour approval rows stay attached to an
        anonymised id so legal and audit records are not destroyed.
        """
        user = self._find_user(identifier)
        if user.status == UserStatus.DELETED:
            raise HTTPException(status_code=400, detail="Account is already deleted")

        original_email = user.email
        try:
            self._purge_personal_data(user)
            self._anonymize_account(user)
            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            logger.exception("Failed to delete account %s", user.id)
            raise HTTPException(status_code=500, detail="Unable to delete account")

        self._revoke_sessions(original_email)
        return MessageResponse(message="Account deleted successfully")

    def _purge_personal_data(self, user: User) -> None:
        post_ids = [
            row[0]
            for row in self.db.query(SocialPost.id).filter(SocialPost.user_id == user.id).all()
        ]
        if post_ids:
            self.db.query(SocialLike).filter(
                SocialLike.target_type == "POST",
                SocialLike.target_id.in_(post_ids),
            ).delete(synchronize_session=False)
            self.db.query(SocialView).filter(
                SocialView.target_type == "POST",
                SocialView.target_id.in_(post_ids),
            ).delete(synchronize_session=False)

        self.db.query(SocialLike).filter(SocialLike.user_id == user.id).delete(synchronize_session=False)
        self.db.query(SocialView).filter(SocialView.user_id == user.id).delete(synchronize_session=False)
        self.db.query(SocialPost).filter(SocialPost.user_id == user.id).delete(synchronize_session=False)
        self.db.query(Notification).filter(Notification.user_id == user.id).delete(synchronize_session=False)
        self.db.query(FormResponse).filter(FormResponse.user_id == user.id).delete(synchronize_session=False)
        self.db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete(synchronize_session=False)
        self.db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete(synchronize_session=False)
        self.db.execute(
            program_participants_association.delete().where(
                program_participants_association.c.user_id == user.id
            )
        )
        self.db.query(Form).filter(Form.assigned_user_id == user.id).update(
            {Form.assigned_user_id: None},
            synchronize_session=False,
        )
        self.db.query(Branch).filter(Branch.president_id == user.id).update(
            {Branch.president_id: None},
            synchronize_session=False,
        )
        self.db.query(VolunteerHoursSubmission).filter(
            VolunteerHoursSubmission.reviewed_by == user.id
        ).update(
            {VolunteerHoursSubmission.reviewed_by: None},
            synchronize_session=False,
        )
        self.db.query(VolunteerHoursSubmission).filter(
            VolunteerHoursSubmission.user_id == user.id
        ).update(
            {
                VolunteerHoursSubmission.activity_description: None,
                VolunteerHoursSubmission.proof_document_url: None,
            },
            synchronize_session=False,
        )
        self.db.query(PaystackSession).filter(PaystackSession.user_id == user.id).update(
            {
                PaystackSession.email: f"deleted-{user.id}@deleted.invalid",
                PaystackSession.access_code: None,
                PaystackSession.transaction_metadata: None,
            },
            synchronize_session=False,
        )
        self.db.query(Payment).filter(Payment.user_id == user.id).update(
            {Payment.payment_metadata: None},
            synchronize_session=False,
        )
        self.db.query(History).filter(History.user_id == user.id).update(
            {
                History.phone_number: None,
                History.recipient: None,
                History.description: None,
                History.transaction_metadata: None,
            },
            synchronize_session=False,
        )

        otp_filters = []
        if user.email:
            otp_filters.append(OTP.email.ilike(user.email))
        if user.phone_number:
            otp_filters.append(OTP.phone == user.phone_number)
        if otp_filters:
            self.db.query(OTP).filter(or_(*otp_filters)).delete(synchronize_session=False)

        linked = (
            self.db.query(User)
            .filter(User.id != user.id)
            .filter(cast(User.connected_users, String).like(f"%{user.id}%"))
            .all()
        )
        for other in linked:
            ids = other.connected_users if isinstance(other.connected_users, list) else []
            other.connected_users = [
                item for item in ids
                if item != user.id and not (isinstance(item, dict) and item.get("id") == user.id)
            ]

    def _anonymize_account(self, user: User) -> None:
        user.fullname = "Deleted user"
        user.email = f"deleted-{user.id}@deleted.invalid"
        user.phone_number = None
        user.hashed_password = _password_context.hash(secrets.token_urlsafe(32))
        user.nationality = None
        user.date_of_birth = None
        user.gender = None
        user.address = None
        user.profile_picture_url = None
        user.membership_type = None
        user.current_branch = None
        user.branch_id = None
        user.member_id = None
        user.date_joined_organization = None
        user.past_positions = None
        user.volunteer_points = 0
        user.occupation = None
        user.organization_workplace = None
        user.skills = None
        user.experiences = None
        user.connected_users = None
        user.facebook_url = None
        user.whatsapp_number = None
        user.linkedin_url = None
        user.twitter_url = None
        user.instagram_url = None
        user.is_prominent = False
        user.prominent_order = 0
        user.prominent_headline = None
        user.profile_sharing = False
        user.in_app_notification = False
        user.sms_notification = False
        user.user_type = UserType.MEMBER
        user.role = None
        user.role_id = None
        user.assigned_region = None
        user.assigned_branch = None
        user.assigned_region_id = None
        user.assigned_branch_id = None
        user.enabled = False
        user.status = UserStatus.DELETED
        user.updated_at = datetime.utcnow()

    def _revoke_sessions(self, email: Optional[str]) -> None:
        if not email:
            return
        try:
            SessionDriver().remove_tokens(email)
        except Exception:
            logger.warning("Could not revoke sessions for deleted account", exc_info=True)

    def get_all_users_paged(self, page: int, size: int):
        query = self.db.query(User)
        total = query.count()
        users = query.offset((page - 1) * size).limit(size).all()
        
        return {
            "total": total,
            "page": page,
            "size": size,
            "users": [
                UserResponse(
                    id=user.id,
                    fullname=user.fullname,
                    email=user.email,
                    phone_number=user.phone_number,
                    enabled=user.enabled,
                    status=user.status,
                    created_at=user.created_at,
                    updated_at=user.updated_at  
                ) for user in users
            ]
        }

    def update_user(self, email: str, payload: UserUpdateRequest) -> UserResponse:
            # log the update attempt
            logger.debug(f"Updating user {email} with data: {payload.dict(exclude_unset=True)}")
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                user = self.db.query(User).filter(User.email.ilike(email)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            data = payload.dict(exclude_unset=True)
            data.pop("member_id", None)
            if data.get("whatsapp_number"):
                data["whatsapp_number"] = str(data["whatsapp_number"])[:20]

            if "branch_id" in data or "current_branch" in data:
                resolved_id, resolved_name = resolve_branch(
                    self.db,
                    branch_id=data.pop("branch_id", None) or None,
                    current_branch=data.pop("current_branch", None),
                )
                user.branch_id = resolved_id
                if resolved_name is not None:
                    user.current_branch = resolved_name

            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return self.get_user_by_id(user.id)

    def update_current_user(self, email: str, payload: UserUpdateRequest) -> UserResponse:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            data = payload.dict(exclude_unset=True)
            if "branch_id" in data or "current_branch" in data:
                resolved_id, resolved_name = resolve_branch(
                    self.db,
                    branch_id=data.pop("branch_id", None) or None,
                    current_branch=data.pop("current_branch", None),
                )
                user.branch_id = resolved_id
                if resolved_name is not None:
                    user.current_branch = resolved_name
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return self._to_response(user)