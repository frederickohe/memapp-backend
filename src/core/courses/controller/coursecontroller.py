from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
import jwt
from pydantic import BaseModel
from core.auth.service.sessiondriver import SessionDriver, TokenData
from fastapi_jwt_auth import AuthJWT
from core.courses.dto.response.message_response import MessageResponse
from core.exceptions import *
from utilities.dbconfig import SessionLocal
from sqlalchemy.orm import Session
import logging

# Import your models and services
from core.courses.model.Course import Course, CourseStatus, CourseLevel
from core.courses.service.course_service import CourseService
from core.courses.dto.request.course_create import CourseCreateRequest
from core.courses.dto.request.course_update import CourseUpdateRequest
from core.courses.dto.response.paged_courses import PagedCourseResponse
from core.courses.dto.response.course_response import (
    CourseResponse,
    CourseWithTimelineResponse,
    EnrollmentResponse,
    ProgressResponse
)

# Reuse your existing auth dependencies
from core.user.controller.usercontroller import validate_token, get_db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

course_routes = APIRouter()

@course_routes.post("/", response_model=CourseResponse)
def create_course(
    course_data: CourseCreateRequest,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Create a new course (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    # Add admin check here if needed
    # if not is_admin(current_user_email):
    #     raise HTTPException(status_code=403, detail="Only admins can create courses")
    
    return course_service.create_course(course_data, created_by=current_user_email)

@course_routes.get("/", response_model=PagedCourseResponse)
def get_all_courses(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[CourseStatus] = Query(None),
    level: Optional[CourseLevel] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all courses with pagination and optional filtering"""
    course_service = CourseService(db)
    return course_service.get_all_courses_paged(page, size, status, level)

@course_routes.get("/{course_id}", response_model=CourseWithTimelineResponse)
def get_course_details(
    course_id: str,
    db: Session = Depends(get_db)
):
    """Get course details including timeline"""
    course_service = CourseService(db)
    course = course_service.get_course_with_timeline(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@course_routes.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: str,
    course_data: CourseUpdateRequest,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Update course details (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    # Add admin check here if needed
    return course_service.update_course(course_id, course_data)

@course_routes.delete("/{course_id}", response_model=MessageResponse)
def delete_course(
    course_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Delete a course (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    # Add admin check here if needed
    course_service.delete_course(course_id)
    return {"message": "Course deleted successfully"}

@course_routes.post("/{course_id}/enroll", response_model=EnrollmentResponse)
def enroll_in_course(
    course_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Enroll the current user in a course"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    return course_service.enroll_user(current_user_email, course_id)

@course_routes.get("/{course_id}/enrollments", response_model=List[EnrollmentResponse])
def get_course_enrollments(
    course_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Get all enrollments for a course (Admin only)"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    # Add admin check here if needed
    return course_service.get_course_enrollments(course_id)

@course_routes.get("/me/enrollments", response_model=List[EnrollmentResponse])
def get_my_enrollments(
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Get current user's course enrollments"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    return course_service.get_user_enrollments(current_user_email)

@course_routes.get("/me/progress/{course_id}", response_model=ProgressResponse)
def get_my_progress(
    course_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    """Get current user's progress in a course"""
    current_user_email = authjwt.get_jwt_subject()
    course_service = CourseService(db)
    
    return course_service.get_user_progress(current_user_email, course_id)