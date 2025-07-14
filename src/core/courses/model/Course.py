from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from datetime import datetime, date
from enum import Enum
from utilities.dbconfig import Base
from sqlalchemy.sql import func

class CourseStatus(str, Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class CourseLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Admission details
    admission_start_date: Mapped[Optional[date]] = mapped_column(DateTime)
    admission_end_date: Mapped[Optional[date]] = mapped_column(DateTime)
    application_link: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Course details
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    weekly_commitment_hours: Mapped[int] = mapped_column(Integer, default=5)
    level: Mapped[CourseLevel] = mapped_column(String(20), default=CourseLevel.BEGINNER)
    status: Mapped[CourseStatus] = mapped_column(String(20), default=CourseStatus.UPCOMING)
    
    # Media
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(200))
    promo_video_url: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    timeline: Mapped[List["CourseTimeline"]] = relationship(
        "CourseTimeline", 
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseTimeline.week_number"
    )
    
    enrollments: Mapped[List["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title})>"

class CourseTimeline(Base):
    __tablename__ = "course_timelines"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, unique=True, nullable=False)
    course_id: Mapped[str] = mapped_column(String(20), ForeignKey('courses.id'), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    learning_objectives: Mapped[Optional[str]] = mapped_column(Text)
    resources: Mapped[Optional[str]] = mapped_column(Text)  # Could be JSON in production
    
    # Progress tracking
    target_completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timestamps
    start_date: Mapped[Optional[date]] = mapped_column(DateTime)
    end_date: Mapped[Optional[date]] = mapped_column(DateTime)
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="timeline")
    
    def __repr__(self):
        return f"<CourseTimeline(week={self.week_number}, title={self.title})>"

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True, unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey('users.id'), nullable=False)
    course_id: Mapped[str] = mapped_column(String(20), ForeignKey('courses.id'), nullable=False)
    
    # Enrollment details
    enrollment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    current_progress: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<CourseEnrollment(user={self.user_id}, course={self.course_id})>"