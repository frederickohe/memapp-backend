from typing import List
from pydantic import BaseModel

from core.courses.dto.response.course_response import CourseResponse


class PagedCourseResponse(BaseModel):
    total: int
    page: int
    size: int
    courses: List[CourseResponse]