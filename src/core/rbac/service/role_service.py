from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from core.rbac.dto.request.role_requests import CreateRoleRequest, UpdateRoleRequest
from core.rbac.dto.response.role_responses import RolePermissionSummary, RoleResponse
from core.rbac.model.Permission import Permission
from core.rbac.model.Role import Role
from core.rbac.service.permission_service import PermissionService
from utilities.id_helper import generate_id


def _normalize_role_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)

    def _to_response(self, role: Role, include_permissions: bool) -> RoleResponse:
        permissions = None
        if include_permissions:
            permissions = [
                RolePermissionSummary(
                    id=p.id,
                    name=p.name,
                    group=p.group,
                )
                for p in role.permissions
            ]
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system=role.is_system,
            is_active=role.is_active,
            permissions=permissions,
        )

    def list_roles(self, include_permissions: bool = True) -> List[RoleResponse]:
        query = self.db.query(Role).order_by(Role.name)
        if include_permissions:
            query = query.options(joinedload(Role.permissions))
        roles = query.all()
        return [self._to_response(role, include_permissions) for role in roles]

    def get_role(self, role_id: str, include_permissions: bool = True) -> RoleResponse:
        query = self.db.query(Role).filter(Role.id == role_id)
        if include_permissions:
            query = query.options(joinedload(Role.permissions))
        role = query.first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return self._to_response(role, include_permissions)

    def get_role_entity(self, role_id: str) -> Optional[Role]:
        return (
            self.db.query(Role)
            .options(joinedload(Role.permissions))
            .filter(Role.id == role_id)
            .first()
        )

    def get_role_by_name(self, name: str) -> Optional[Role]:
        normalized = _normalize_role_name(name)
        return (
            self.db.query(Role)
            .options(joinedload(Role.permissions))
            .filter(Role.name == normalized)
            .first()
        )

    def create_role(self, request: CreateRoleRequest) -> RoleResponse:
        name = _normalize_role_name(request.name)
        if self.db.query(Role).filter(Role.name == name).first():
            raise HTTPException(status_code=409, detail="Role name already exists")

        permissions = self.permission_service.get_by_ids(request.permission_ids)
        if len(permissions) != len(set(request.permission_ids)):
            raise HTTPException(status_code=400, detail="One or more permissions are invalid")

        role = Role(
            id=generate_id(),
            name=name,
            description=request.description.strip(),
            is_system=False,
            is_active=True,
            permissions=permissions,
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return self._to_response(role, True)

    def update_role(self, role_id: str, request: UpdateRoleRequest) -> RoleResponse:
        role = self.get_role_entity(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        if request.name is not None:
            name = _normalize_role_name(request.name)
            existing = self.db.query(Role).filter(Role.name == name, Role.id != role_id).first()
            if existing:
                raise HTTPException(status_code=409, detail="Role name already exists")
            role.name = name

        if request.description is not None:
            role.description = request.description.strip()

        if request.is_active is not None:
            if role.is_system and not request.is_active:
                raise HTTPException(status_code=400, detail="System roles cannot be deactivated")
            role.is_active = request.is_active

        role.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(role)
        return self._to_response(role, True)

    def delete_role(self, role_id: str) -> None:
        role = self.get_role_entity(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role.is_system:
            raise HTTPException(status_code=400, detail="System roles cannot be deleted")
        if role.users:
            raise HTTPException(
                status_code=400,
                detail="Role is assigned to admin users and cannot be deleted",
            )
        self.db.delete(role)
        self.db.commit()

    def set_role_permissions(self, role_id: str, permission_ids: List[str]) -> RoleResponse:
        role = self.get_role_entity(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role.is_system and role.name == "super_admin":
            raise HTTPException(
                status_code=400,
                detail="Super admin permissions cannot be modified",
            )

        permissions = self.permission_service.get_by_ids(permission_ids)
        if len(permissions) != len(set(permission_ids)):
            raise HTTPException(status_code=400, detail="One or more permissions are invalid")

        role.permissions = permissions
        role.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(role)
        return self._to_response(role, True)
