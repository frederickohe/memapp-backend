from typing import List

from sqlalchemy.orm import Session

from core.rbac.model.Permission import Permission
from core.rbac.model.Role import Role
from core.rbac.seed import LEGACY_ROLE_MAP, PERMISSION_CATALOGUE, ROLE_PERMISSIONS, SYSTEM_ROLES
from core.user.model.User import User, UserType
from utilities.id_helper import generate_id


class PermissionService:
    def __init__(self, db: Session):
        self.db = db

    def list_permissions(self) -> List[Permission]:
        return (
            self.db.query(Permission)
            .order_by(Permission.group, Permission.name)
            .all()
        )

    def ensure_seed_data(self) -> None:
        existing = self.db.query(Permission).count()
        if existing == 0:
            permission_by_name = {}
            for name, group, description in PERMISSION_CATALOGUE:
                permission = Permission(
                    id=generate_id(),
                    name=name,
                    group=group,
                    description=description,
                )
                self.db.add(permission)
                permission_by_name[name] = permission

            role_by_name = {}
            for name, description in SYSTEM_ROLES:
                role = Role(
                    id=generate_id(),
                    name=name,
                    description=description,
                    is_system=True,
                    is_active=True,
                )
                self.db.add(role)
                role_by_name[name] = role

            self.db.flush()

            for role_name, permission_names in ROLE_PERMISSIONS.items():
                role = role_by_name[role_name]
                role.permissions = [
                    permission_by_name[pname]
                    for pname in permission_names
                    if pname in permission_by_name
                ]

            self.db.commit()

        self._migrate_legacy_admins()

    def _migrate_legacy_admins(self) -> None:
        admins = (
            self.db.query(User)
            .filter(User.user_type == UserType.ADMIN, User.role_id.is_(None))
            .all()
        )
        if not admins:
            return

        for user in admins:
            legacy_key = (user.role or "SUPER_ADMIN").upper()
            role_name = LEGACY_ROLE_MAP.get(legacy_key, "super_admin")
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                continue
            user.role_id = role.id
            user.role = role.name.upper()
        self.db.commit()

    def get_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        if not permission_ids:
            return []
        return (
            self.db.query(Permission)
            .filter(Permission.id.in_(permission_ids))
            .all()
        )
