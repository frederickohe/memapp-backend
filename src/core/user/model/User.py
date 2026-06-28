from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey, Boolean, Date, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.notification.model.Notification import Notification
from core.histories.model.history import History
from utilities.dbconfig import Base
from datetime import datetime, date
from typing import List, Optional
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.auth.model.password_reset_token import PasswordResetToken
from core.auth.model.refreshtoken import RefreshToken


class UserStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"

class Gender(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class MembershipType(str, PyEnum):
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"
    VIP = "VIP"
    STANDARD = "STANDARD"

class UserType(str, PyEnum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"

class AdminRole(str, PyEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    NATIONAL_ADMIN = "NATIONAL_ADMIN"
    REGIONAL_ADMIN = "REGIONAL_ADMIN"
    BRANCH_ADMIN = "BRANCH_ADMIN"

class BooleanEnum(str, PyEnum):
    YES = "YES"
    NO = "NO"
    
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, primary_key=True)
    fullname: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String)
    
    # Personal Information
    nationality: Mapped[Optional[str]] = mapped_column(String(100))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String, default=None)
    address: Mapped[Optional[str]] = mapped_column(String(300))
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Membership Information
    membership_type: Mapped[Optional[str]] = mapped_column(String, default=None)
    current_branch: Mapped[Optional[str]] = mapped_column(String(100))
    branch_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("branches.id"), nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    volunteer_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    month_dues_paid_status: Mapped[Optional[str]] = mapped_column(String, default=None)
    year_affiliation_paid_status: Mapped[Optional[str]] = mapped_column(String, default=None)
    
    
    # Professional Information
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    organization_workplace: Mapped[Optional[str]] = mapped_column(String(200))
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON)
    experiences: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Connected Users (other users in the system)
    connected_users: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Social Media Profiles
    facebook_url: Mapped[Optional[str]] = mapped_column(String(200))
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(20))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(200))
    twitter_url: Mapped[Optional[str]] = mapped_column(String(200))
    instagram_url: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Prominent profile (featured on member dashboard)
    is_prominent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prominent_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prominent_headline: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Notification Preferences
    profile_sharing: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    in_app_notification: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    sms_notification: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_type: Mapped[str] = mapped_column(String, nullable=False, default=UserType.MEMBER)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    role_id: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey("roles.id"), nullable=True
    )
    reset_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assigned_branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assigned_region_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("regions.id"), nullable=True)
    assigned_branch_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("branches.id"), nullable=True)

    status: Mapped[UserStatus] = mapped_column(String, nullable=False, default=UserStatus.ACTIVE)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    password_reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        "PasswordResetToken", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user",
        cascade="all, delete-orphan"
    )

    admin_role: Mapped[Optional["Role"]] = relationship(
        "Role",
        back_populates="users",
        foreign_keys=[role_id],
    )

    branch: Mapped[Optional["Branch"]] = relationship(
        "Branch",
        foreign_keys=[branch_id],
        back_populates="members",
    )

    # Removed custom __init__; SQLAlchemy handles defaults and values automatically

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
    
    # Notifications relationship (one-to-many)
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"  # Using dynamic loading for potentially large collections
    )
    
    # Financial Records relationship (one-to-many)
    financial_records: Mapped[List["History"]] = relationship(
        "History",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"  # Using dynamic loading for potentially large collections
    )
    
    # News Posts relationship (one-to-many) - for admins who post news
    news_posts: Mapped[List["News"]] = relationship(
        "News",
        back_populates="admin",
        cascade="all, delete-orphan",
        lazy="dynamic"  # Using dynamic loading for potentially large collections
    )
    
    # Forms created by admin (one-to-many)
    created_forms: Mapped[List["Form"]] = relationship(
        "Form",
        foreign_keys="Form.admin_id",
        back_populates="admin",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Forms assigned to user (one-to-many)
    assigned_forms: Mapped[List["Form"]] = relationship(
        "Form",
        foreign_keys="Form.assigned_user_id",
        back_populates="assigned_user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Form responses submitted by user (one-to-many)
    form_responses: Mapped[List["FormResponse"]] = relationship(
        "FormResponse",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Programs created by user (admin) (one-to-many)
    created_programs: Mapped[List["Program"]] = relationship(
        "Program",
        foreign_keys="Program.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Programs user is participating in (many-to-many)
    participating_programs: Mapped[List["Program"]] = relationship(
        "Program",
        secondary="program_participants",
        back_populates="participants",
        lazy="dynamic"
    )

    volunteer_hours_submissions: Mapped[List["VolunteerHoursSubmission"]] = relationship(
        "VolunteerHoursSubmission",
        foreign_keys="VolunteerHoursSubmission.user_id",
        back_populates="member",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # For security/authentication purposes
    @property
    def password(self):
        return self.hashed_password

    @property
    def is_active(self):
        return self.enabled

    @property
    def is_admin(self) -> bool:
        return self.user_type == UserType.ADMIN

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)