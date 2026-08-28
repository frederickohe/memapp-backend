from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from utilities.dbconfig import Base


class PaymentType(str, PyEnum):
    MONTHLY_DUES = "monthly_dues"
    ANNUAL_AFFILIATION = "annual_affiliation"
    REFUND = "refund"


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentProvider(str, PyEnum):
    PAYSTACK = "paystack"
    MOOLRE = "moolre"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    payment_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    amount_ghs: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GHS")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=PaymentStatus.PENDING.value, index=True)
    gateway_response: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    payment_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    receipt_number: Mapped[Optional[str]] = mapped_column(String(30), unique=True, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="payments")
