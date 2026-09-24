import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from core.branches.model.Branch import Branch
from core.branches.model.Region import Region
from core.branches.service.scope_helper import apply_member_scope, resolve_scope
from core.exceptions.AuthException import PermissionDeniedError
from core.rbac.dto.request.member_user_requests import AssignMemberRoleRequest, UpdateMemberUserRequest
from core.rbac.dto.response.member_user_responses import (
    MemberUserListResponse,
    MemberUserOverviewResponse,
    MemberUserResponse,
)
from core.rbac.service.rbac_service import RbacService
from core.rbac.service.role_service import RoleService
from core.dashboard.dto.response.dashboardresponse import ProminentProfileResponse
from core.user.model.User import User, UserStatus, UserType
from core.user.service.membership_helpers import format_role_label, resolve_branch, resolve_position


class MemberUserService:
    def __init__(self, db: Session):
        self.db = db
        self.rbac = RbacService(db)
        self.role_service = RoleService(db)

    def _base_query(self):
        return self.db.query(User).filter(
            User.status != UserStatus.DELETED,
            or_(
                User.user_type == UserType.MEMBER,
                User.member_id.isnot(None),
            ),
        )

    def _to_response(self, user: User) -> MemberUserResponse:
        branch_name = None
        region_name = None
        if user.branch:
            branch_name = user.branch.name
            if user.branch.region:
                region_name = user.branch.region.name
        role_name = None
        if user.admin_role:
            role_name = user.admin_role.name
        elif user.role:
            role_name = user.role.lower()
        return MemberUserResponse(
            id=user.id,
            full_name=user.fullname,
            email=user.email,
            phone=user.phone_number,
            member_id=user.member_id,
            membership_type=user.membership_type,
            date_joined_organization=user.date_joined_organization,
            past_positions=user.past_positions or [],
            current_branch=user.current_branch or branch_name,
            branch_id=user.branch_id,
            branch_name=branch_name,
            region_name=region_name,
            user_type=user.user_type,
            role_id=user.role_id,
            role_name=role_name,
            position=format_role_label(role_name) or resolve_position(self.db, user),
            assigned_region=user.assigned_region,
            assigned_branch=user.assigned_branch,
            month_dues_paid_status=(
                "NOT_REQUIRED"
                if user.branch is not None and not user.branch.collects_dues
                else user.month_dues_paid_status
            ),
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

    def get_overview(
        self,
        scope: Optional[str] = None,
        region_id: Optional[str] = None,
        branch_id: Optional[str] = None,
    ) -> MemberUserOverviewResponse:
        resolved_scope, resolved_region_id, resolved_branch_id = resolve_scope(
            scope, region_id, branch_id
        )
        members = self._base_query()
        members = apply_member_scope(
            members, self.db, resolved_scope, resolved_region_id, resolved_branch_id
        )
        total = members.count()
        active = members.filter(
            User.enabled.is_(True),
            User.status == UserStatus.ACTIVE,
        ).count()
        inactive = total - active
        dues_pending = (
            members.outerjoin(Branch, User.branch_id == Branch.id)
            .filter(or_(User.branch_id.is_(None), Branch.collects_dues.is_(True)))
            .filter(
                or_(
                    User.month_dues_paid_status.is_(None),
                    func.upper(User.month_dues_paid_status).notin_(
                        ["YES", "PAID", "NOT_REQUIRED", "N/A"]
                    ),
                )
            )
            .count()
        )
        affiliation_pending = members.filter(
            or_(
                User.year_affiliation_paid_status.is_(None),
                func.upper(User.year_affiliation_paid_status).notin_(
                    ["YES", "PAID", "NOT_REQUIRED", "N/A"]
                ),
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
        branch_id: Optional[str] = None,
        region_id: Optional[str] = None,
        scope: Optional[str] = None,
        membership_type: Optional[str] = None,
        prominent_only: Optional[bool] = None,
    ) -> MemberUserListResponse:
        resolved_scope, resolved_region_id, resolved_branch_id = resolve_scope(
            scope, region_id, branch_id
        )
        if branch_id:
            resolved_scope = "branch"
            resolved_branch_id = branch_id

        query = (
            self._base_query()
            .options(
                joinedload(User.branch).joinedload(Branch.region),
                joinedload(User.admin_role),
            )
            .order_by(User.created_at.desc())
        )
        query = apply_member_scope(
            query, self.db, resolved_scope, resolved_region_id, resolved_branch_id
        )

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

        if branch and not branch_id:
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
        user = (
            self._base_query()
            .options(
                joinedload(User.branch).joinedload(Branch.region),
                joinedload(User.admin_role),
            )
            .filter(User.id == user_id)
            .first()
        )
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
            "date_joined_organization": "date_joined_organization",
            "past_positions": "past_positions",
            "current_branch": "current_branch",
            "branch_id": "branch_id",
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

        if "branch_id" in data or "current_branch" in data:
            resolved_id, resolved_name = resolve_branch(
                self.db,
                branch_id=data.get("branch_id") or None,
                current_branch=data.get("current_branch"),
            )
            user.branch_id = resolved_id
            if resolved_name is not None:
                user.current_branch = resolved_name

        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return self.get_member_user(user.id)

    def assign_member_role(
        self,
        user_id: str,
        request: AssignMemberRoleRequest,
        actor: User,
    ) -> MemberUserResponse:
        user = (
            self._base_query()
            .options(
                joinedload(User.branch).joinedload(Branch.region),
                joinedload(User.admin_role),
            )
            .filter(User.id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not request.role_id:
            user.user_type = UserType.MEMBER
            user.role_id = None
            user.role = None
            user.assigned_region = None
            user.assigned_branch = None
            user.assigned_region_id = None
            user.assigned_branch_id = None
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            return self.get_member_user(user.id)

        target_role = self.role_service.get_role_entity(request.role_id)
        if not target_role or not target_role.is_active:
            raise HTTPException(status_code=400, detail="Invalid role selected")

        if not self.rbac.can_assign_role(actor, target_role):
            raise PermissionDeniedError(
                detail=f"You cannot assign the {target_role.name} role"
            )

        assigned_region = request.assigned_region
        assigned_branch = request.assigned_branch
        assigned_region_id = None
        assigned_branch_id = user.branch_id

        if user.branch:
            if not assigned_branch:
                assigned_branch = user.branch.name
            if user.branch.region and not assigned_region:
                assigned_region = user.branch.region.name
                assigned_region_id = user.branch.region_id

        if target_role.name == "regional_admin" and not assigned_region:
            raise HTTPException(
                status_code=400,
                detail="Regional admins require an assigned region",
            )
        if target_role.name == "branch_admin" and not assigned_branch:
            raise HTTPException(
                status_code=400,
                detail="Branch admins require an assigned branch",
            )

        if assigned_region:
            region = (
                self.db.query(Region)
                .filter(func.lower(Region.name) == assigned_region.strip().lower())
                .first()
            )
            if region:
                assigned_region = region.name
                assigned_region_id = region.id

        if assigned_branch and not assigned_branch_id:
            branch = (
                self.db.query(Branch)
                .filter(func.lower(Branch.name) == assigned_branch.strip().lower())
                .first()
            )
            if branch:
                assigned_branch = branch.name
                assigned_branch_id = branch.id

        user.user_type = UserType.ADMIN
        user.role_id = target_role.id
        user.role = target_role.name.upper()
        user.assigned_region = assigned_region
        user.assigned_branch = assigned_branch
        user.assigned_region_id = assigned_region_id
        user.assigned_branch_id = assigned_branch_id
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self.get_member_user(user.id)

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
