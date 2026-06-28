from typing import Callable

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user, get_db, require_admin
from core.rbac.service.rbac_service import RbacService
from core.user.model.User import User


def require_permission(permission_name: str) -> Callable:
    def _dependency(
        user: User = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> User:
        rbac = RbacService(db)
        if not rbac.user_has_permission(user, permission_name):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission_name}",
            )
        return user

    return _dependency
