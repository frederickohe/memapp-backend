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
    authorization_url: Optional[str] = None
    access_code: Optional[str] = None
    ussd_dial_code: Optional[str] = None
    message: Optional[str] = None


class PaymentConfigResponse(BaseModel):
    monthly_dues_amount_ghs: float
    annual_affiliation_amount_ghs: float
    currency: str
    default_provider: str
    paystack_enabled: bool
    moolre_enabled: bool


class AdminPaymentItem(BaseModel):
    id: str
    reference: str
    customer: PaymentCustomerSummary
    type: str
    method: Optional[str] = None
    amount: float
    amount_ghs: float
    status: str
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
