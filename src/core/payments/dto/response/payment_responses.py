from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PaymentCustomerSummary(BaseModel):
    id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        orm_mode = True


class PaymentResponse(BaseModel):
    id: str
    reference: str
    payment_type: str
    provider: str
    method: Optional[str] = None
    amount_ghs: float
    currency: str
    status: str
    period_year: Optional[int] = None
    period_month: Optional[int] = None
    period_label: Optional[str] = None
    receipt_number: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


class InitiatePaymentResponse(BaseModel):
    payment_id: str
    reference: str
    provider: str
    method: str
    amount_ghs: float
    period_year: int
    period_month: int
    period_label: str
    authorization_url: Optional[str] = None
    access_code: Optional[str] = None
    ussd_dial_code: Optional[str] = None
    message: Optional[str] = None


class PaymentConfigResponse(BaseModel):
    monthly_dues_amount_ghs: float
    annual_affiliation_amount_ghs: float
    annual_total_ghs: float
    currency: str
    default_provider: str
    combined_monthly: bool
    paystack_enabled: bool
    moolre_enabled: bool


class DuesMonthItem(BaseModel):
    year: int
    month: int
    label: str
    amount_ghs: float
    status: str
    can_pay: bool
    is_current: bool
    payment_id: Optional[str] = None
    reference: Optional[str] = None
    receipt_number: Optional[str] = None
    paid_at: Optional[datetime] = None


class DuesScheduleResponse(BaseModel):
    year: int
    currency: str
    monthly_amount_ghs: float
    annual_total_ghs: float
    months_paid: int
    months_applicable: int
    months_outstanding: int
    amount_paid_ghs: float
    amount_outstanding_ghs: float
    current_month_paid: bool
    year_in_good_standing: bool
    months: List[DuesMonthItem]


class AdminPaymentItem(BaseModel):
    id: str
    reference: str
    customer: PaymentCustomerSummary
    type: str
    method: Optional[str] = None
    amount: float
    amount_ghs: float
    status: str
    period_year: Optional[int] = None
    period_month: Optional[int] = None
    created_at: datetime


class AdminPaymentListResponse(BaseModel):
    total: int
    page: int
    pages: int
    payments: List[AdminPaymentItem]


class RevenueDayItem(BaseModel):
    day: str
    value: float


class PaymentMethodBreakdown(BaseModel):
    method: str
    percent: float
    count: int
    color: str


class PaymentOverviewResponse(BaseModel):
    total_payments: int
    total_revenue_ghs: float
    successful_count: int
    pending_count: int
    failed_count: int
    dues_collected_ghs: float
    affiliation_collected_ghs: float
    weekly_revenue: List[RevenueDayItem]
    payment_methods: List[PaymentMethodBreakdown]
