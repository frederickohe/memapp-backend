from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from core.branches.dto.request.branch_requests import (
    AssignPresidentRequest,
    CreateBranchRequest,
    CreateRegionRequest,
    UpdateBranchRequest,
    UpdateRegionRequest,
)
from core.branches.dto.response.branch_responses import (
    BranchListResponse,
    BranchPresidentSummary,
    BranchResponse,
    RegionListResponse,
    RegionResponse,
)
from core.branches.model.Branch import Branch
from core.branches.model.Region import Region
from core.user.model.User import User, UserType
from utilities.id_helper import generate_id


class BranchService:
    def __init__(self, db: Session):
        self.db = db

    def _branch_to_response(self, branch: Branch) -> BranchResponse:
        president = None
        if branch.president:
            president = BranchPresidentSummary(
                id=branch.president.id,
                full_name=branch.president.fullname,
                email=branch.president.email,
                phone=branch.president.phone_number,
            )
        return BranchResponse(
            id=branch.id,
            region_id=branch.region_id,
            region_name=branch.region.name if branch.region else "",
            name=branch.name,
            address=branch.address,
            lat=branch.lat,
            lng=branch.lng,
            president=president,
            is_active=branch.is_active,
            created_at=branch.created_at,
        )

    def list_regions(self, active_only: bool = True) -> RegionListResponse:
        query = self.db.query(Region).order_by(Region.name.asc())
        if active_only:
            query = query.filter(Region.is_active.is_(True))
        regions = query.all()
        return RegionListResponse(
            regions=[
                RegionResponse(
                    id=r.id,
                    name=r.name,
                    is_active=r.is_active,
                    branch_count=len([b for b in r.branches if b.is_active]),
                    created_at=r.created_at,
                )
                for r in regions
            ]
        )

    def create_region(self, request: CreateRegionRequest) -> RegionResponse:
        existing = self.db.query(Region).filter(Region.name.ilike(request.name.strip())).first()
        if existing:
            raise HTTPException(status_code=400, detail="Region with this name already exists")

        region = Region(id=generate_id(), name=request.name.strip(), is_active=True)
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return RegionResponse(
            id=region.id,
            name=region.name,
            is_active=region.is_active,
            branch_count=0,
            created_at=region.created_at,
        )

    def update_region(self, region_id: str, request: UpdateRegionRequest) -> RegionResponse:
        region = self.db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")

        if request.name is not None:
            region.name = request.name.strip()
        if request.is_active is not None:
            region.is_active = request.is_active

        self.db.commit()
        self.db.refresh(region)
        branch_count = self.db.query(Branch).filter(Branch.region_id == region.id, Branch.is_active.is_(True)).count()
        return RegionResponse(
            id=region.id,
            name=region.name,
            is_active=region.is_active,
            branch_count=branch_count,
            created_at=region.created_at,
        )

    def list_branches(
        self,
        region_id: Optional[str] = None,
        active_only: bool = True,
    ) -> BranchListResponse:
        query = (
            self.db.query(Branch)
            .options(joinedload(Branch.region), joinedload(Branch.president))
            .order_by(Branch.name.asc())
        )
        if active_only:
            query = query.filter(Branch.is_active.is_(True))
        if region_id:
            query = query.filter(Branch.region_id == region_id)

        branches = query.all()
        return BranchListResponse(branches=[self._branch_to_response(b) for b in branches])

    def get_branch(self, branch_id: str) -> BranchResponse:
        branch = (
            self.db.query(Branch)
            .options(joinedload(Branch.region), joinedload(Branch.president))
            .filter(Branch.id == branch_id)
            .first()
        )
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
        return self._branch_to_response(branch)

    def create_branch(self, request: CreateBranchRequest) -> BranchResponse:
        region = self.db.query(Region).filter(Region.id == request.region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")

        if request.president_id:
            self._validate_president(request.president_id)

        branch = Branch(
            id=generate_id(),
            region_id=request.region_id,
            name=request.name.strip(),
            address=request.address,
            lat=request.lat,
            lng=request.lng,
            president_id=request.president_id,
            is_active=True,
        )
        self.db.add(branch)
        self.db.commit()
        return self.get_branch(branch.id)

    def update_branch(self, branch_id: str, request: UpdateBranchRequest) -> BranchResponse:
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        if request.region_id is not None:
            region = self.db.query(Region).filter(Region.id == request.region_id).first()
            if not region:
                raise HTTPException(status_code=404, detail="Region not found")
            branch.region_id = request.region_id

        if request.name is not None:
            branch.name = request.name.strip()
        if request.address is not None:
            branch.address = request.address
        if request.lat is not None:
            branch.lat = request.lat
        if request.lng is not None:
            branch.lng = request.lng
        if request.president_id is not None:
            if request.president_id:
                self._validate_president(request.president_id)
            branch.president_id = request.president_id or None
        if request.is_active is not None:
            branch.is_active = request.is_active

        branch.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self.get_branch(branch_id)

    def assign_president(self, branch_id: str, request: AssignPresidentRequest) -> BranchResponse:
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        if request.president_id:
            self._validate_president(request.president_id)
            branch.president_id = request.president_id
        else:
            branch.president_id = None

        branch.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self.get_branch(branch_id)

    def _validate_president(self, user_id: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="President user not found")
        if user.user_type != UserType.MEMBER:
            raise HTTPException(status_code=400, detail="Branch president must be a member user")
        return user
