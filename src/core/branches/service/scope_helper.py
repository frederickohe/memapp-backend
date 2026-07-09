"""Helpers for filtering queries by national, regional, or branch scope."""

from typing import Optional, Tuple

from sqlalchemy.orm import Query, Session

from core.branches.model.Branch import Branch
from core.user.model.User import User, UserType


def resolve_scope(
    scope: Optional[str],
    region_id: Optional[str],
    branch_id: Optional[str],
) -> Tuple[str, Optional[str], Optional[str]]:
    normalized = (scope or "national").lower()
    if normalized not in ("national", "region", "branch"):
        normalized = "national"
    if normalized == "branch" and branch_id:
        return normalized, None, branch_id
    if normalized == "region" and region_id:
        return normalized, region_id, None
    return "national", None, None


def apply_member_scope(
    query: Query,
    db: Session,
    scope: str,
    region_id: Optional[str],
    branch_id: Optional[str],
) -> Query:
    if scope == "branch" and branch_id:
        return query.filter(User.branch_id == branch_id)
    if scope == "region" and region_id:
        branch_ids = [
            row[0]
            for row in db.query(Branch.id).filter(Branch.region_id == region_id, Branch.is_active.is_(True)).all()
        ]
        if not branch_ids:
            return query.filter(User.id.is_(None))
        return query.filter(User.branch_id.in_(branch_ids))
    return query


def apply_branch_id_filter(query: Query, branch_id: Optional[str]) -> Query:
    if branch_id:
        return query.filter(User.branch_id == branch_id)
    return query


def get_scoped_member_ids(
    db: Session,
    scope: str,
    region_id: Optional[str],
    branch_id: Optional[str],
) -> Optional[list[str]]:
    query = db.query(User.id).filter(User.user_type == UserType.MEMBER, User.enabled.is_(True))
    query = apply_member_scope(query, db, scope, region_id, branch_id)
    ids = [row[0] for row in query.all()]
    return ids
