import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from core.rbac.dto.request.member_user_requests import UpdateMemberUserRequest
from core.rbac.dto.response.member_user_responses import (
    MemberUserListResponse,
    MemberUserOverviewResponse,
    MemberUserResponse,
)
from core.dashboard.dto.response.dashboardresponse import ProminentProfileResponse
from core.user.model.User import User, UserStatus, UserType


class MemberUserService:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return self.db.query(User).filter(User.user_type == UserType.MEMBER)

    def _to_response(self, user: User) -> MemberUserResponse:
        return MemberUserResponse(
            id=user.id,
            full_name=user.fullname,
            email=user.email,
            phone=user.phone_number,
            member_id=user.member_id,
            membership_type=user.membership_type,
            current_branch=user.current_branch,
            month_dues_paid_status=user.month_dues_paid_status,
            year_affiliation_paid_status=user.year_affiliation_paid_status,
            volunteer_points=user.volunteer_points or 0,
            profile_picture_url=user.profile_picture_url,
            is_prominent=user.is_prominent or False,
            prominent_order=user.prominent_order or 0,
            prominent_headline=user.prominent_headline,
            is_active=user.enabled,
            status=user.status,
            created_at=user.created_at,
        )

    def get_overview(self) -> MemberUserOverviewResponse:
        members = self._base_query()
        total = members.count()
        active = members.filter(
            User.enabled.is_(True),
            User.status == UserStatus.ACTIVE,
        ).count()
        inactive = total - active
        dues_pending = members.filter(
            or_(
                User.month_dues_paid_status.is_(None),
                User.month_dues_paid_status != "PAID",
            )
        ).count()
        affiliation_pending = members.filter(
            or_(
                User.year_affiliation_paid_status.is_(None),
                User.year_affiliation_paid_status != "PAID",
            )
        ).count()

        return MemberUserOverviewResponse(
            total_users=total,
            active_users=active,
            inactive_users=inactive,
            dues_pending=dues_pending,
            affiliation_pending=affiliation_pending,
        )

    def list_member_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        branch: Optional[str] = None,
        membership_type: Optional[str] = None,
        prominent_only: Optional[bool] = None,
    ) -> MemberUserListResponse:
        query = self._base_query().order_by(User.created_at.desc())

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.fullname.ilike(term),
                    User.email.ilike(term),
                    User.phone_number.ilike(term),
                    User.member_id.ilike(term),
                )
            )

        if status:
            query = query.filter(User.status == status)

        if branch:
            query = query.filter(User.current_branch.ilike(f"%{branch.strip()}%"))

        if membership_type:
            query = query.filter(User.membership_type == membership_type)

        if prominent_only is not None:
            query = query.filter(User.is_prominent == prominent_only)

        total = query.count()
        pages = max(1, math.ceil(total / limit)) if total else 1
        users = query.offset((page - 1) * limit).limit(limit).all()

        return MemberUserListResponse(
            total=total,
            page=page,
            pages=pages,
            users=[self._to_response(user) for user in users],
        )

    def get_member_user(self, user_id: str) -> MemberUserResponse:
        user = self._base_query().filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_response(user)

    def update_member_user(
        self,
        user_id: str,
        request: UpdateMemberUserRequest,
    ) -> MemberUserResponse:
        user = self._base_query().filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data = request.dict(exclude_unset=True)
        field_map = {
            "full_name": "fullname",
            "email": "email",
            "phone": "phone_number",
            "member_id": "member_id",
            "membership_type": "membership_type",
            "current_branch": "current_branch",
            "month_dues_paid_status": "month_dues_paid_status",
            "year_affiliation_paid_status": "year_affiliation_paid_status",
            "is_prominent": "is_prominent",
            "prominent_order": "prominent_order",
            "prominent_headline": "prominent_headline",
        }

        for key, value in data.items():
            attr = field_map.get(key, key)
            if hasattr(user, attr):
                setattr(user, attr, value)

        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return self._to_response(user)

    def list_prominent_profiles(self, limit: int = 10) -> list[ProminentProfileResponse]:
        users = (
            self._base_query()
            .filter(
                User.is_prominent.is_(True),
                User.enabled.is_(True),
                User.status == UserStatus.ACTIVE,
            )
            .order_by(User.prominent_order.asc(), User.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            ProminentProfileResponse(
                id=user.id,
                full_name=user.fullname,
                profile_picture_url=user.profile_picture_url,
                current_branch=user.current_branch,
                occupation=user.occupation,
                prominent_headline=user.prominent_headline,
                volunteer_points=user.volunteer_points or 0,
            )
            for user in users
        ]

    def deactivate_member_user(self, user_id: str) -> None:
        user = self._base_query().filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.enabled = False
        user.status = UserStatus.INACTIVE
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
