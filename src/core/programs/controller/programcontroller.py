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
from core.programs.model.program import Program
from core.user.model.User import User

# DTO Models
from core.programs.dto.response.programresponse import (
    ProgramResponse,
    ProgramDetailResponse,
    PagedProgramResponse,
    ProgramEnrollmentResponse,
    ProgramEnrollmentsListResponse,
    UserProgramsResponse,
    MessageResponse
)
from core.programs.dto.request.programrequest import (
    ProgramCreateRequest,
    ProgramUpdateRequest,
    ProgramEnrollmentRequest,
    ProgramEnrollmentUpdateRequest
)

from core.programs.service.programservice import ProgramService
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
program_routes = APIRouter()


# ===================== PROGRAM MANAGEMENT ENDPOINTS (Admin Only) =====================

@program_routes.post("/create", response_model=ProgramDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    request: ProgramCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new program (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can create programs")
    
    service = ProgramService(db)
    
    program = service.create_program(
        created_by=current_user.id,
        title=request.title,
        description=request.description,
        starting_date=request.starting_date,
        end_date=request.end_date,
        register_url=request.register_url,
        youtube_url=request.youtube_url,
        thumbnail_url=request.thumbnail_url,
        category=request.category,
        location=request.location,
        capacity=request.capacity,
        form_ids=request.form_ids,
        is_published=request.is_published,
        allow_registration=request.allow_registration,
        metadata=request.metadata
    )
    
    return program


@program_routes.get("/{program_id}", response_model=ProgramDetailResponse)
async def get_program(
    program_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific program by ID"""
    service = ProgramService(db)
    return service.get_program(program_id)


@program_routes.get("", response_model=PagedProgramResponse)
async def list_programs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all programs created by the admin with pagination"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can view all programs")
    
    service = ProgramService(db)
    return service.get_all_programs(
        page=page,
        size=size,
        status=status,
        category=category,
        is_published=is_published,
        created_by=current_user.id
    )


@program_routes.put("/{program_id}", response_model=ProgramDetailResponse)
async def update_program(
    program_id: str,
    request: ProgramUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a program (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can update programs")
    
    service = ProgramService(db)
    
    program = service.update_program(
        program_id=program_id,
        created_by=current_user.id,
        title=request.title,
        description=request.description,
        starting_date=request.starting_date,
        end_date=request.end_date,
        register_url=request.register_url,
        youtube_url=request.youtube_url,
        thumbnail_url=request.thumbnail_url,
        category=request.category,
        location=request.location,
        capacity=request.capacity,
        form_ids=request.form_ids,
        is_published=request.is_published,
        allow_registration=request.allow_registration,
        metadata=request.metadata
    )
    
    return program


@program_routes.delete("/{program_id}", response_model=MessageResponse)
async def delete_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a program (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete programs")
    
    service = ProgramService(db)
    result = service.delete_program(program_id, current_user.id)
    return MessageResponse(message=result["message"])


# ===================== PROGRAM ENROLLMENT ENDPOINTS =====================

@program_routes.post("/{program_id}/enroll", response_model=ProgramEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_program(
    program_id: str,
    request: ProgramEnrollmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a program by submitting a form"""
    service = ProgramService(db)
    
    response = service.enroll_user(
        program_id=program_id,
        user_id=request.user_id,
        form_id=request.form_id,
        form_data=request.form_data,
        notes=request.notes
    )
    
    return response


@program_routes.post("/{program_id}/self-enroll", response_model=ProgramEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def self_enroll_in_program(
    program_id: str,
    request: ProgramEnrollmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Self-enroll in a program by submitting a form"""
    service = ProgramService(db)
    
    response = service.enroll_user(
        program_id=program_id,
        user_id=current_user.id,
        form_id=request.form_id,
        form_data=request.form_data,
        notes=request.notes
    )
    
    return response


@program_routes.post("/{program_id}/unenroll", response_model=MessageResponse)
async def unenroll_from_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unenroll from a program"""
    service = ProgramService(db)
    result = service.unenroll_user(program_id, current_user.id)
    return MessageResponse(message=result["message"])


@program_routes.get("/{program_id}/enrollments", response_model=ProgramEnrollmentsListResponse)
async def get_program_enrollments(
    program_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all enrollments for a program (Admin only - program creator)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can view enrollments")
    
    service = ProgramService(db)
    return service.get_program_enrollments(
        program_id=program_id,
        created_by=current_user.id,
        page=page,
        size=size
    )


@program_routes.put("/enrollments/{enrollment_id}", response_model=ProgramEnrollmentResponse)
async def update_enrollment(
    program_id: str,
    enrollment_id: str,
    request: ProgramEnrollmentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update form response data (Admin only)"""
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Only admins can update enrollments")
    
    service = ProgramService(db)
    return service.update_enrollment_status(
        form_response_id=enrollment_id,
        program_id=program_id,
        created_by=current_user.id,
        completion_percentage=request.completion_percentage,
        notes=request.notes
    )


# ===================== PUBLIC PROGRAM ENDPOINTS =====================

@program_routes.get("/public/browse", response_model=PagedProgramResponse)
async def list_public_programs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all published programs (no authentication required)"""
    service = ProgramService(db)
    return service.get_public_programs(page=page, size=size, category=category)


# ===================== USER PROGRAM ENDPOINTS =====================

@program_routes.get("/my-programs", response_model=UserProgramsResponse)
async def get_my_programs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all programs the current user is enrolled in"""
    service = ProgramService(db)
    return service.get_user_programs(
        user_id=current_user.id,
        page=page,
        size=size
    )
