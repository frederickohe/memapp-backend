import calendar
import logging
import secrets
import string
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from config import settings
from core.moolre.service.moolreservice import MoolrePaymentService
from core.paystack.dto.request.paystack_request import PaystackInitializeRequest
from core.paystack.service.paystack_service import PaystackService
from core.payments.dto.request.payment_requests import InitiatePaymentRequest
from core.payments.dto.response.payment_responses import (
    AdminPaymentItem,
    AdminPaymentListResponse,
    DuesMonthItem,
    DuesScheduleResponse,
    InitiatePaymentResponse,
    PaymentConfigResponse,
    PaymentCustomerSummary,
    PaymentMethodBreakdown,
    PaymentOverviewResponse,
    PaymentResponse,
    RevenueDayItem,
)
from core.payments.model.Payment import Payment, PaymentProvider, PaymentStatus, PaymentType
from core.payments.service.receipt_service import ReceiptService
from core.receipts.model.Receipt import Receipt
from core.user.model.User import User
from utilities.id_helper import generate_id

logger = logging.getLogger(__name__)

PAYSTACK_BASE = "https://api.paystack.co"

_TYPE_PREFIX = {
    PaymentType.MONTHLY_DUES.value: "YMC-DUES",
    PaymentType.ANNUAL_AFFILIATION.value: "YMC-AFF",
}

_METHOD_COLORS = {
    "card": "#111111",
    "momo_link": "#ed1c24",
    "momo_ussd": "#c81018",
    "mtn_momo": "#ed1c24",
    "vodafone": "#111111",
    "airteltigo": "#6b7280",
}


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.receipt_service = ReceiptService()

    def get_config(self) -> PaymentConfigResponse:
        monthly = settings.MONTHLY_DUES_AMOUNT_GHS
        return PaymentConfigResponse(
            monthly_dues_amount_ghs=monthly,
            annual_affiliation_amount_ghs=settings.ANNUAL_AFFILIATION_AMOUNT_GHS,
            annual_total_ghs=settings.ANNUAL_MEMBERSHIP_AMOUNT_GHS,
            currency=settings.DEFAULT_CURRENCY,
            default_provider=PaymentProvider.PAYSTACK.value,
            combined_monthly=True,
            paystack_enabled=bool(settings.PAYSTACK_SECRET_KEY and settings.PAYSTACK_PUBLIC_KEY),
            moolre_enabled=bool(settings.MOOLRE_ACCOUNT_NUMBER),
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _period_label(year: int, month: int) -> str:
        return f"{calendar.month_name[month]} {year}"

    def _amount_for_type(self, payment_type: str) -> float:
        if payment_type in (
            PaymentType.MONTHLY_DUES.value,
            PaymentType.ANNUAL_AFFILIATION.value,
        ):
            return settings.MONTHLY_DUES_AMOUNT_GHS
        raise HTTPException(status_code=400, detail="Invalid payment type")

    def generate_reference(self, payment_type: str) -> str:
        prefix = _TYPE_PREFIX.get(payment_type, "YMC-PAY")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_str = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"{prefix}-{timestamp}-{random_str}"

    def _generate_receipt_number(self) -> str:
        year = datetime.now(timezone.utc).year
        count = (
            self.db.query(func.count(Payment.id))
            .filter(Payment.receipt_number.isnot(None))
            .scalar()
            or 0
        )
        return f"YMC-RCP-{year}-{count + 1:05d}"

    def _resolve_period(self, user: User, year: Optional[int], month: Optional[int]) -> tuple[int, int]:
        now = self._now()
        period_year = year or now.year
        period_month = month or now.month
        if user.created_at:
            joined = user.created_at
            if joined.tzinfo is None:
                joined = joined.replace(tzinfo=timezone.utc)
            join_year, join_month = joined.year, joined.month
            if (period_year, period_month) < (join_year, join_month):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot pay dues for a month before your membership started",
                )
        return period_year, period_month

    def _successful_period_payment(self, user_id: str, year: int, month: int) -> Optional[Payment]:
        return (
            self.db.query(Payment)
            .filter(
                Payment.user_id == user_id,
                Payment.period_year == year,
                Payment.period_month == month,
                Payment.payment_type == PaymentType.MONTHLY_DUES.value,
                Payment.status == PaymentStatus.SUCCESS.value,
            )
            .first()
        )

    def _pending_period_payment(self, user_id: str, year: int, month: int) -> Optional[Payment]:
        return (
            self.db.query(Payment)
            .filter(
                Payment.user_id == user_id,
                Payment.period_year == year,
                Payment.period_month == month,
                Payment.payment_type == PaymentType.MONTHLY_DUES.value,
                Payment.status == PaymentStatus.PENDING.value,
            )
            .order_by(Payment.created_at.desc())
            .first()
        )

    async def initiate(self, user: User, request: InitiatePaymentRequest) -> InitiatePaymentResponse:
        amount_ghs = self._amount_for_type(request.payment_type)
        period_year, period_month = self._resolve_period(
            user, request.period_year, request.period_month
        )

        existing_success = self._successful_period_payment(user.id, period_year, period_month)
        if existing_success:
            raise HTTPException(
                status_code=400,
                detail=f"{self._period_label(period_year, period_month)} is already paid",
            )

        payment = self._pending_period_payment(user.id, period_year, period_month)
        if payment:
            payment.amount_ghs = amount_ghs
            payment.provider = PaymentProvider.PAYSTACK.value
            payment.method = request.method or "card"
            payment.payment_metadata = {
                **(payment.payment_metadata or {}),
                "period_year": period_year,
                "period_month": period_month,
                "branch": user.current_branch,
                "covers": ["monthly_dues", "annual_affiliation"],
            }
        else:
            payment = Payment(
                id=generate_id(),
                user_id=user.id,
                reference=self.generate_reference(PaymentType.MONTHLY_DUES.value),
                payment_type=PaymentType.MONTHLY_DUES.value,
                provider=PaymentProvider.PAYSTACK.value,
                method=request.method or "card",
                amount_ghs=amount_ghs,
                period_year=period_year,
                period_month=period_month,
                currency=settings.DEFAULT_CURRENCY,
                status=PaymentStatus.PENDING.value,
                payment_metadata={
                    "period_year": period_year,
                    "period_month": period_month,
                    "branch": user.current_branch,
                    "covers": ["monthly_dues", "annual_affiliation"],
                },
            )
            self.db.add(payment)
        self.db.commit()

        return await self._initiate_paystack(user, payment, request)

    async def _initiate_paystack(
        self, user: User, payment: Payment, request: InitiatePaymentRequest
    ) -> InitiatePaymentResponse:
        paystack = PaystackService(self.db)
        amount_kobo = int(Decimal(str(payment.amount_ghs)) * 100)
        init_request = PaystackInitializeRequest(
            email=user.email,
            amount=amount_kobo,
            reference=payment.reference,
            callback_url=request.callback_url,
            metadata={
                "payment_id": payment.id,
                "payment_type": payment.payment_type,
                "user_id": user.id,
                "period_year": payment.period_year,
                "period_month": payment.period_month,
            },
            channels=["card", "mobile_money", "bank"],
        )
        result = await paystack.initialize_transaction(user.id, init_request)
        return InitiatePaymentResponse(
            payment_id=payment.id,
            reference=payment.reference,
            provider=PaymentProvider.PAYSTACK.value,
            method="card",
            amount_ghs=float(payment.amount_ghs),
            period_year=payment.period_year,
            period_month=payment.period_month,
            period_label=self._period_label(payment.period_year, payment.period_month),
            authorization_url=result.authorization_url,
            access_code=result.access_code,
        )

    def _initiate_moolre(
        self, user: User, payment: Payment, request: InitiatePaymentRequest
    ) -> InitiatePaymentResponse:
        moolre = MoolrePaymentService()
        callback_url = settings.resolved_moolre_callback_url()
        redirect_url = settings.resolved_moolre_redirect_url()
        metadata = {
            "payment_id": payment.id,
            "payment_type": payment.payment_type,
            "user_id": user.id,
        }

        if request.method == "momo_ussd":
            if not request.phone:
                raise HTTPException(status_code=400, detail="Phone number required for MoMo USSD")
            channel = moolre.detect_momo_channel(request.phone)
            payment.method = self._channel_to_method(channel)
            self.db.commit()
            result = moolre.initiate_ussd_payment(
                payer_phone=request.phone,
                amount=float(payment.amount_ghs),
                externalref=payment.reference,
                channel=channel,
            )
            dial_code = moolre.build_merchant_ussd_dial_code(
                float(payment.amount_ghs), payment.reference
            )
            return InitiatePaymentResponse(
                payment_id=payment.id,
                reference=payment.reference,
                provider=PaymentProvider.MOOLRE.value,
                method="momo_ussd",
                amount_ghs=float(payment.amount_ghs),
                period_year=payment.period_year,
                period_month=payment.period_month,
                period_label=self._period_label(payment.period_year, payment.period_month),
                ussd_dial_code=dial_code or None,
                message="Approve the payment prompt on your phone.",
            )

        payment.method = "momo_link" if request.method == "momo_link" else "card"
        self.db.commit()
        result = moolre.generate_payment_link(
            amount=float(payment.amount_ghs),
            email=user.email,
            externalref=payment.reference,
            callback_url=callback_url,
            redirect_url=redirect_url,
            metadata=metadata,
        )
        return InitiatePaymentResponse(
            payment_id=payment.id,
            reference=payment.reference,
            provider=PaymentProvider.MOOLRE.value,
            method=payment.method,
            amount_ghs=float(payment.amount_ghs),
            period_year=payment.period_year,
            period_month=payment.period_month,
            period_label=self._period_label(payment.period_year, payment.period_month),
            authorization_url=result.get("authorization_url"),
        )

    @staticmethod
    def _channel_to_method(channel: str) -> str:
        return {"13": "mtn_momo", "6": "vodafone", "7": "airteltigo"}.get(channel, "momo_ussd")

    async def verify(self, reference: str, user_id: str) -> PaymentResponse:
        payment = self._get_payment_by_reference(reference)
        if payment.user_id != user_id:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status == PaymentStatus.SUCCESS.value:
            return self._to_response(payment)

        if payment.provider == PaymentProvider.PAYSTACK.value:
            await self._verify_paystack(payment)
        elif payment.provider == PaymentProvider.MOOLRE.value:
            self._verify_moolre(payment)

        self.db.refresh(payment)
        return self._to_response(payment)

    async def _verify_paystack(self, payment: Payment) -> None:
        if not settings.PAYSTACK_SECRET_KEY:
            raise HTTPException(status_code=503, detail="Paystack is not configured")

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{PAYSTACK_BASE}/transaction/verify/{payment.reference}",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Paystack verification failed: {exc}")

        if result.get("status") and result.get("data", {}).get("status") == "success":
            data = result["data"]
            channel = (data.get("channel") or "card").lower()
            if "mobile" in channel or "momo" in channel:
                payment.method = payment.method or "mtn_momo"
            else:
                payment.method = payment.method or "card"
            self._complete_payment(payment, data.get("gateway_response", "success"))
        elif result.get("data", {}).get("status") == "failed":
            payment.status = PaymentStatus.FAILED.value
            payment.gateway_response = result["data"].get("gateway_response")
            self.db.commit()

    def _verify_moolre(self, payment: Payment) -> None:
        moolre = MoolrePaymentService()
        result = moolre.verify_payment(payment.reference)
        if result.get("status") == "success":
            self._complete_payment(payment, "Moolre payment confirmed")
        elif result.get("txstatus") in (2, "2", 3, "3"):
            payment.status = PaymentStatus.FAILED.value
            self.db.commit()

    def handle_webhook(self, reference: str, success: bool, gateway_response: str = "") -> bool:
        """Called by gateway webhooks. Returns True if payment was completed."""
        if not reference or not str(reference).startswith("YMC-"):
            return False

        payment = (
            self.db.query(Payment)
            .filter(Payment.reference == str(reference))
            .first()
        )
        if not payment:
            return False
        if payment.status == PaymentStatus.SUCCESS.value:
            return True
        if success:
            self._complete_payment(payment, gateway_response or "Webhook confirmed")
            return True
        payment.status = PaymentStatus.FAILED.value
        payment.gateway_response = gateway_response
        self.db.commit()
        return False

    def _complete_payment(self, payment: Payment, gateway_response: str) -> None:
        if payment.status == PaymentStatus.SUCCESS.value:
            return

        payment.status = PaymentStatus.SUCCESS.value
        payment.gateway_response = gateway_response[:500] if gateway_response else None
        payment.paid_at = datetime.now(timezone.utc)
        if not payment.receipt_number:
            payment.receipt_number = self._generate_receipt_number()

        user = self.db.query(User).filter(User.id == payment.user_id).first()
        if user:
            self.db.flush()
            self._sync_member_flags(user)

        self.db.commit()

        if user:
            self._store_receipt_record(payment, user)

    def _store_receipt_record(self, payment: Payment, user: User) -> None:
        existing = (
            self.db.query(Receipt)
            .filter(Receipt.transaction_id == payment.id)
            .first()
        )
        if existing:
            return

        pdf_url = self.receipt_service.upload_receipt_pdf(payment, user)
        receipt = Receipt(
            id=generate_id(),
            transaction_id=payment.id,
            user_id=user.id,
            image_url=pdf_url or f"/api/v1/payments/{payment.id}/receipt",
        )
        self.db.add(receipt)
        self.db.commit()

    def list_member_payments(self, user_id: str, limit: int = 20) -> list[PaymentResponse]:
        payments = (
            self.db.query(Payment)
            .filter(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_response(p) for p in payments]

    def admin_list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        payment_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> AdminPaymentListResponse:
        query = self.db.query(Payment).join(User, Payment.user_id == User.id)

        if status:
            query = query.filter(Payment.status == status)
        if payment_type:
            query = query.filter(Payment.payment_type == payment_type)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Payment.reference.ilike(term),
                    User.fullname.ilike(term),
                    User.email.ilike(term),
                )
            )

        total = query.count()
        pages = max(1, (total + limit - 1) // limit)
        offset = (page - 1) * limit
        rows = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()

        items = []
        for payment in rows:
            user = self.db.query(User).filter(User.id == payment.user_id).first()
            items.append(
                AdminPaymentItem(
                    id=payment.id,
                    reference=payment.reference,
                    customer=PaymentCustomerSummary(
                        id=user.id,
                        full_name=user.fullname,
                        email=user.email,
                        phone=user.phone_number,
                    ),
                    type=payment.payment_type,
                    method=payment.method,
                    amount=float(payment.amount_ghs),
                    amount_ghs=float(payment.amount_ghs),
                    status=payment.status,
                    period_year=payment.period_year,
                    period_month=payment.period_month,
                    created_at=payment.created_at,
                )
            )

        return AdminPaymentListResponse(
            total=total,
            page=page,
            pages=pages,
            payments=items,
        )

    def admin_overview(self) -> PaymentOverviewResponse:
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=6)

        total = self.db.query(func.count(Payment.id)).scalar() or 0
        successful = (
            self.db.query(func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.SUCCESS.value)
            .scalar()
            or 0
        )
        pending = (
            self.db.query(func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.PENDING.value)
            .scalar()
            or 0
        )
        failed = (
            self.db.query(func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.FAILED.value)
            .scalar()
            or 0
        )

        revenue = (
            self.db.query(func.coalesce(func.sum(Payment.amount_ghs), 0))
            .filter(Payment.status == PaymentStatus.SUCCESS.value)
            .scalar()
            or 0
        )
        dues_collected = (
            self.db.query(func.coalesce(func.sum(Payment.amount_ghs), 0))
            .filter(
                Payment.status == PaymentStatus.SUCCESS.value,
                Payment.payment_type == PaymentType.MONTHLY_DUES.value,
            )
            .scalar()
            or 0
        )
        affiliation_collected = (
            self.db.query(func.coalesce(func.sum(Payment.amount_ghs), 0))
            .filter(
                Payment.status == PaymentStatus.SUCCESS.value,
                Payment.payment_type == PaymentType.ANNUAL_AFFILIATION.value,
            )
            .scalar()
            or 0
        )

        weekly_revenue = []
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_total = (
                self.db.query(func.coalesce(func.sum(Payment.amount_ghs), 0))
                .filter(
                    Payment.status == PaymentStatus.SUCCESS.value,
                    Payment.paid_at >= day_start,
                    Payment.paid_at < day_end,
                )
                .scalar()
                or 0
            )
            weekly_revenue.append(
                RevenueDayItem(day=day_names[day.weekday()], value=float(day_total))
            )

        method_rows = (
            self.db.query(Payment.method, func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.SUCCESS.value)
            .group_by(Payment.method)
            .all()
        )
        method_total = sum(count for _, count in method_rows) or 1
        method_labels = {
            "card": "Card (Paystack)",
            "momo_link": "MoMo (Web Link)",
            "momo_ussd": "MoMo (USSD)",
            "mtn_momo": "MTN MoMo",
            "vodafone": "Vodafone Cash",
            "airteltigo": "AirtelTigo Money",
        }
        payment_methods = [
            PaymentMethodBreakdown(
                method=method_labels.get(method or "other", method or "Other"),
                percent=round((count / method_total) * 100, 1),
                count=count,
                color=_METHOD_COLORS.get(method or "", "#6b7280"),
            )
            for method, count in method_rows
        ]

        return PaymentOverviewResponse(
            total_payments=total,
            total_revenue_ghs=float(revenue),
            successful_count=successful,
            pending_count=pending,
            failed_count=failed,
            dues_collected_ghs=float(dues_collected),
            affiliation_collected_ghs=float(affiliation_collected),
            weekly_revenue=weekly_revenue,
            payment_methods=payment_methods,
        )

    def get_payment_for_receipt(self, payment_id: str, user_id: str) -> tuple[Payment, User]:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment or payment.user_id != user_id:
            raise HTTPException(status_code=404, detail="Payment not found")
        if payment.status != PaymentStatus.SUCCESS.value:
            raise HTTPException(status_code=400, detail="Receipt available only for successful payments")
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return payment, user

    def get_by_reference(self, reference: str) -> Payment:
        return self._get_payment_by_reference(reference)

    def _join_period(self, user: User) -> tuple[int, int]:
        if not user.created_at:
            return 1970, 1
        joined = user.created_at
        if joined.tzinfo is None:
            joined = joined.replace(tzinfo=timezone.utc)
        return joined.year, joined.month

    def _sync_member_flags(self, user: User) -> None:
        now = self._now()
        current_paid = self._successful_period_payment(user.id, now.year, now.month)
        user.month_dues_paid_status = "YES" if current_paid else "NO"

        join_year, join_month = self._join_period(user)
        unpaid_through_current = False
        for month in range(1, 13):
            if (now.year, month) < (join_year, join_month):
                continue
            if (now.year, month) > (now.year, now.month):
                break
            if not self._successful_period_payment(user.id, now.year, month):
                unpaid_through_current = True
                break
        user.year_affiliation_paid_status = "NO" if unpaid_through_current else "YES"

    def get_schedule(self, user: User, year: Optional[int] = None) -> DuesScheduleResponse:
        now = self._now()
        year = year or now.year
        monthly_amount = settings.MONTHLY_DUES_AMOUNT_GHS
        join_year, join_month = self._join_period(user)

        paid_rows = (
            self.db.query(Payment)
            .filter(
                Payment.user_id == user.id,
                Payment.period_year == year,
                Payment.payment_type == PaymentType.MONTHLY_DUES.value,
                Payment.status == PaymentStatus.SUCCESS.value,
            )
            .all()
        )
        paid_by_month = {row.period_month: row for row in paid_rows}

        months: list[DuesMonthItem] = []
        months_paid = 0
        months_applicable = 0
        months_outstanding = 0

        for month in range(1, 13):
            period = (year, month)
            is_current = period == (now.year, now.month)
            before_join = period < (join_year, join_month)
            in_future = period > (now.year, now.month)
            paid = paid_by_month.get(month)

            if before_join:
                status_value = "not_due"
            elif paid:
                status_value = "paid"
                months_paid += 1
                months_applicable += 1
            elif in_future:
                status_value = "upcoming"
                months_applicable += 1
            elif is_current:
                status_value = "due"
                months_applicable += 1
                months_outstanding += 1
            else:
                status_value = "overdue"
                months_applicable += 1
                months_outstanding += 1

            months.append(
                DuesMonthItem(
                    year=year,
                    month=month,
                    label=self._period_label(year, month),
                    amount_ghs=monthly_amount,
                    status=status_value,
                    can_pay=status_value in ("due", "overdue", "upcoming"),
                    is_current=is_current,
                    payment_id=paid.id if paid else None,
                    reference=paid.reference if paid else None,
                    receipt_number=paid.receipt_number if paid else None,
                    paid_at=paid.paid_at if paid else None,
                )
            )

        current_month_paid = bool(
            year == now.year and paid_by_month.get(now.month)
        )
        year_in_good_standing = months_outstanding == 0 and months_paid > 0

        return DuesScheduleResponse(
            year=year,
            currency=settings.DEFAULT_CURRENCY,
            monthly_amount_ghs=monthly_amount,
            annual_total_ghs=settings.ANNUAL_MEMBERSHIP_AMOUNT_GHS,
            months_paid=months_paid,
            months_applicable=months_applicable,
            months_outstanding=months_outstanding,
            amount_paid_ghs=round(months_paid * monthly_amount, 2),
            amount_outstanding_ghs=round(months_outstanding * monthly_amount, 2),
            current_month_paid=current_month_paid,
            year_in_good_standing=year_in_good_standing,
            months=months,
        )

    def _get_payment_by_reference(self, reference: str) -> Payment:
        payment = self.db.query(Payment).filter(Payment.reference == reference).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    @staticmethod
    def _to_response(payment: Payment) -> PaymentResponse:
        year = getattr(payment, "period_year", None)
        month = getattr(payment, "period_month", None)
        label = None
        if year and month:
            label = f"{calendar.month_name[month]} {year}"
        return PaymentResponse(
            id=payment.id,
            reference=payment.reference,
            payment_type=payment.payment_type,
            provider=payment.provider,
            method=payment.method,
            amount_ghs=float(payment.amount_ghs),
            currency=payment.currency,
            status=payment.status,
            period_year=year,
            period_month=month,
            period_label=label,
            receipt_number=payment.receipt_number,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
        )
