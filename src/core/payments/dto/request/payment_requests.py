from typing import Literal, Optional

from pydantic import BaseModel, Field


class InitiatePaymentRequest(BaseModel):
    payment_type: Literal["monthly_dues", "annual_affiliation"] = "monthly_dues"
    provider: Optional[Literal["paystack", "moolre"]] = "paystack"
    method: Literal["card", "momo_link", "momo_ussd"] = "card"
    phone: Optional[str] = None
    callback_url: Optional[str] = None
    period_year: Optional[int] = Field(None, ge=2020, le=2100)
    period_month: Optional[int] = Field(None, ge=1, le=12)


class ActivatePaymentRequest(BaseModel):
    reference: str = Field(..., min_length=3)


class AdminPaymentListParams(BaseModel):
    page: int = 1
    limit: int = 20
    status: Optional[str] = None
    type: Optional[str] = None
    search: Optional[str] = None
