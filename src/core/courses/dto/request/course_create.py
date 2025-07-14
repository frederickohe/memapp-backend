# dto/request/create_course.py
from pydantic import BaseModel
from datetime import date
from typing import Optional
from core.courses.model.Course import CourseStatus, CourseLevel

class CourseCreateRequest(BaseModel):
    title: str
    description: str
    short_description: Optional[str] = None
    admission_start_date: Optional[date] = None
    admission_end_date: Optional[date] = None
    application_link: Optional[str] = None
    duration_weeks: int
    weekly_commitment_hours: int = 5
    level: CourseLevel = CourseLevel.BEGINNER
    status: CourseStatus = CourseStatus.UPCOMING
    thumbnail_url: Optional[str] = None
    promo_video_url: Optional[str] = None