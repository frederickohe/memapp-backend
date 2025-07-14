# dto/response/course_response.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from core.courses.model.Course import CourseStatus, CourseLevel

class CourseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    short_description: Optional[str]
    status: CourseStatus
    level: CourseLevel
    duration_weeks: int
    thumbnail_url: Optional[str]
    created_at: datetime

class TimelineWeekResponse(BaseModel):
    week_number: int
    title: str
    description: Optional[str]
    target_completion_percentage: float

class CourseWithTimelineResponse(CourseResponse):
    timeline: List[TimelineWeekResponse]

class EnrollmentResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    enrollment_date: datetime
    current_progress: float
    is_active: bool

class ProgressResponse(BaseModel):
    course_id: str
    overall_progress: float
