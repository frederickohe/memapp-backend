from typing import Literal, Optional

from pydantic import BaseModel, Field


class InitiatePaymentRequest(BaseModel):
    payment_type: Literal["monthly_dues", "annual_affiliation"]
    provider: Optional[Literal["paystack", "moolre"]] = None
    method: Literal["card", "momo_link", "momo_ussd"] = "card"
    phone: Optional[str] = None
    callback_url: Optional[str] = None


class ActivatePaymentRequest(BaseModel):
    reference: str = Field(..., min_length=3)


class AdminPaymentListParams(BaseModel):
    page: int = 1
    limit: int = 20
    status: Optional[str] = None
    type: Optional[str] = None
    search: Optional[str] = None
