from datetime import datetime, timedelta, timezone
import csv
import io
import secrets
import string
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from fastapi import HTTPException, status
from core.forms.model.Form import Form, FormResponse, FormAssignmentType
from core.user.model.User import User
from core.forms.dto.response.formresponse import (
    FormResponse as FormResponseDTO,
    FormDetailResponse,
    FormResponseDataResponse,
    FormResponsesListResponse,
    FormAnalyticsResponse,
    FieldAnalytics,
    FieldOptionCount,
    DailyResponseCount,
    PagedFormResponse,
    FormFieldResponse
)


class FormService:
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_form_id(self) -> str:
        """Generate a unique form ID"""
        return "FORM_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def _generate_response_id(self) -> str:
        """Generate a unique form response ID"""
        return "FRESP_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def _convert_fields_to_db_format(self, fields_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert fields list to database format"""
        fields_dict = {}
        for idx, field in enumerate(fields_list):
            fields_dict[field.get("name", f"field_{idx}")] = {
                "name": field.get("name", f"field_{idx}"),
                "label": field.get("label", ""),
                "field_type": field.get("field_type", "text"),
                "required": field.get("required", False),
                "placeholder": field.get("placeholder"),
                "options": field.get("options"),
                "validation": field.get("validation"),
                "order": idx
            }
        return fields_dict
    
    def create_form(
        self,
        admin_id: str,
        title: str,
        description: Optional[str],
        assignment_type: str,
        fields: List[Dict[str, Any]],
        program_id: Optional[str] = None,
        assigned_user_id: Optional[str] = None,
        is_active: bool = True
    ) -> FormResponseDTO:
        """Create a new form"""
        # Verify admin exists
        admin = self.db.query(User).filter(User.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Validate assignment type
        if assignment_type not in [FormAssignmentType.PUBLIC, FormAssignmentType.PROGRAM, FormAssignmentType.USER]:
            raise HTTPException(
                status_code=400,
                detail="Invalid assignment_type. Must be PUBLIC, PROGRAM, or USER"
            )
        
        # If assigning to program, verify it exists (you may need to adjust based on your data model)
        if assignment_type == FormAssignmentType.PROGRAM and program_id:
            # Add validation if program model exists
            pass
        
        # If assigning to user, verify user exists
        if assignment_type == FormAssignmentType.USER and assigned_user_id:
            user = self.db.query(User).filter(User.id == assigned_user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Assigned user not found")
        
        # Convert fields to database format
        fields_dict = self._convert_fields_to_db_format(fields)
        
        # Create form record
        form = Form(
            id=self._generate_form_id(),
            admin_id=admin_id,
            title=title,
            description=description,
            assignment_type=assignment_type,
            program_id=program_id,
            assigned_user_id=assigned_user_id,
            fields=fields_dict,
            is_active=is_active
        )
        
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        
        return self._convert_form_to_dto(form)
    
    def get_form(self, form_id: str) -> FormResponseDTO:
        """Get a specific form by ID"""
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        return self._convert_form_to_dto(form)
    
    def get_form_detail(self, form_id: str) -> FormDetailResponse:
        """Get detailed form information with response count"""
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        response_count = self.db.query(FormResponse).filter(FormResponse.form_id == form_id).count()
        
        return FormDetailResponse(
            id=form.id,
            admin_id=form.admin_id,
            title=form.title,
            description=form.description,
            assignment_type=form.assignment_type,
            program_id=form.program_id,
            assigned_user_id=form.assigned_user_id,
            fields=self._convert_fields_to_response_list(form.fields),
            is_active=form.is_active,
            response_count=response_count,
            created_at=form.created_at,
            updated_at=form.updated_at
        )
    
    def get_all_forms(
        self,
        page: int = 1,
        size: int = 10,
        admin_id: Optional[str] = None,
        assignment_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PagedFormResponse:
        """Get all forms with optional filters and pagination"""
        query = self.db.query(Form)
        
        # Apply filters
        if admin_id:
            query = query.filter(Form.admin_id == admin_id)
        if assignment_type:
            query = query.filter(Form.assignment_type == assignment_type)
        if is_active is not None:
            query = query.filter(Form.is_active == is_active)
        
        # Sort by most recent first
        query = query.order_by(desc(Form.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        forms = query.offset(skip).limit(size).all()
        
        items = []
        for form in forms:
            response_count = self.db.query(FormResponse).filter(FormResponse.form_id == form.id).count()
            items.append(FormDetailResponse(
                id=form.id,
                admin_id=form.admin_id,
                title=form.title,
                description=form.description,
                assignment_type=form.assignment_type,
                program_id=form.program_id,
                assigned_user_id=form.assigned_user_id,
                fields=self._convert_fields_to_response_list(form.fields),
                is_active=form.is_active,
                response_count=response_count,
                created_at=form.created_at,
                updated_at=form.updated_at
            ))
        
        return PagedFormResponse(total=total, page=page, size=size, items=items)
    
    def update_form(
        self,
        form_id: str,
        admin_id: str,
        **kwargs
    ) -> FormResponseDTO:
        """Update a form (admin only)"""
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Verify admin owns the form
        if form.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this form")
        
        # Update fields
        if "title" in kwargs and kwargs["title"] is not None:
            form.title = kwargs["title"]
        if "description" in kwargs and kwargs["description"] is not None:
            form.description = kwargs["description"]
        if "assignment_type" in kwargs and kwargs["assignment_type"] is not None:
            if kwargs["assignment_type"] not in [FormAssignmentType.PUBLIC, FormAssignmentType.PROGRAM, FormAssignmentType.USER]:
                raise HTTPException(status_code=400, detail="Invalid assignment_type")
            form.assignment_type = kwargs["assignment_type"]
        if "program_id" in kwargs:
            form.program_id = kwargs["program_id"]
        if "assigned_user_id" in kwargs:
            form.assigned_user_id = kwargs["assigned_user_id"]
        if "fields" in kwargs and kwargs["fields"] is not None:
            form.fields = self._convert_fields_to_db_format(kwargs["fields"])
        if "is_active" in kwargs and kwargs["is_active"] is not None:
            form.is_active = kwargs["is_active"]
        
        form.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(form)
        
        return self._convert_form_to_dto(form)
    
    def delete_form(self, form_id: str, admin_id: str) -> Dict[str, str]:
        """Delete a form (admin only)"""
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Verify admin owns the form
        if form.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this form")
        
        self.db.delete(form)
        self.db.commit()
        
        return {"message": "Form deleted successfully"}
    
    def submit_form_response(
        self,
        form_id: str,
        user_id: str,
        data: Dict[str, Any],
        notes: Optional[str] = None
    ) -> FormResponseDataResponse:
        """Submit a response to a form"""
        # Verify form exists
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        if not form.is_active:
            raise HTTPException(status_code=400, detail="Form is not active")
        
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        existing = (
            self.db.query(FormResponse)
            .filter(FormResponse.form_id == form_id, FormResponse.user_id == user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="You have already submitted this survey")

        # Validate data against form fields (basic validation)
        self._validate_form_response(form, data)
        
        # Create response record
        response = FormResponse(
            id=self._generate_response_id(),
            form_id=form_id,
            user_id=user_id,
            data=data,
            notes=notes,
            is_submitted=True
        )
        
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        
        return self._convert_response_to_dto(response)
    
    def _convert_response_to_dto(self, response: FormResponse) -> FormResponseDataResponse:
        """Convert form response model to DTO with user info"""
        user = self.db.query(User).filter(User.id == response.user_id).first()
        return FormResponseDataResponse(
            id=response.id,
            form_id=response.form_id,
            user_id=response.user_id,
            user_name=user.fullname if user else None,
            user_email=user.email if user else None,
            data=response.data,
            notes=response.notes,
            is_submitted=response.is_submitted,
            created_at=response.created_at,
            updated_at=response.updated_at,
        )
    
    def get_form_responses(
        self,
        form_id: str,
        admin_id: str,
        page: int = 1,
        size: int = 10
    ) -> FormResponsesListResponse:
        """Get all responses to a form (admin only)"""
        # Verify form exists and admin owns it
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        if form.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to view responses for this form")
        
        # Get responses
        query = self.db.query(FormResponse).filter(FormResponse.form_id == form_id)
        
        # Sort by most recent first
        query = query.order_by(desc(FormResponse.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * size
        responses = query.offset(skip).limit(size).all()
        
        response_dtos = [self._convert_response_to_dto(r) for r in responses]
        
        return FormResponsesListResponse(
            form_id=form_id,
            form_title=form.title,
            total_responses=total,
            page=page,
            size=size,
            responses=response_dtos
        )
    
    def get_user_form_responses(
        self,
        user_id: str,
        page: int = 1,
        size: int = 10
    ) -> PagedFormResponse:
        """Get all forms assigned to a user and their responses"""
        # Get forms assigned to this user
        query = self.db.query(Form).filter(
            and_(
                Form.assigned_user_id == user_id,
                Form.is_active == True
            )
        )
        
        query = query.order_by(desc(Form.created_at))
        
        total = query.count()
        skip = (page - 1) * size
        forms = query.offset(skip).limit(size).all()
        
        items = []
        for form in forms:
            # Check if user already submitted a response
            response_count = self.db.query(FormResponse).filter(
                and_(
                    FormResponse.form_id == form.id,
                    FormResponse.user_id == user_id
                )
            ).count()
            
            items.append(FormDetailResponse(
                id=form.id,
                admin_id=form.admin_id,
                title=form.title,
                description=form.description,
                assignment_type=form.assignment_type,
                program_id=form.program_id,
                assigned_user_id=form.assigned_user_id,
                fields=self._convert_fields_to_response_list(form.fields),
                is_active=form.is_active,
                response_count=response_count,
                created_at=form.created_at,
                updated_at=form.updated_at
            ))
        
        return PagedFormResponse(total=total, page=page, size=size, items=items)
    
    def get_public_forms(
        self,
        page: int = 1,
        size: int = 10
    ) -> PagedFormResponse:
        """Get all public forms"""
        query = self.db.query(Form).filter(
            and_(
                Form.assignment_type == FormAssignmentType.PUBLIC,
                Form.is_active == True
            )
        )
        
        query = query.order_by(desc(Form.created_at))
        
        total = query.count()
        skip = (page - 1) * size
        forms = query.offset(skip).limit(size).all()
        
        items = []
        for form in forms:
            response_count = self.db.query(FormResponse).filter(FormResponse.form_id == form.id).count()
            items.append(FormDetailResponse(
                id=form.id,
                admin_id=form.admin_id,
                title=form.title,
                description=form.description,
                assignment_type=form.assignment_type,
                program_id=form.program_id,
                assigned_user_id=form.assigned_user_id,
                fields=self._convert_fields_to_response_list(form.fields),
                is_active=form.is_active,
                response_count=response_count,
                created_at=form.created_at,
                updated_at=form.updated_at
            ))
        
        return PagedFormResponse(total=total, page=page, size=size, items=items)

    def get_available_surveys(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
    ) -> PagedFormResponse:
        """Public surveys plus forms assigned to this member."""
        query = (
            self.db.query(Form)
            .filter(
                Form.is_active == True,
                or_(
                    Form.assignment_type == FormAssignmentType.PUBLIC,
                    and_(
                        Form.assignment_type == FormAssignmentType.USER,
                        Form.assigned_user_id == user_id,
                    ),
                ),
            )
            .order_by(desc(Form.created_at))
        )
        total = query.count()
        forms = query.offset((page - 1) * size).limit(size).all()
        form_ids = [form.id for form in forms]
        submitted_ids = set()
        if form_ids:
            submitted_ids = {
                row[0]
                for row in self.db.query(FormResponse.form_id)
                .filter(
                    FormResponse.user_id == user_id,
                    FormResponse.form_id.in_(form_ids),
                )
                .all()
            }
        items = []
        for form in forms:
            response_count = (
                self.db.query(FormResponse)
                .filter(FormResponse.form_id == form.id)
                .count()
            )
            items.append(
                FormDetailResponse(
                    id=form.id,
                    admin_id=form.admin_id,
                    title=form.title,
                    description=form.description,
                    assignment_type=form.assignment_type,
                    program_id=form.program_id,
                    assigned_user_id=form.assigned_user_id,
                    fields=self._convert_fields_to_response_list(form.fields),
                    is_active=form.is_active,
                    response_count=response_count,
                    submitted=form.id in submitted_ids,
                    created_at=form.created_at,
                    updated_at=form.updated_at,
                )
            )
        return PagedFormResponse(total=total, page=page, size=size, items=items)
    
    def get_form_analytics(self, form_id: str, admin_id: str) -> FormAnalyticsResponse:
        """Compute analytics for a form (admin only)"""
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        if form.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to view analytics for this form")
        
        responses = (
            self.db.query(FormResponse)
            .filter(FormResponse.form_id == form_id)
            .order_by(FormResponse.created_at)
            .all()
        )
        
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        total = len(responses)
        last_7 = sum(1 for r in responses if r.created_at and r.created_at >= seven_days_ago)
        last_30 = sum(1 for r in responses if r.created_at and r.created_at >= thirty_days_ago)
        
        # Daily counts for last 30 days
        daily_map: Dict[str, int] = {}
        for i in range(30):
            day = (now - timedelta(days=29 - i)).strftime("%Y-%m-%d")
            daily_map[day] = 0
        for r in responses:
            if r.created_at and r.created_at >= thirty_days_ago:
                day_key = r.created_at.strftime("%Y-%m-%d")
                if day_key in daily_map:
                    daily_map[day_key] += 1
        daily_counts = [DailyResponseCount(date=d, count=c) for d, c in sorted(daily_map.items())]
        
        # Per-field analytics
        fields_list = self._convert_fields_to_response_list(form.fields)
        choice_types = {"select", "radio", "checkbox"}
        field_analytics: List[FieldAnalytics] = []
        
        for field in fields_list:
            answered = 0
            option_counts: Optional[List[FieldOptionCount]] = None
            
            if field.field_type in choice_types and field.options:
                counts: Dict[str, int] = {opt: 0 for opt in field.options}
                for r in responses:
                    val = r.data.get(field.name)
                    if val is None or val == "" or val == []:
                        continue
                    answered += 1
                    if field.field_type == "checkbox" and isinstance(val, list):
                        for v in val:
                            if v in counts:
                                counts[v] += 1
                    elif isinstance(val, str) and val in counts:
                        counts[val] += 1
                option_counts = [FieldOptionCount(option=k, count=v) for k, v in counts.items()]
            else:
                for r in responses:
                    val = r.data.get(field.name)
                    if val is not None and val != "" and val != []:
                        answered += 1
            
            field_analytics.append(FieldAnalytics(
                name=field.name,
                label=field.label,
                field_type=field.field_type,
                total_answered=answered,
                option_counts=option_counts,
            ))
        
        return FormAnalyticsResponse(
            form_id=form_id,
            form_title=form.title,
            total_responses=total,
            responses_last_7_days=last_7,
            responses_last_30_days=last_30,
            daily_counts=daily_counts,
            field_analytics=field_analytics,
        )
    
    def export_form_responses_csv(self, form_id: str, admin_id: str) -> Tuple[str, str]:
        """Export all form responses as CSV (admin only)"""
        form = self.db.query(Form).filter(Form.id == form_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        if form.admin_id != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to export responses for this form")
        
        responses = (
            self.db.query(FormResponse)
            .filter(FormResponse.form_id == form_id)
            .order_by(desc(FormResponse.created_at))
            .all()
        )
        
        fields_list = self._convert_fields_to_response_list(form.fields)
        field_names = [f.name for f in fields_list]
        field_labels = {f.name: f.label for f in fields_list}
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        header = ["Response ID", "User ID", "User Name", "User Email", "Submitted At", "Notes"]
        header.extend(field_labels.get(fn, fn) for fn in field_names)
        writer.writerow(header)
        
        for r in responses:
            user = self.db.query(User).filter(User.id == r.user_id).first()
            row = [
                r.id,
                r.user_id,
                user.fullname if user else "",
                user.email if user else "",
                r.created_at.isoformat() if r.created_at else "",
                r.notes or "",
            ]
            for fn in field_names:
                val = r.data.get(fn, "")
                if isinstance(val, list):
                    val = "; ".join(str(v) for v in val)
                row.append(val)
            writer.writerow(row)
        
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in form.title)[:50]
        filename = f"{safe_title}_responses.csv"
        return output.getvalue(), filename
    
    def _validate_form_response(self, form: Form, data: Dict[str, Any]) -> None:
        """Validate form response against form fields"""
        for field_name, field_info in form.fields.items():
            if field_info.get("required") and (field_name not in data or data[field_name] is None):
                raise HTTPException(
                    status_code=400,
                    detail=f"Required field '{field_info.get('label', field_name)}' is missing"
                )
    
    def _convert_form_to_dto(self, form: Form) -> FormResponseDTO:
        """Convert form model to DTO"""
        return FormResponseDTO(
            id=form.id,
            admin_id=form.admin_id,
            title=form.title,
            description=form.description,
            assignment_type=form.assignment_type,
            program_id=form.program_id,
            assigned_user_id=form.assigned_user_id,
            fields=self._convert_fields_to_response_list(form.fields),
            is_active=form.is_active,
            created_at=form.created_at,
            updated_at=form.updated_at
        )
    
    def _convert_fields_to_response_list(self, fields_dict: Dict[str, Any]) -> List[FormFieldResponse]:
        """Convert fields dict to response list"""
        if not fields_dict:
            return []
        fields_list = []
        sorted_fields = sorted(
            fields_dict.items(),
            key=lambda x: x[1].get("order", 0) if isinstance(x[1], dict) else 0
        )
        
        for field_name, field_info in sorted_fields:
            if not isinstance(field_info, dict):
                continue
            fields_list.append(FormFieldResponse(
                name=field_info.get("name", field_name),
                label=field_info.get("label", ""),
                field_type=field_info.get("field_type", "text"),
                required=field_info.get("required", False),
                placeholder=field_info.get("placeholder"),
                options=field_info.get("options"),
                validation=field_info.get("validation")
            ))
        
        return fields_list
