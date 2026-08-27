import math
import secrets
import string
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from core.branches.model.Branch import Branch
from core.branches.service.scope_helper import resolve_scope
from core.user.model.User import User, UserType
from core.vhs.dto.request.vhs_requests import RejectVhsRequest, SubmitVolunteerHoursRequest
from core.vhs.dto.response.vhs_responses import (
    VolunteerContributionResponse,
    VolunteerImpactResponse,
    VolunteerMilestoneResponse,
    VhsSubmissionListResponse,
    VhsSubmissionResponse,
)
from core.vhs.model.volunteer_hours_submission import VhsStatus, VolunteerHoursSubmission

POINTS_PER_HOUR = 10

VOLUNTEER_MILESTONES = [
    {
        "id": "first-step",
        "name": "First Step",
        "title": "Bronze Volunteer",
        "hours_required": 10,
        "image_key": "bronze",
        "level": 1,
    },
    {
        "id": "helper",
        "name": "Helper",
        "title": "Helper Volunteer",
        "hours_required": 25,
        "image_key": "platinum",
        "level": 2,
    },
    {
        "id": "champion",
        "name": "Champion",
        "title": "Gold Volunteer",
        "hours_required": 50,
        "image_key": "gold",
        "level": 3,
    },
    {
        "id": "leader",
        "name": "Leader",
        "title": "Leader Volunteer",
        "hours_required": 100,
        "image_key": None,
        "level": 4,
    },
    {
        "id": "legend",
        "name": "Legend",
        "title": "Legend Volunteer",
        "hours_required": 250,
        "image_key": None,
        "level": 5,
    },
]


class VhsService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _generate_id() -> str:
        suffix = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        return f"VHS_{suffix}"

    @staticmethod
    def _points_for_hours(hours: float) -> int:
        return max(1, round(hours * POINTS_PER_HOUR))

    def _to_response(self, submission: VolunteerHoursSubmission) -> VhsSubmissionResponse:
        member = submission.member
        points_to_award = (
            self._points_for_hours(submission.hours) if submission.status == VhsStatus.PENDING else None
        )
        return VhsSubmissionResponse(
            id=submission.id,
            user_id=submission.user_id,
            member_name=member.fullname if member else "Unknown",
            member_id=member.member_id if member else None,
            member_email=member.email if member else None,
            member_phone=member.phone_number if member else None,
            member_avatar_url=member.profile_picture_url if member else None,
            member_branch=member.current_branch if member else None,
            hours=submission.hours,
            activity_name=submission.activity_name,
            activity_description=submission.activity_description,
            branch=submission.branch or (member.current_branch if member else None),
            volunteer_date=submission.volunteer_date,
            proof_document_url=submission.proof_document_url,
            status=submission.status,
            rejection_reason=submission.rejection_reason,
            points_awarded=submission.points_awarded,
            points_to_award=points_to_award,
            reviewed_by=submission.reviewed_by,
            reviewed_at=submission.reviewed_at,
            created_at=submission.created_at,
        )

    def submit(self, user: User, request: SubmitVolunteerHoursRequest) -> VhsSubmissionResponse:
        if user.user_type != UserType.MEMBER:
            raise HTTPException(status_code=403, detail="Only members can submit volunteer hours")

        submission = VolunteerHoursSubmission(
            id=self._generate_id(),
            user_id=user.id,
            hours=request.hours,
            activity_name=request.activity_name.strip(),
            activity_description=request.activity_description.strip() if request.activity_description else None,
            branch=request.branch or user.current_branch,
            volunteer_date=request.volunteer_date,
            proof_document_url=request.proof_document_url,
            status=VhsStatus.PENDING,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        submission = (
            self.db.query(VolunteerHoursSubmission)
            .options(joinedload(VolunteerHoursSubmission.member))
            .filter(VolunteerHoursSubmission.id == submission.id)
            .first()
        )
        return self._to_response(submission)

    def list_submissions(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        scope: Optional[str] = None,
        region_id: Optional[str] = None,
        branch_id: Optional[str] = None,
    ) -> VhsSubmissionListResponse:
        resolved_scope, resolved_region_id, resolved_branch_id = resolve_scope(
            scope, region_id, branch_id
        )

        query = (
            self.db.query(VolunteerHoursSubmission)
            .options(joinedload(VolunteerHoursSubmission.member))
            .order_by(VolunteerHoursSubmission.created_at.desc())
        )
        if status and status != "all":
            query = query.filter(VolunteerHoursSubmission.status == status)

        if resolved_scope == "branch" and resolved_branch_id:
            query = query.filter(VolunteerHoursSubmission.branch_id == resolved_branch_id)
        elif resolved_scope == "region" and resolved_region_id:
            branch_ids = [
                row[0]
                for row in self.db.query(Branch.id).filter(Branch.region_id == resolved_region_id).all()
            ]
            if branch_ids:
                query = query.filter(VolunteerHoursSubmission.branch_id.in_(branch_ids))
            else:
                query = query.filter(VolunteerHoursSubmission.id.is_(None))

        total = query.count()
        pages = max(1, math.ceil(total / limit)) if total else 1
        submissions = query.offset((page - 1) * limit).limit(limit).all()

        return VhsSubmissionListResponse(
            total=total,
            page=page,
            pages=pages,
            submissions=[self._to_response(s) for s in submissions],
        )

    def get_submission(self, submission_id: str) -> VhsSubmissionResponse:
        submission = (
            self.db.query(VolunteerHoursSubmission)
            .options(joinedload(VolunteerHoursSubmission.member))
            .filter(VolunteerHoursSubmission.id == submission_id)
            .first()
        )
        if not submission:
            raise HTTPException(status_code=404, detail="Volunteer hours submission not found")
        return self._to_response(submission)

    def approve(self, submission_id: str, admin: User) -> VhsSubmissionResponse:
        submission = (
            self.db.query(VolunteerHoursSubmission)
            .options(joinedload(VolunteerHoursSubmission.member))
            .filter(VolunteerHoursSubmission.id == submission_id)
            .first()
        )
        if not submission:
            raise HTTPException(status_code=404, detail="Volunteer hours submission not found")
        if submission.status != VhsStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only pending submissions can be approved")

        points = self._points_for_hours(submission.hours)
        submission.status = VhsStatus.APPROVED
        submission.points_awarded = points
        submission.reviewed_by = admin.id
        submission.reviewed_at = datetime.now(timezone.utc)
        submission.rejection_reason = None

        member = submission.member
        if member:
            current_points = member.volunteer_points or 0
            member.volunteer_points = current_points + points

        self.db.commit()
        self.db.refresh(submission)
        return self._to_response(submission)

    def reject(self, submission_id: str, admin: User, request: RejectVhsRequest) -> VhsSubmissionResponse:
        submission = (
            self.db.query(VolunteerHoursSubmission)
            .options(joinedload(VolunteerHoursSubmission.member))
            .filter(VolunteerHoursSubmission.id == submission_id)
            .first()
        )
        if not submission:
            raise HTTPException(status_code=404, detail="Volunteer hours submission not found")
        if submission.status != VhsStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only pending submissions can be rejected")

        submission.status = VhsStatus.REJECTED
        submission.rejection_reason = request.reason.strip()
        submission.reviewed_by = admin.id
        submission.reviewed_at = datetime.now(timezone.utc)
        submission.points_awarded = None

        self.db.commit()
        self.db.refresh(submission)
        return self._to_response(submission)

    def get_member_impact(self, user: User) -> VolunteerImpactResponse:
        hours_volunteered = float(
            self.db.query(func.coalesce(func.sum(VolunteerHoursSubmission.hours), 0.0))
            .filter(
                VolunteerHoursSubmission.user_id == user.id,
                VolunteerHoursSubmission.status == VhsStatus.APPROVED,
            )
            .scalar()
            or 0.0
        )
        events_attended = int(
            self.db.query(func.count(VolunteerHoursSubmission.id))
            .filter(
                VolunteerHoursSubmission.user_id == user.id,
                VolunteerHoursSubmission.status == VhsStatus.APPROVED,
            )
            .scalar()
            or 0
        )
        volunteer_points = user.volunteer_points or 0
        higher_ranked = int(
            self.db.query(func.count(User.id))
            .filter(
                User.user_type == UserType.MEMBER,
                User.volunteer_points > volunteer_points,
            )
            .scalar()
            or 0
        )
        total_members = int(
            self.db.query(func.count(User.id))
            .filter(User.user_type == UserType.MEMBER)
            .scalar()
            or 0
        )
        community_rank = higher_ranked + 1 if total_members else 0

        milestones: list[VolunteerMilestoneResponse] = []
        previous_required = 0.0
        current_milestone_id = None
        rank_title = "Member"
        next_rank_title = VOLUNTEER_MILESTONES[0]["name"] if VOLUNTEER_MILESTONES else None
        next_rank_hours = VOLUNTEER_MILESTONES[0]["hours_required"] if VOLUNTEER_MILESTONES else None

        for index, spec in enumerate(VOLUNTEER_MILESTONES):
            required = float(spec["hours_required"])
            next_spec = VOLUNTEER_MILESTONES[index + 1] if index + 1 < len(VOLUNTEER_MILESTONES) else None
            if hours_volunteered >= required:
                status = "completed"
                current_milestone_id = spec["id"]
                rank_title = spec["title"]
                if next_spec:
                    next_rank_title = next_spec["name"]
                    next_rank_hours = float(next_spec["hours_required"])
                else:
                    next_rank_title = None
                    next_rank_hours = required
            elif hours_volunteered >= previous_required:
                status = "in_progress"
                if current_milestone_id is None:
                    next_rank_title = spec["name"]
                    next_rank_hours = required
            else:
                status = "locked"

            hours_completed = min(hours_volunteered, required)
            progress = 1.0 if required <= 0 else min(1.0, hours_volunteered / required)
            milestones.append(
                VolunteerMilestoneResponse(
                    id=spec["id"],
                    name=spec["name"],
                    title=spec["title"],
                    hours_required=required,
                    image_key=spec.get("image_key"),
                    level=spec["level"],
                    status=status,
                    hours_completed=hours_completed,
                    progress=round(progress, 4),
                    next_id=next_spec["id"] if next_spec else None,
                    next_name=next_spec["name"] if next_spec else None,
                    next_hours_required=float(next_spec["hours_required"]) if next_spec else None,
                )
            )
            previous_required = required

        if next_rank_hours and next_rank_hours > 0:
            next_rank_progress = min(1.0, hours_volunteered / next_rank_hours)
        else:
            next_rank_progress = 1.0
        points_to_next = max(0, round((next_rank_hours or 0) * POINTS_PER_HOUR) - volunteer_points)

        submissions = (
            self.db.query(VolunteerHoursSubmission)
            .filter(VolunteerHoursSubmission.user_id == user.id)
            .order_by(VolunteerHoursSubmission.created_at.desc())
            .limit(10)
            .all()
        )
        recent_contributions = [
            VolunteerContributionResponse(
                id=item.id,
                title=item.activity_name,
                hours=item.hours,
                points=item.points_awarded or self._points_for_hours(item.hours),
                volunteer_date=item.volunteer_date,
                status=item.status,
                activity_description=item.activity_description,
                branch=item.branch,
            )
            for item in submissions
        ]

        return VolunteerImpactResponse(
            hours_volunteered=hours_volunteered,
            volunteer_points=volunteer_points,
            events_attended=events_attended,
            community_rank=community_rank,
            total_members=total_members,
            rank_title=rank_title,
            next_rank_title=next_rank_title,
            next_rank_progress=round(next_rank_progress, 4),
            points_to_next=points_to_next,
            current_milestone_id=current_milestone_id,
            milestones=milestones,
            recent_contributions=recent_contributions,
        )
