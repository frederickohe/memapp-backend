from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from config import settings
from core.branches.dto.response.branch_responses import (
    ProgressOverviewResponse,
    RecentRegistration,
    TopBranchStat,
)
from core.branches.model.Branch import Branch
from core.branches.model.Region import Region
from core.branches.service.scope_helper import apply_member_scope, resolve_scope
from core.user.model.User import User, UserStatus, UserType
from core.vhs.model.volunteer_hours_submission import VhsStatus, VolunteerHoursSubmission


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_progress_overview(
        self,
        scope: Optional[str] = None,
        region_id: Optional[str] = None,
        branch_id: Optional[str] = None,
    ) -> ProgressOverviewResponse:
        resolved_scope, resolved_region_id, resolved_branch_id = resolve_scope(scope, region_id, branch_id)

        region_name = None
        branch_name = None
        if resolved_scope == "region" and resolved_region_id:
            region = self.db.query(Region).filter(Region.id == resolved_region_id).first()
            region_name = region.name if region else None
        if resolved_scope == "branch" and resolved_branch_id:
            branch = (
                self.db.query(Branch)
                .options(joinedload(Branch.region))
                .filter(Branch.id == resolved_branch_id)
                .first()
            )
            branch_name = branch.name if branch else None
            region_name = branch.region.name if branch and branch.region else None

        members_query = self.db.query(User).filter(User.user_type == UserType.MEMBER)
        members_query = apply_member_scope(
            members_query, self.db, resolved_scope, resolved_region_id, resolved_branch_id
        )

        total_members = members_query.count()
        active_members = members_query.filter(
            User.enabled.is_(True),
            User.status == UserStatus.ACTIVE,
        ).count()
        inactive_members = total_members - active_members

        vhs_query = self.db.query(VolunteerHoursSubmission)
        if resolved_scope == "branch" and resolved_branch_id:
            vhs_query = vhs_query.filter(VolunteerHoursSubmission.branch_id == resolved_branch_id)
        elif resolved_scope == "region" and resolved_region_id:
            branch_ids = [
                row[0]
                for row in self.db.query(Branch.id).filter(Branch.region_id == resolved_region_id).all()
            ]
            if branch_ids:
                vhs_query = vhs_query.filter(VolunteerHoursSubmission.branch_id.in_(branch_ids))
            else:
                vhs_query = vhs_query.filter(VolunteerHoursSubmission.id.is_(None))

        pending_vhs = vhs_query.filter(VolunteerHoursSubmission.status == VhsStatus.PENDING).count()
        approved_vhs = vhs_query.filter(VolunteerHoursSubmission.status == VhsStatus.APPROVED).count()

        if resolved_scope == "branch" and resolved_branch_id:
            branch_count = 1
        elif resolved_scope == "region" and resolved_region_id:
            branch_count = (
                self.db.query(Branch)
                .filter(Branch.region_id == resolved_region_id, Branch.is_active.is_(True))
                .count()
            )
        else:
            branch_count = self.db.query(Branch).filter(Branch.is_active.is_(True)).count()

        member_target = self._member_target(resolved_scope, branch_count)
        members_remaining = max(0, member_target - total_members)
        member_progress_pct = self._member_progress_pct(total_members, member_target)

        top_branches = self._top_branches(resolved_scope, resolved_region_id, resolved_branch_id)
        recent_registrations = self._recent_registrations(
            resolved_scope, resolved_region_id, resolved_branch_id
        )

        return ProgressOverviewResponse(
            scope=resolved_scope,
            region_id=resolved_region_id,
            region_name=region_name,
            branch_id=resolved_branch_id,
            branch_name=branch_name,
            total_members=total_members,
            active_members=active_members,
            inactive_members=inactive_members,
            member_target=member_target,
            members_remaining=members_remaining,
            member_progress_pct=member_progress_pct,
            pending_vhs=pending_vhs,
            approved_vhs=approved_vhs,
            branch_count=branch_count,
            top_branches=top_branches,
            recent_registrations=recent_registrations,
        )

    @staticmethod
    def _member_target(scope: str, branch_count: int) -> int:
        if scope == "branch":
            return settings.YMCA_BRANCH_MEMBER_TARGET
        if scope == "region":
            return branch_count * settings.YMCA_BRANCH_MEMBER_TARGET
        return settings.YMCA_ORGANIZATION_MEMBER_TARGET

    @staticmethod
    def _member_progress_pct(total_members: int, member_target: int) -> int:
        if member_target <= 0:
            return 0
        return min(100, round((total_members / member_target) * 100))

    def _top_branches(
        self,
        scope: str,
        region_id: Optional[str],
        branch_id: Optional[str],
        limit: int = 5,
    ) -> list[TopBranchStat]:
        query = (
            self.db.query(
                Branch.id,
                Branch.name,
                Region.name,
                func.count(User.id).label("member_count"),
            )
            .join(Region, Branch.region_id == Region.id)
            .outerjoin(User, (User.branch_id == Branch.id) & (User.user_type == UserType.MEMBER))
            .filter(Branch.is_active.is_(True))
            .group_by(Branch.id, Branch.name, Region.name)
            .order_by(desc("member_count"))
        )

        if scope == "branch" and branch_id:
            query = query.filter(Branch.id == branch_id)
        elif scope == "region" and region_id:
            query = query.filter(Branch.region_id == region_id)

        rows = query.limit(limit).all()
        branch_target = settings.YMCA_BRANCH_MEMBER_TARGET
        return [
            TopBranchStat(
                branch_id=row[0],
                branch_name=row[1],
                region_name=row[2],
                member_count=row[3] or 0,
                member_target=branch_target,
                member_progress_pct=AnalyticsService._member_progress_pct(row[3] or 0, branch_target),
            )
            for row in rows
        ]

    def _recent_registrations(
        self,
        scope: str,
        region_id: Optional[str],
        branch_id: Optional[str],
        limit: int = 5,
    ) -> list[RecentRegistration]:
        query = (
            self.db.query(User)
            .options(joinedload(User.branch).joinedload(Branch.region))
            .filter(User.user_type == UserType.MEMBER)
            .order_by(User.created_at.desc())
        )
        query = apply_member_scope(query, self.db, scope, region_id, branch_id)
        users = query.limit(limit).all()

        return [
            RecentRegistration(
                id=user.id,
                name=user.fullname,
                branch_name=user.branch.name if getattr(user, "branch", None) else user.current_branch,
                member_id=user.member_id,
                status="active" if user.enabled and user.status == UserStatus.ACTIVE else "inactive",
                created_at=user.created_at,
            )
            for user in users
        ]
