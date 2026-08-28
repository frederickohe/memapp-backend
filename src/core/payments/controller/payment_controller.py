from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional

from core.auth.dependencies import get_current_user, get_db
from core.payments.dto.request.payment_requests import ActivatePaymentRequest, InitiatePaymentRequest
from core.payments.dto.response.payment_responses import (
    AdminPaymentListResponse,
    DuesScheduleResponse,
    InitiatePaymentResponse,
    PaymentConfigResponse,
    PaymentOverviewResponse,
    PaymentResponse,
)
from core.payments.service.payment_service import PaymentService
from core.payments.service.receipt_service import ReceiptService
from core.rbac.dependencies import require_permission
from core.rbac.dto.response.api_envelope import ApiEnvelope
from core.user.model.User import User

payment_member_routes = APIRouter()
payment_admin_routes = APIRouter()


@payment_member_routes.get("/config", response_model=ApiEnvelope[PaymentConfigResponse])
def get_payment_config(db: Session = Depends(get_db)):
    return ApiEnvelope(data=PaymentService(db).get_config())


@payment_member_routes.get("/schedule", response_model=ApiEnvelope[DuesScheduleResponse])
def get_dues_schedule(
    year: Optional[int] = Query(None, ge=2020, le=2100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=PaymentService(db).get_schedule(user, year=year))


@payment_member_routes.post("/initiate", response_model=ApiEnvelope[InitiatePaymentResponse])
async def initiate_payment(
    request: InitiatePaymentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=await PaymentService(db).initiate(user, request))


@payment_member_routes.get("/verify/{reference}", response_model=ApiEnvelope[PaymentResponse])
async def verify_payment(
    reference: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=await PaymentService(db).verify(reference, user.id))


@payment_member_routes.get("/me", response_model=ApiEnvelope[List[PaymentResponse]])
def list_my_payments(
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=PaymentService(db).list_member_payments(user.id, limit=limit))


@payment_member_routes.get("/{payment_id}/receipt")
def download_receipt(
    payment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)
    payment, member = service.get_payment_for_receipt(payment_id, user.id)
    pdf_bytes = ReceiptService().render_pdf_bytes(payment, member)
    filename = f"{payment.receipt_number or payment.reference}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@payment_admin_routes.get("/list", response_model=ApiEnvelope[AdminPaymentListResponse])
def admin_list_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None, alias="type"),
    search: Optional[str] = Query(None),
    _: User = Depends(require_permission("finance.view")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(
        data=PaymentService(db).admin_list(
            page=page, limit=limit, status=status, payment_type=type, search=search
        )
    )


@payment_admin_routes.get("/overview", response_model=ApiEnvelope[PaymentOverviewResponse])
def admin_payment_overview(
    _: User = Depends(require_permission("finance.view")),
    db: Session = Depends(get_db),
):
    return ApiEnvelope(data=PaymentService(db).admin_overview())


@payment_admin_routes.post("/activate", response_model=ApiEnvelope[PaymentResponse])
async def admin_activate_payment(
    request: ActivatePaymentRequest,
    _: User = Depends(require_permission("finance.manage")),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)
    payment = service.get_by_reference(request.reference)
    if payment.status != "success":
        if payment.provider == "paystack":
            await service._verify_paystack(payment)
        elif payment.provider == "moolre":
            service._verify_moolre(payment)
        else:
            service._complete_payment(payment, "Manually activated by admin")
        db.refresh(payment)
    if payment.status != "success":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Payment could not be verified. Check the reference and gateway status.",
        )
    return ApiEnvelope(data=service._to_response(payment))
