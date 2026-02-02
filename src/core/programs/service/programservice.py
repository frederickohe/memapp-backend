from datetime import datetime
import secrets
import string
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from fastapi import HTTPException, status
from core.programs.model.program import Program, ProgramEnrollment, ProgramStatus, program_participants_association, program_forms_association
from core.user.model.User import User
from core.forms.model.Form import Form
from core.programs.dto.response.programresponse import (
    ProgramResponse,
    ProgramDetailResponse,
    PagedProgramResponse,
    ProgramEnrollmentResponse,
    ProgramEnrollmentsListResponse,
    UserProgramsResponse,
    ProgramFormResponse,
    UserBasicResponse,
    FormFieldResponse
)


class ProgramService:
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_program_id(self) -> str:
        """Generate a unique program ID"""
        return "PROG_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def _generate_enrollment_id(self) -> str:
        """Generate a unique enrollment ID"""
        return "ENRL_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def _get_program_status(self, program: Program) -> ProgramStatus:
        """Determine program status based on dates"""
        now = datetime.utcnow()
        
        if program.status == ProgramStatus.CANCELLED:
            return ProgramStatus.CANCELLED
        
        if now < program.starting_date:
            return ProgramStatus.UPCOMING
        elif now > program.end_date:
            return ProgramStatus.COMPLETED
        else:
            return ProgramStatus.ONGOING
    
    def create_program(
        self,
        created_by: str,
        title: str,
        description: Optional[str],
        starting_date: datetime,
        end_date: datetime,
        register_url: Optional[str] = None,
        youtube_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        capacity: Optional[int] = None,
        form_ids: Optional[List[str]] = None,
        is_published: bool = False,
        allow_registration: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProgramDetailResponse:
        """Create a new program"""
        # Verify creator exists
        creator = self.db.query(User).filter(User.id == created_by).first()
        if not creator:
            raise HTTPException(status_code=404, detail="Creator user not found")
        
        # Validate dates
        if end_date <= starting_date:
            raise HTTPException(status_code=400, detail="End date must be after starting date")
        
        # Create program record
        program = Program(
            id=self._generate_program_id(),
            title=title,
            description=description,
            starting_date=starting_date,
            end_date=end_date,
            register_url=register_url,
            youtube_url=youtube_url,
            thumbnail_url=thumbnail_url,
            category=category,
            location=location,
            capacity=capacity,
            created_by=created_by,
            is_published=is_published,
            allow_registration=allow_registration,
            metadata=metadata,
            status=self._get_program_status(Program(
                starting_date=starting_date,
                end_date=end_date,
                status=ProgramStatus.UPCOMING,
                title="",
                created_by=""
            ))
        )
        
        # Add forms if provided
        if form_ids:
            forms = self.db.query(Form).filter(Form.id.in_(form_ids)).all()
            if len(forms) != len(form_ids):
                raise HTTPException(status_code=404, detail="One or more forms not found")
            program.forms = forms
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        return self._convert_program_to_detail_dto(program)
    
    def get_program(self, program_id: str) -> ProgramDetailResponse:
        """Get a specific program by ID"""
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        return self._convert_program_to_detail_dto(program)
    
    def get_all_programs(
        self,
        page: int = 1,
        size: int = 10,
        status: Optional[str] = None,
        category: Optional[str] = None,
        is_published: Optional[bool] = None,
        created_by: Optional[str] = None
    ) -> PagedProgramResponse:
        """Get all programs with filters and pagination"""
        query = self.db.query(Program)
        
        # Apply filters
        if created_by:
            query = query.filter(Program.created_by == created_by)
        if category:
            query = query.filter(Program.category == category)
        if is_published is not None:
            query = query.filter(Program.is_published == is_published)
        if status:
            query = query.filter(Program.status == status)
        
        # Sort by most recent first
        query = query.order_by(desc(Program.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        programs = query.offset(skip).limit(size).all()
        
        items = [self._convert_program_to_detail_dto(p) for p in programs]
        
        return PagedProgramResponse(total=total, page=page, size=size, items=items)
    
    def update_program(
        self,
        program_id: str,
        created_by: str,
        **kwargs
    ) -> ProgramDetailResponse:
        """Update a program (admin only)"""
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        # Verify user owns the program
        if program.created_by != created_by:
            raise HTTPException(status_code=403, detail="Not authorized to update this program")
        
        # Update fields
        if "title" in kwargs and kwargs["title"] is not None:
            program.title = kwargs["title"]
        if "description" in kwargs and kwargs["description"] is not None:
            program.description = kwargs["description"]
        if "starting_date" in kwargs and kwargs["starting_date"] is not None:
            program.starting_date = kwargs["starting_date"]
        if "end_date" in kwargs and kwargs["end_date"] is not None:
            # Validate date
            if kwargs["end_date"] <= program.starting_date:
                raise HTTPException(status_code=400, detail="End date must be after starting date")
            program.end_date = kwargs["end_date"]
        if "register_url" in kwargs:
            program.register_url = kwargs["register_url"]
        if "youtube_url" in kwargs:
            program.youtube_url = kwargs["youtube_url"]
        if "thumbnail_url" in kwargs:
            program.thumbnail_url = kwargs["thumbnail_url"]
        if "category" in kwargs:
            program.category = kwargs["category"]
        if "location" in kwargs:
            program.location = kwargs["location"]
        if "capacity" in kwargs:
            program.capacity = kwargs["capacity"]
        if "is_published" in kwargs and kwargs["is_published"] is not None:
            program.is_published = kwargs["is_published"]
        if "allow_registration" in kwargs and kwargs["allow_registration"] is not None:
            program.allow_registration = kwargs["allow_registration"]
        if "metadata" in kwargs and kwargs["metadata"] is not None:
            program.metadata = kwargs["metadata"]
        if "form_ids" in kwargs and kwargs["form_ids"] is not None:
            forms = self.db.query(Form).filter(Form.id.in_(kwargs["form_ids"])).all()
            if len(forms) != len(kwargs["form_ids"]):
                raise HTTPException(status_code=404, detail="One or more forms not found")
            program.forms = forms
        
        program.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(program)
        
        return self._convert_program_to_detail_dto(program)
    
    def delete_program(self, program_id: str, created_by: str) -> Dict[str, str]:
        """Delete a program (admin only)"""
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        # Verify user owns the program
        if program.created_by != created_by:
            raise HTTPException(status_code=403, detail="Not authorized to delete this program")
        
        self.db.delete(program)
        self.db.commit()
        
        return {"message": "Program deleted successfully"}
    
    def enroll_user(
        self,
        program_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> ProgramEnrollmentResponse:
        """Enroll a user in a program"""
        # Verify program exists
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if not program.is_published:
            raise HTTPException(status_code=400, detail="Program is not published")
        
        if not program.allow_registration:
            raise HTTPException(status_code=400, detail="Registration is not allowed for this program")
        
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already enrolled
        existing_enrollment = self.db.query(ProgramEnrollment).filter(
            and_(
                ProgramEnrollment.program_id == program_id,
                ProgramEnrollment.user_id == user_id
            )
        ).first()
        
        if existing_enrollment:
            raise HTTPException(status_code=400, detail="User is already enrolled in this program")
        
        # Check capacity
        if program.capacity:
            current_count = self.db.query(ProgramEnrollment).filter(
                and_(
                    ProgramEnrollment.program_id == program_id,
                    ProgramEnrollment.status == 'ACTIVE'
                )
            ).count()
            if current_count >= program.capacity:
                raise HTTPException(status_code=400, detail="Program is at full capacity")
        
        # Create enrollment record
        enrollment = ProgramEnrollment(
            id=self._generate_enrollment_id(),
            program_id=program_id,
            user_id=user_id,
            status='ACTIVE',
            notes=notes
        )
        
        # Add user to participants if not already there
        if user not in program.participants:
            program.participants.append(user)
        
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        
        return ProgramEnrollmentResponse.from_orm(enrollment)
    
    def unenroll_user(self, program_id: str, user_id: str) -> Dict[str, str]:
        """Unenroll a user from a program"""
        enrollment = self.db.query(ProgramEnrollment).filter(
            and_(
                ProgramEnrollment.program_id == program_id,
                ProgramEnrollment.user_id == user_id
            )
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        enrollment.status = 'DROPPED'
        enrollment.dropped_at = datetime.utcnow()
        
        self.db.commit()
        
        return {"message": "User unenrolled from program successfully"}
    
    def get_program_enrollments(
        self,
        program_id: str,
        created_by: str,
        page: int = 1,
        size: int = 10
    ) -> ProgramEnrollmentsListResponse:
        """Get all enrollments for a program (admin only)"""
        # Verify program exists and user owns it
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if program.created_by != created_by:
            raise HTTPException(status_code=403, detail="Not authorized to view enrollments for this program")
        
        # Get enrollments
        query = self.db.query(ProgramEnrollment).filter(ProgramEnrollment.program_id == program_id)
        
        # Sort by most recent first
        query = query.order_by(desc(ProgramEnrollment.enrolled_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        enrollments = query.offset(skip).limit(size).all()
        
        enrollment_dtos = [ProgramEnrollmentResponse.from_orm(e) for e in enrollments]
        
        return ProgramEnrollmentsListResponse(
            program_id=program_id,
            program_title=program.title,
            total_enrollments=total,
            page=page,
            size=size,
            enrollments=enrollment_dtos
        )
    
    def get_user_programs(
        self,
        user_id: str,
        page: int = 1,
        size: int = 10
    ) -> UserProgramsResponse:
        """Get all programs a user is enrolled in"""
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get enrollments for this user
        query = self.db.query(Program).join(
            ProgramEnrollment,
            Program.id == ProgramEnrollment.program_id
        ).filter(
            ProgramEnrollment.user_id == user_id
        )
        
        query = query.order_by(desc(Program.created_at))
        
        total = query.count()
        skip = (page - 1) * size
        programs = query.offset(skip).limit(size).all()
        
        program_dtos = [ProgramResponse.from_orm(p) for p in programs]
        
        return UserProgramsResponse(
            total=total,
            page=page,
            size=size,
            programs=program_dtos
        )
    
    def get_public_programs(
        self,
        page: int = 1,
        size: int = 10,
        category: Optional[str] = None
    ) -> PagedProgramResponse:
        """Get all published programs"""
        query = self.db.query(Program).filter(Program.is_published == True)
        
        if category:
            query = query.filter(Program.category == category)
        
        query = query.order_by(desc(Program.created_at))
        
        total = query.count()
        skip = (page - 1) * size
        programs = query.offset(skip).limit(size).all()
        
        items = [self._convert_program_to_detail_dto(p) for p in programs]
        
        return PagedProgramResponse(total=total, page=page, size=size, items=items)
    
    def update_enrollment_status(
        self,
        enrollment_id: str,
        program_id: str,
        created_by: str,
        status: Optional[str] = None,
        completion_percentage: Optional[int] = None,
        notes: Optional[str] = None
    ) -> ProgramEnrollmentResponse:
        """Update enrollment status (admin only)"""
        # Verify program owner
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if program.created_by != created_by:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get enrollment
        enrollment = self.db.query(ProgramEnrollment).filter(
            ProgramEnrollment.id == enrollment_id
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        # Update fields
        if status:
            enrollment.status = status
            if status == 'COMPLETED':
                enrollment.completed_at = datetime.utcnow()
            elif status == 'DROPPED':
                enrollment.dropped_at = datetime.utcnow()
        
        if completion_percentage is not None:
            enrollment.completion_percentage = completion_percentage
        
        if notes is not None:
            enrollment.notes = notes
        
        enrollment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(enrollment)
        
        return ProgramEnrollmentResponse.from_orm(enrollment)
    
    def _convert_program_to_detail_dto(self, program: Program) -> ProgramDetailResponse:
        """Convert program model to detailed DTO"""
        # Get forms
        forms_data = []
        for form in program.forms:
            form_fields = []
            for field_name, field_info in form.fields.items():
                form_fields.append(FormFieldResponse(
                    name=field_info.get("name", field_name),
                    label=field_info.get("label", ""),
                    field_type=field_info.get("field_type", "text"),
                    required=field_info.get("required", False),
                    placeholder=field_info.get("placeholder"),
                    options=field_info.get("options"),
                    validation=field_info.get("validation")
                ))
            
            forms_data.append(ProgramFormResponse(
                id=form.id,
                title=form.title,
                description=form.description,
                fields=form_fields
            ))
        
        # Get participants
        participants_data = []
        for participant in program.participants:
            participants_data.append(UserBasicResponse(
                id=participant.id,
                fullname=participant.fullname,
                email=participant.email,
                profile_picture_url=participant.profile_picture_url
            ))
        
        return ProgramDetailResponse(
            id=program.id,
            title=program.title,
            description=program.description,
            starting_date=program.starting_date,
            end_date=program.end_date,
            register_url=program.register_url,
            youtube_url=program.youtube_url,
            thumbnail_url=program.thumbnail_url,
            category=program.category,
            location=program.location,
            capacity=program.capacity,
            status=program.status,
            is_published=program.is_published,
            allow_registration=program.allow_registration,
            created_by=program.created_by,
            forms=forms_data,
            participant_count=len(program.participants),
            participants=participants_data,
            created_at=program.created_at,
            updated_at=program.updated_at
        )
