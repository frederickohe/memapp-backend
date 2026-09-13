from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.branches.model.Branch import Branch
from core.rbac.model.Role import Role
from core.user.model.User import User

ROLE_LABELS = {
    "super_admin": "Super Admin",
    "national_admin": "National Admin",
    "regional_admin": "Regional Admin",
    "branch_admin": "Branch Admin",
}


def format_role_label(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    key = name.strip().lower()
    if key in ROLE_LABELS:
        return ROLE_LABELS[key]
    return name.replace("_", " ").replace("-", " ").title()


def resolve_branch(
    db: Session,
    branch_id: Optional[str] = None,
    current_branch: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Return (branch_id, branch_name) for an active branch."""
    if branch_id:
        branch = (
            db.query(Branch)
            .filter(Branch.id == branch_id, Branch.is_active.is_(True))
            .first()
        )
        if not branch:
            raise HTTPException(
                status_code=400,
                detail="Selected branch is not available",
            )
        return branch.id, branch.name

    if current_branch and str(current_branch).strip():
        name = str(current_branch).strip()
        branch = (
            db.query(Branch)
            .filter(func.lower(Branch.name) == name.lower(), Branch.is_active.is_(True))
            .first()
        )
        if branch:
            return branch.id, branch.name
        return None, name

    return None, None


def resolve_position(db: Session, user: User) -> Optional[str]:
    role_name = None
    admin_role = getattr(user, "admin_role", None)
    if admin_role and getattr(admin_role, "name", None):
        role_name = admin_role.name
    elif user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name
    elif user.role:
        role_name = user.role

    if role_name:
        return format_role_label(role_name)

    is_president = (
        db.query(Branch.id).filter(Branch.president_id == user.id).first()
    )
    if is_president:
        return "Branch President"
    return None
