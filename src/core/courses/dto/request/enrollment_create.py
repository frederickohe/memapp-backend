from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class EnrollmentRequest(BaseModel):
    id: str
    user_id: str
    course_id: str
    enrollment_date: datetime
    current_progress: float
    is_active: bool