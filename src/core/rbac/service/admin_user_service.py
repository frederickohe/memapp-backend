import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload

from core.exceptions.AuthException import PermissionDeniedError
from core.exceptions.UserException import UserAlreadyExistsError
from core.rbac.dto.request.admin_user_requests import (
    CreateAdminUserRequest,
    ResetAdminUserPasswordRequest,
    UpdateAdminUserRequest,
)
from core.rbac.dto.response.admin_user_responses import (
    AdminRoleSummary,
    AdminUserListResponse,
    AdminUserResponse,
)
from core.rbac.service.rbac_service import RbacService
from core.rbac.service.role_service import RoleService
from core.user.model.User import User, UserType
from utilities.id_helper import generate_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminUserService:
    def __init__(self, db: Session):
        self.db = db
        self.rbac = RbacService(db)
        self.role_service = RoleService(db)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _to_response(self, user: User) -> AdminUserResponse:
        role = user.admin_role or self.role_service.get_role_entity(user.role_id or "")
        if not role:
            raise HTTPException(status_code=500, detail="Admin user has no assigned role")

        return AdminUserResponse(
            id=user.id,
            full_name=user.fullname,
            email=user.email,
            phone=user.phone_number or "",
            is_active=user.enabled,
            reset_required=user.reset_required,
            last_login_at=user.last_login_at,
            role=AdminRoleSummary(id=role.id, name=role.name),
            assigned_region=user.assigned_region,
            assigned_branch=user.assigned_branch,
        )

    def list_admin_users(self, page: int = 1, limit: int = 20) -> AdminUserListResponse:
        query = (
            self.db.query(User)
            .options(joinedload(User.admin_role))
            .filter(User.user_type == UserType.ADMIN)
            .order_by(User.created_at.desc())
        )
        total = query.count()
        pages = max(1, math.ceil(total / limit)) if total else 1
        users = query.offset((page - 1) * limit).limit(limit).all()

        return AdminUserListResponse(
            total=total,
            page=page,
            pages=pages,
            users=[self._to_response(user) for user in users],
        )

    def get_admin_user(self, user_id: str) -> AdminUserResponse:
        user = (
            self.db.query(User)
            .options(joinedload(User.admin_role))
            .filter(User.id == user_id, User.user_type == UserType.ADMIN)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        return self._to_response(user)

    def create_admin_user(
        self,
        request: CreateAdminUserRequest,
        actor: Optional[User] = None,
    ) -> AdminUserResponse:
        existing_admin_count = (
            self.db.query(User).filter(User.user_type == UserType.ADMIN).count()
        )

        if existing_admin_count > 0:
            if not actor or actor.user_type != UserType.ADMIN:
                raise PermissionDeniedError(
                    detail="Only an existing admin can create new admin accounts"
                )
            if not self.rbac.can_create_admin(actor):
                raise PermissionDeniedError(
                    detail="You do not have permission to create admin accounts"
                )

        target_role = self.role_service.get_role_entity(request.role_id)
        if not target_role or not target_role.is_active:
            raise HTTPException(status_code=400, detail="Invalid role selected")

        if existing_admin_count > 0 and actor and not self.rbac.can_assign_role(actor, target_role):
            raise PermissionDeniedError(
                detail=f"You cannot assign the {target_role.name} role"
            )

        if target_role.name == "regional_admin" and not request.assigned_region:
            raise HTTPException(status_code=400, detail="Regional admins require an assigned region")
        if target_role.name == "branch_admin" and not request.assigned_branch:
            raise HTTPException(status_code=400, detail="Branch admins require an assigned branch")

        existing_user = (
            self.db.query(User)
            .filter((User.email == request.email) | (User.fullname == request.full_name))
            .first()
        )
        if existing_user:
            if existing_user.email == request.email:
                raise UserAlreadyExistsError(field="email")
            raise UserAlreadyExistsError(field="fullname")

        user = User(
            id=generate_id(),
            fullname=request.full_name,
            email=request.email,
            phone_number=request.phone,
            hashed_password=self._hash_password(request.password),
            user_type=UserType.ADMIN,
            role=target_role.name.upper(),
            role_id=target_role.id,
            reset_required=request.reset_required,
            assigned_region=request.assigned_region,
            assigned_branch=request.assigned_branch,
            enabled=True,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        user.admin_role = target_role
        return self._to_response(user)

    def update_admin_user(
        self,
        user_id: str,
        request: UpdateAdminUserRequest,
        actor: User,
    ) -> AdminUserResponse:
        if not self.rbac.user_has_permission(actor, "admin_users.update"):
            raise PermissionDeniedError(detail="You do not have permission to update admin users")

        user = (
            self.db.query(User)
            .options(joinedload(User.admin_role))
            .filter(User.id == user_id, User.user_type == UserType.ADMIN)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="Admin user not found")

        if request.full_name is not None:
            user.fullname = request.full_name
        if request.phone is not None:
            user.phone_number = request.phone
        if request.is_active is not None:
            user.enabled = request.is_active
        if request.reset_required is not None:
            user.reset_required = request.reset_required
        if request.assigned_region is not None:
            user.assigned_region = request.assigned_region
        if request.assigned_branch is not None:
            user.assigned_branch = request.assigned_branch

        if request.role_id is not None:
            target_role = self.role_service.get_role_entity(request.role_id)
            if not target_role or not target_role.is_active:
                raise HTTPException(status_code=400, detail="Invalid role selected")
            if not self.rbac.can_assign_role(actor, target_role):
                raise PermissionDeniedError(
                    detail=f"You cannot assign the {target_role.name} role"
                )
            user.role_id = target_role.id
            user.role = target_role.name.upper()
            user.admin_role = target_role

        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return self._to_response(user)

    def deactivate_admin_user(self, user_id: str, actor: User) -> None:
        if not self.rbac.user_has_permission(actor, "admin_users.deactivate"):
            raise PermissionDeniedError(
                detail="You do not have permission to deactivate admin users"
            )
        if actor.id == user_id:
            raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

        user = (
            self.db.query(User)
            .filter(User.id == user_id, User.user_type == UserType.ADMIN)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="Admin user not found")

        user.enabled = False
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()

    def reset_admin_password(
        self,
        user_id: str,
        request: ResetAdminUserPasswordRequest,
        actor: User,
    ) -> None:
        if not self.rbac.user_has_permission(actor, "admin_users.reset_password"):
            raise PermissionDeniedError(
                detail="You do not have permission to reset admin passwords"
            )

        user = (
            self.db.query(User)
            .filter(User.id == user_id, User.user_type == UserType.ADMIN)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="Admin user not found")

        user.hashed_password = self._hash_password(request.new_password)
        user.reset_required = False
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()

    def record_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
