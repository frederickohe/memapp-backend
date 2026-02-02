from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from core.auth.service.sessiondriver import SessionDriver, TokenData
from fastapi_jwt_auth import AuthJWT
from core.exceptions import *
import jwt

from utilities.dbconfig import SessionLocal
from sqlalchemy.orm import Session
import logging
from core.forms.model.Form import Form
from core.user.model.User import User

# DTO Models
from core.forms.dto.response.formresponse import (
    FormResponse,
    FormDetailResponse,
    FormResponseDataResponse,
    FormResponsesListResponse,
    PagedFormResponse,
    MessageResponse
)
from core.forms.dto.request.formrequest import (
    FormCreateRequest,
    FormUpdateRequest,
    FormResponseSubmitRequest
)

from core.forms.service.formservice import FormService
from fastapi_jwt_auth.exceptions import MissingTokenError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Helper functions
def validate_token(authjwt: AuthJWT = Depends()):
    try:
        authjwt.jwt_required()
        return authjwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token expired. Please log in again."
        )
    except MissingTokenError:
        raise HTTPException(
            status_code=401,
            detail="No token found. Please create an account and log in.",
        )
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_role(user: User) -> bool:
    """Check if user has admin role"""
    # You may need to adjust based on your User model
    return getattr(user, 'is_admin', False) or getattr(user, 'role', None) == 'admin'


def get_current_user(authjwt: AuthJWT = Depends(validate_token), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
    try:
        token_data = authjwt.get_jwt()
        user_id = token_data.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Unauthorized")


# Create router
form_routes = APIRouter(prefix="/api/forms", tags=["Forms"])


# ===================== FORM MANAGEMENT ENDPOINTS (Admin Only) =====================

@form_routes.post("/create", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    request: FormCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new form (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can create forms")
    
    service = FormService(db)
    
    # Convert field request objects to dictionaries
    fields_data = [field.dict() for field in request.fields]
    
    form = service.create_form(
        admin_id=current_user.id,
        title=request.title,
        description=request.description,
        assignment_type=request.assignment_type,
        fields=fields_data,
        program_id=request.program_id,
        assigned_user_id=request.assigned_user_id,
        is_active=request.is_active
    )
    
    return form


@form_routes.get("/{form_id}", response_model=FormResponse)
async def get_form(
    form_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific form by ID"""
    service = FormService(db)
    return service.get_form(form_id)


@form_routes.get("/{form_id}/detail", response_model=FormDetailResponse)
async def get_form_detail(
    form_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed form information with response count"""
    service = FormService(db)
    return service.get_form_detail(form_id)


@form_routes.get("", response_model=PagedFormResponse)
async def list_forms(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    assignment_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all forms created by the admin with pagination"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can view all forms")
    
    service = FormService(db)
    return service.get_all_forms(
        page=page,
        size=size,
        admin_id=current_user.id,
        assignment_type=assignment_type,
        is_active=is_active
    )


@form_routes.put("/{form_id}", response_model=FormResponse)
async def update_form(
    form_id: str,
    request: FormUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a form (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can update forms")
    
    service = FormService(db)
    
    # Convert field request objects to dictionaries if provided
    fields_data = None
    if request.fields:
        fields_data = [field.dict() for field in request.fields]
    
    form = service.update_form(
        form_id=form_id,
        admin_id=current_user.id,
        title=request.title,
        description=request.description,
        assignment_type=request.assignment_type,
        fields=fields_data,
        program_id=request.program_id,
        assigned_user_id=request.assigned_user_id,
        is_active=request.is_active
    )
    
    return form


@form_routes.delete("/{form_id}", response_model=MessageResponse)
async def delete_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a form (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete forms")
    
    service = FormService(db)
    result = service.delete_form(form_id, current_user.id)
    return MessageResponse(message=result["message"])


# ===================== FORM RESPONSE ENDPOINTS =====================

@form_routes.post("/{form_id}/submit", response_model=FormResponseDataResponse, status_code=status.HTTP_201_CREATED)
async def submit_form_response(
    form_id: str,
    request: FormResponseSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a response to a form"""
    service = FormService(db)
    
    response = service.submit_form_response(
        form_id=form_id,
        user_id=current_user.id,
        data=request.data,
        notes=request.notes
    )
    
    return response


@form_routes.get("/{form_id}/responses", response_model=FormResponsesListResponse)
async def get_form_responses(
    form_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all responses to a form (Admin only - form owner)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can view form responses")
    
    service = FormService(db)
    return service.get_form_responses(
        form_id=form_id,
        admin_id=current_user.id,
        page=page,
        size=size
    )


# ===================== PUBLIC FORM ENDPOINTS =====================

@form_routes.get("/public/list", response_model=PagedFormResponse)
async def list_public_forms(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all public forms (no authentication required)"""
    service = FormService(db)
    return service.get_public_forms(page=page, size=size)


# ===================== USER-ASSIGNED FORM ENDPOINTS =====================

@form_routes.get("/my-forms", response_model=PagedFormResponse)
async def get_my_forms(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all forms assigned to the current user"""
    service = FormService(db)
    return service.get_user_form_responses(
        user_id=current_user.id,
        page=page,
        size=size
    )
