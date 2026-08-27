import secrets
import string
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.dashboard.dto.request.profilerequest import (
    ProminentProfileCreateRequest,
    ProminentProfileUpdateRequest,
)
from core.dashboard.dto.response.dashboardresponse import (
    PagedProminentProfilesResponse,
    ProminentProfileMessageResponse,
    ProminentProfileResponse,
)
from core.dashboard.model.ProminentProfile import ProminentProfile


class ProminentProfileService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_id(self) -> str:
        return "PROF_" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    def _to_response(self, profile: ProminentProfile) -> ProminentProfileResponse:
        return ProminentProfileResponse(
            id=profile.id,
            full_name=profile.full_name,
            profile_picture_url=profile.photo_url,
            current_branch=profile.country,
            occupation=profile.occupation,
            prominent_headline=profile.headline,
            volunteer_points=0,
            bio=profile.bio,
            country=profile.country,
            era=profile.era,
            category=profile.category,
            sort_order=profile.sort_order or 0,
            is_published=bool(profile.is_published),
        )

    def list_profiles(
        self,
        limit: int = 20,
        category: Optional[str] = None,
    ) -> List[ProminentProfileResponse]:
        query = self.db.query(ProminentProfile).filter(
            ProminentProfile.is_published.is_(True)
        )
        if category:
            query = query.filter(ProminentProfile.category == category.upper())
        profiles = (
            query.order_by(ProminentProfile.sort_order.asc(), ProminentProfile.full_name.asc())
            .limit(limit)
            .all()
        )
        return [self._to_response(profile) for profile in profiles]

    def get_profile(self, profile_id: str, published_only: bool = True) -> ProminentProfileResponse:
        query = self.db.query(ProminentProfile).filter(ProminentProfile.id == profile_id)
        if published_only:
            query = query.filter(ProminentProfile.is_published.is_(True))
        profile = query.first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return self._to_response(profile)

    def list_admin(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[str] = None,
        published_only: Optional[bool] = None,
    ) -> PagedProminentProfilesResponse:
        query = self.db.query(ProminentProfile)
        if category:
            query = query.filter(ProminentProfile.category == category.upper())
        if published_only is not None:
            query = query.filter(ProminentProfile.is_published == published_only)

        total = query.count()
        profiles = (
            query.order_by(ProminentProfile.sort_order.asc(), ProminentProfile.full_name.asc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return PagedProminentProfilesResponse(
            total=total,
            page=page,
            size=size,
            items=[self._to_response(profile) for profile in profiles],
        )

    def create_profile(self, request: ProminentProfileCreateRequest) -> ProminentProfileResponse:
        profile = ProminentProfile(
            id=self._generate_id(),
            full_name=request.full_name.strip(),
            headline=(request.headline or "").strip() or None,
            bio=request.bio.strip(),
            photo_url=(request.photo_url or "").strip() or None,
            country=(request.country or "").strip() or None,
            occupation=(request.occupation or "").strip() or None,
            era=(request.era or "").strip() or None,
            category=request.category.upper(),
            sort_order=request.sort_order or 0,
            is_published=request.is_published,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return self._to_response(profile)

    def update_profile(
        self,
        profile_id: str,
        request: ProminentProfileUpdateRequest,
    ) -> ProminentProfileResponse:
        profile = self.db.query(ProminentProfile).filter(ProminentProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        data = request.dict(exclude_unset=True)
        if "headline" in data:
            profile.headline = (data.pop("headline") or "").strip() or None
        if "photo_url" in data:
            profile.photo_url = (data.pop("photo_url") or "").strip() or None
        if "category" in data and data["category"]:
            data["category"] = data["category"].upper()
        for key, value in data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(profile, key, value)

        self.db.commit()
        self.db.refresh(profile)
        return self._to_response(profile)

    def delete_profile(self, profile_id: str) -> ProminentProfileMessageResponse:
        profile = self.db.query(ProminentProfile).filter(ProminentProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        self.db.delete(profile)
        self.db.commit()
        return ProminentProfileMessageResponse(message="Profile deleted")
