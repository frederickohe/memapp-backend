from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import logging

from utilities.dbconfig import SessionLocal
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user, require_admin
from core.user.model.User import User
from core.forms.dto.response.formresponse import (
    FormResponse,
    FormDetailResponse,
    FormResponseDataResponse,
    FormResponsesListResponse,
    FormAnalyticsResponse,
    PagedFormResponse,
    MessageResponse,
)
from core.forms.dto.request.formrequest import (
    FormCreateRequest,
    FormUpdateRequest,
    FormResponseSubmitRequest,
)
from core.forms.service.formservice import FormService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


form_routes = APIRouter()


# ===================== STATIC ROUTES (must come before /{form_id}) =====================

@form_routes.get("/public/list", response_model=PagedFormResponse)
async def list_public_forms(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all public forms (no authentication required)"""
    service = FormService(db)
    return service.get_public_forms(page=page, size=size)


@form_routes.get("/my-forms", response_model=PagedFormResponse)
async def get_my_forms(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all forms assigned to the current user"""
    service = FormService(db)
    return service.get_user_form_responses(user_id=current_user.id, page=page, size=size)


@form_routes.post("/create", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    request: FormCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new form (Admin only)"""
    service = FormService(db)
    fields_data = [field.dict() for field in request.fields]
    return service.create_form(
        admin_id=current_user.id,
        title=request.title,
        description=request.description,
        assignment_type=request.assignment_type,
        fields=fields_data,
        program_id=request.program_id,
        assigned_user_id=request.assigned_user_id,
        is_active=request.is_active,
    )


@form_routes.get("", response_model=PagedFormResponse)
async def list_forms(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    assignment_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all forms created by the admin with pagination"""
    service = FormService(db)
    return service.get_all_forms(
        page=page,
        size=size,
        admin_id=current_user.id,
        assignment_type=assignment_type,
        is_active=is_active,
    )


# ===================== FORM BY ID =====================

@form_routes.get("/{form_id}", response_model=FormResponse)
async def get_form(form_id: str, db: Session = Depends(get_db)):
    """Get a specific form by ID"""
    service = FormService(db)
    return service.get_form(form_id)


@form_routes.get("/{form_id}/detail", response_model=FormDetailResponse)
async def get_form_detail(form_id: str, db: Session = Depends(get_db)):
    """Get detailed form information with response count"""
    service = FormService(db)
    return service.get_form_detail(form_id)


@form_routes.put("/{form_id}", response_model=FormResponse)
async def update_form(
    form_id: str,
    request: FormUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a form (Admin only)"""
    service = FormService(db)
    fields_data = None
    if request.fields:
        fields_data = [field.dict() for field in request.fields]
    return service.update_form(
        form_id=form_id,
        admin_id=current_user.id,
        title=request.title,
        description=request.description,
        assignment_type=request.assignment_type,
        fields=fields_data,
        program_id=request.program_id,
        assigned_user_id=request.assigned_user_id,
        is_active=request.is_active,
    )


@form_routes.delete("/{form_id}", response_model=MessageResponse)
async def delete_form(
    form_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a form (Admin only)"""
    service = FormService(db)
    result = service.delete_form(form_id, current_user.id)
    return MessageResponse(message=result["message"])


# ===================== FORM RESPONSES =====================

@form_routes.post(
    "/{form_id}/submit",
    response_model=FormResponseDataResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_form_response(
    form_id: str,
    request: FormResponseSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a response to a form"""
    service = FormService(db)
    return service.submit_form_response(
        form_id=form_id,
        user_id=current_user.id,
        data=request.data,
        notes=request.notes,
    )


@form_routes.get("/{form_id}/responses", response_model=FormResponsesListResponse)
async def get_form_responses(
    form_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get all responses to a form (Admin only - form owner)"""
    service = FormService(db)
    return service.get_form_responses(
        form_id=form_id,
        admin_id=current_user.id,
        page=page,
        size=size,
    )


@form_routes.get("/{form_id}/analytics", response_model=FormAnalyticsResponse)
async def get_form_analytics(
    form_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get analytics for a form (Admin only - form owner)"""
    service = FormService(db)
    return service.get_form_analytics(form_id=form_id, admin_id=current_user.id)


@form_routes.get("/{form_id}/responses/export")
async def export_form_responses(
    form_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Export all form responses as CSV (Admin only - form owner)"""
    service = FormService(db)
    csv_content, filename = service.export_form_responses_csv(
        form_id=form_id,
        admin_id=current_user.id,
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
