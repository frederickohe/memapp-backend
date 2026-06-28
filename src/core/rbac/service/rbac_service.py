from typing import Optional

from sqlalchemy.orm import Session, joinedload

from core.rbac.model.Role import Role
from core.rbac.seed import ASSIGNABLE_ROLES
from core.user.model.User import User, UserType


class RbacService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_role(self, user: User) -> Optional[Role]:
        if user.admin_role:
            return user.admin_role
        if not user.role_id:
            return None
        return (
            self.db.query(Role)
            .options(joinedload(Role.permissions))
            .filter(Role.id == user.role_id)
            .first()
        )

    def is_super_admin(self, user: User) -> bool:
        role = self.get_user_role(user)
        return bool(role and role.name == "super_admin")

    def user_has_permission(self, user: User, permission_name: str) -> bool:
        if user.user_type != UserType.ADMIN:
            return False
        if self.is_super_admin(user):
            return True
        role = self.get_user_role(user)
        if not role or not role.is_active:
            return False
        return any(p.name == permission_name for p in role.permissions)

    def can_assign_role(self, actor: User, target_role: Role) -> bool:
        if actor.user_type != UserType.ADMIN:
            return False
        if self.is_super_admin(actor):
            return True
        actor_role = self.get_user_role(actor)
        if not actor_role:
            return False
        allowed = set(ASSIGNABLE_ROLES.get(actor_role.name, []))
        return target_role.name in allowed

    def can_create_admin(self, actor: Optional[User]) -> bool:
        if actor is None:
            return True
        return self.user_has_permission(actor, "admin_users.create")
