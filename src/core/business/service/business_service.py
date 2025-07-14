import secrets
import string
from fastapi import HTTPException
from sqlalchemy.orm import Session
from core.user.model.User import User
from core.business.model.Business import Business
from core.exceptions import *
from core.business.dto.request.businessupdate import BusinessUpdateRequest
from core.business.dto.response.business_response import BusinessResponse
from core.user.dto.response.message_response import MessageResponse
from typing import Optional
from datetime import datetime

class BusinessService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_business(self, email: str) -> BusinessResponse:
        """Get business information for the current user"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.business:
            raise HTTPException(status_code=404, detail="Business information not found for this user")
            
        return self._business_to_response(user.business)

    def update_user_business(self, email: str, business_data: BusinessUpdateRequest) -> BusinessResponse:
        """Update business information for the current user"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.business:
            # Create new business if it doesn't exist
            business = Business(
                id=self._generate_business_id(),
                user_id=user.id,
                **business_data.dict(exclude_unset=True)
            )
            self.db.add(business)
        else:
            # Update existing business
            business = user.business
            for field, value in business_data.dict(exclude_unset=True).items():
                setattr(business, field, value)
            business.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business)
        return self._business_to_response(business)

    def get_business_by_user_id(self, user_id: str) -> BusinessResponse:
        """Get business information by user ID"""
        business = self._get_business_by_user_id(user_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business information not found")
        return self._business_to_response(business)

    def update_business_by_user_id(self, user_id: str, business_data: BusinessUpdateRequest) -> BusinessResponse:
        """Update business information by user ID"""
        business = self._get_business_by_user_id(user_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business information not found")
            
        for field, value in business_data.dict(exclude_unset=True).items():
            setattr(business, field, value)
        business.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business)
        return self._business_to_response(business)

    def _get_business_by_user_id(self, user_id: str) -> Optional[Business]:
        """Internal method to get business entity by user ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return user.business

    def _business_to_response(self, business: Business) -> BusinessResponse:
        """Convert Business model to BusinessResponse DTO"""
        return BusinessResponse(
            id=business.id,
            user_id=business.user_id,
            name=business.name,
            description=business.description,
            category=business.category,
            website=business.website,
            address=business.address,
            city=business.city,
            state=business.state,
            country=business.country,
            postal_code=business.postal_code,
            tax_id=business.tax_id,
            registration_number=business.registration_number,
            established_date=business.established_date,
            created_at=business.created_at,
            updated_at=business.updated_at
        )

    def _generate_business_id(self) -> str:
        """Generate a unique business ID"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(16))