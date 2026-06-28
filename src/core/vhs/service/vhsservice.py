import math
import secrets
import string
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from core.user.model.User import User, UserType
from core.vhs.dto.request.vhs_requests import RejectVhsRequest, SubmitVolunteerHoursRequest
from core.vhs.dto.response.vhs_responses import VhsSubmissionListResponse, VhsSubmissionResponse
from core.vhs.model.volunteer_hours_submission import VhsStatus, VolunteerHoursSubmission

POINTS_PER_HOUR = 10


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
    ) -> VhsSubmissionListResponse:
        query = (
            self.db.query(VolunteerHoursSubmission)
            .options(joinedload(VolunteerHoursSubmission.member))
            .order_by(VolunteerHoursSubmission.created_at.desc())
        )
        if status and status != "all":
            query = query.filter(VolunteerHoursSubmission.status == status)

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
