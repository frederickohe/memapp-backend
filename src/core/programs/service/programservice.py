from datetime import datetime
import secrets
import string
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from fastapi import HTTPException, status
from core.programs.model.program import Program, ProgramStatus, program_participants_association, program_forms_association
from core.user.model.User import User
from core.forms.model.Form import Form, FormResponse
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
            program_metadata=metadata,
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
        branch_id: Optional[str] = None,
        is_published: Optional[bool] = None,
        created_by: Optional[str] = None
    ) -> PagedProgramResponse:
        """Get all programs with filters and pagination"""
        query = self.db.query(Program)
        
        # Apply filters
        if created_by:
            query = query.filter(Program.created_by == created_by)
        if branch_id:
            query = query.filter(Program.branch_id == branch_id)
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
            program.program_metadata = kwargs["metadata"]
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
        form_id: str,
        form_data: Dict[str, Any],
        notes: Optional[str] = None
    ) -> ProgramEnrollmentResponse:
        """Enroll a user in a program by submitting a program form"""
        # Verify program exists
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if not program.is_published:
            raise HTTPException(status_code=400, detail="Program is not published")
        
        if not program.allow_registration:
            raise HTTPException(status_code=400, detail="Registration is not allowed for this program")
        
        # Verify form exists and belongs to the program
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        if form not in program.forms:
            raise HTTPException(status_code=400, detail="Form is not associated with this program")
        
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user already has a form response for this form
        existing_response = self.db.query(FormResponse).filter(
            and_(
                FormResponse.form_id == form_id,
                FormResponse.user_id == user_id
            )
        ).first()
        
        if existing_response:
            raise HTTPException(status_code=400, detail="User has already submitted this form")
        
        # Create form response (enrollment is now a form submission)
        form_response = FormResponse(
            id="FR_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)),
            form_id=form_id,
            user_id=user_id,
            data=form_data,
            notes=notes,
            is_submitted=True
        )
        
        # Add user to participants if not already there
        if user not in program.participants:
            program.participants.append(user)
        
        self.db.add(form_response)
        self.db.commit()
        self.db.refresh(form_response)
        
        return self._convert_form_response_to_enrollment_dto(form_response)
    
    def unenroll_user(self, program_id: str, user_id: str) -> Dict[str, str]:
        """Unenroll a user from a program by removing their form responses for the program's forms"""
        # Verify program exists
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if not program.forms:
            raise HTTPException(status_code=400, detail="Program has no forms")
        
        # Get all form IDs for this program
        form_ids = [form.id for form in program.forms]
        
        # Delete form responses for this user for the program's forms
        deleted_count = self.db.query(FormResponse).filter(
            and_(
                FormResponse.form_id.in_(form_ids),
                FormResponse.user_id == user_id
            )
        ).delete()
        
        self.db.commit()
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="User has no submissions for this program's forms")
        
        return {"message": f"User unenrolled from program successfully. {deleted_count} form response(s) removed."}
    
    def get_program_enrollments(
        self,
        program_id: str,
        created_by: str,
        page: int = 1,
        size: int = 10
    ) -> ProgramEnrollmentsListResponse:
        """Get all enrollments (form responses) for a program (admin only)"""
        # Verify program exists and user owns it
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if program.created_by != created_by:
            raise HTTPException(status_code=403, detail="Not authorized to view enrollments for this program")
        
        if not program.forms:
            raise HTTPException(status_code=400, detail="Program has no forms")
        
        # Get all form IDs for this program
        form_ids = [form.id for form in program.forms]
        
        # Get form responses for these forms
        query = self.db.query(FormResponse).filter(FormResponse.form_id.in_(form_ids))
        
        # Sort by most recent first
        query = query.order_by(desc(FormResponse.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        form_responses = query.offset(skip).limit(size).all()
        
        enrollment_dtos = [self._convert_form_response_to_enrollment_dto(fr) for fr in form_responses]
        
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
        """Get all programs a user is enrolled in (has submitted forms for)"""
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get programs where user has submitted form responses
        query = self.db.query(Program).join(
            Form,
            Program.forms.any(Form.id == Form.id)
        ).join(
            FormResponse,
            Form.id == FormResponse.form_id
        ).filter(
            FormResponse.user_id == user_id
        ).distinct()
        
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
        form_response_id: str,
        program_id: str,
        created_by: str,
        completion_percentage: Optional[int] = None,
        notes: Optional[str] = None
    ) -> ProgramEnrollmentResponse:
        """Update form response/enrollment data (admin only)"""
        # Verify program owner
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        if program.created_by != created_by:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get form response
        form_response = self.db.query(FormResponse).filter(
            FormResponse.id == form_response_id
        ).first()
        
        if not form_response:
            raise HTTPException(status_code=404, detail="Form response not found")
        
        # Verify form belongs to program
        if form_response.form not in program.forms:
            raise HTTPException(status_code=403, detail="Form response does not belong to this program")
        
        # Update fields
        if notes is not None:
            form_response.notes = notes
        
        form_response.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(form_response)
        
        return self._convert_form_response_to_enrollment_dto(form_response)
    
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
            metadata=program.program_metadata,
            created_at=program.created_at,
            updated_at=program.updated_at
        )
    
    def _convert_form_response_to_enrollment_dto(self, form_response: FormResponse) -> ProgramEnrollmentResponse:
        """Convert form response to enrollment DTO"""
        return ProgramEnrollmentResponse(
            id=form_response.id,
            program_id=None,  # Form response doesn't directly have program_id, but we can fetch from form
            user_id=form_response.user_id,
            status="ACTIVE",  # Form responses are always active unless deleted
            completion_percentage=100,  # Form is complete once submitted
            enrolled_at=form_response.created_at,
            completed_at=form_response.created_at,  # Completed when submitted
            dropped_at=None,
            notes=form_response.notes
        )
