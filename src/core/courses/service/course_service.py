from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from core.courses.model.Course import Course, CourseStatus, CourseLevel, CourseTimeline, CourseEnrollment
from core.courses.dto.request.course_create import CourseCreateRequest
from core.courses.dto.request.course_update import CourseUpdateRequest
from core.courses.dto.response.paged_courses import PagedCourseResponse
from core.courses.dto.response.course_response import (
    CourseResponse,
    CourseWithTimelineResponse,
    EnrollmentResponse,
    ProgressResponse
)
from core.user.model.User import User
import logging

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self, db: Session):
        self.db = db

    def create_course(self, course_data: CourseCreateRequest, created_by: str) -> CourseResponse:
        """Create a new course"""
        try:
            course = Course(
                id=course_data.id,
                title=course_data.title,
                slug=course_data.slug,
                description=course_data.description,
                short_description=course_data.short_description,
                admission_start_date=course_data.admission_start_date,
                admission_end_date=course_data.admission_end_date,
                application_link=course_data.application_link,
                duration_weeks=course_data.duration_weeks,
                weekly_commitment_hours=course_data.weekly_commitment_hours,
                level=course_data.level,
                status=course_data.status,
                thumbnail_url=course_data.thumbnail_url,
                promo_video_url=course_data.promo_video_url,
                created_by=created_by
            )
            
            self.db.add(course)
            self.db.commit()
            self.db.refresh(course)
            
            return CourseResponse.from_orm(course)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating course: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to create course")

    def get_all_courses_paged(self, page: int, size: int, 
                            status: Optional[CourseStatus] = None,
                            level: Optional[CourseLevel] = None) -> PagedCourseResponse:
        """Get paginated list of courses with optional filtering"""
        try:
            query = self.db.query(Course)
            
            if status:
                query = query.filter(Course.status == status)
            if level:
                query = query.filter(Course.level == level)
                
            total = query.count()
            courses = query.offset((page - 1) * size).limit(size).all()
            
            return PagedCourseResponse(
                total=total,
                page=page,
                size=size,
                courses=[CourseResponse.from_orm(course) for course in courses]
            )
            
        except Exception as e:
            logger.error(f"Error fetching courses: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch courses")

    def get_course_by_id(self, course_id: str) -> CourseResponse:
        """Get single course by ID"""
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return CourseResponse.from_orm(course)

    def get_course_with_timeline(self, course_id: str) -> CourseWithTimelineResponse:
        """Get course with its timeline"""
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
            
        timeline = self.db.query(CourseTimeline)\
                        .filter(CourseTimeline.course_id == course_id)\
                        .order_by(CourseTimeline.week_number)\
                        .all()
                        
        return CourseWithTimelineResponse(
            course=CourseResponse.from_orm(course),
            timeline=timeline
        )

    def update_course(self, course_id: str, course_data: CourseUpdateRequest) -> CourseResponse:
        """Update course details"""
        try:
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
                
            for field, value in course_data.dict(exclude_unset=True).items():
                setattr(course, field, value)
                
            course.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(course)
            
            return CourseResponse.from_orm(course)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating course: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to update course")

    def delete_course(self, course_id: str) -> None:
        """Delete a course"""
        try:
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
                
            self.db.delete(course)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting course: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to delete course")

    def enroll_user(self, user_email: str, course_id: str) -> EnrollmentResponse:
        """Enroll a user in a course"""
        try:
            # Check if course exists
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
                
            # Check if user exists
            user = self.db.query(User).filter(User.email == user_email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            # Check if already enrolled
            existing_enrollment = self.db.query(CourseEnrollment)\
                                      .filter(CourseEnrollment.user_id == user.id,
                                             CourseEnrollment.course_id == course_id)\
                                      .first()
            if existing_enrollment:
                raise HTTPException(status_code=400, detail="User already enrolled in this course")
                
            # Create new enrollment
            enrollment = CourseEnrollment(
                user_id=user.id,
                course_id=course_id,
                enrollment_date=datetime.utcnow()
            )
            
            self.db.add(enrollment)
            self.db.commit()
            self.db.refresh(enrollment)
            
            return EnrollmentResponse(
                id=enrollment.id,
                user_id=enrollment.user_id,
                course_id=enrollment.course_id,
                enrollment_date=enrollment.enrollment_date,
                current_progress=enrollment.current_progress,
                is_active=enrollment.is_active
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error enrolling user: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to enroll user")

    def get_course_enrollments(self, course_id: str) -> List[EnrollmentResponse]:
        """Get all enrollments for a course"""
        enrollments = self.db.query(CourseEnrollment)\
                           .filter(CourseEnrollment.course_id == course_id)\
                           .all()
                           
        return [
            EnrollmentResponse(
                id=e.id,
                user_id=e.user_id,
                course_id=e.course_id,
                enrollment_date=e.enrollment_date,
                current_progress=e.current_progress,
                is_active=e.is_active
            ) for e in enrollments
        ]

    def get_user_enrollments(self, user_email: str) -> List[EnrollmentResponse]:
        """Get all courses a user is enrolled in"""
        user = self.db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        enrollments = self.db.query(CourseEnrollment)\
                          .filter(CourseEnrollment.user_id == user.id)\
                          .all()
                          
        return [
            EnrollmentResponse(
                id=e.id,
                user_id=e.user_id,
                course_id=e.course_id,
                enrollment_date=e.enrollment_date,
                current_progress=e.current_progress,
                is_active=e.is_active
            ) for e in enrollments
        ]

    def get_user_progress(self, user_email: str, course_id: str) -> ProgressResponse:
        """Get user's progress in a course"""
        user = self.db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        enrollment = self.db.query(CourseEnrollment)\
                         .filter(CourseEnrollment.user_id == user.id,
                                CourseEnrollment.course_id == course_id)\
                         .first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="User is not enrolled in this course")
            
        return ProgressResponse(
            course_id=course_id,
            user_id=user.id,
            current_progress=enrollment.current_progress,
            last_accessed=datetime.utcnow()  # You might want to track this separately
        )