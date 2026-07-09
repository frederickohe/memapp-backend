import io
import os
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.payments.model.Payment import Payment

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

_TYPE_LABELS = {
    "monthly_dues": "Monthly Membership Dues",
    "annual_affiliation": "Annual Affiliation Fee",
    "refund": "Refund",
}

_METHOD_LABELS = {
    "card": "Card (Paystack)",
    "momo_link": "Mobile Money (Web)",
    "momo_ussd": "Mobile Money (USSD)",
    "mtn_momo": "MTN Mobile Money",
    "vodafone": "Vodafone Cash",
    "airteltigo": "AirtelTigo Money",
}


class ReceiptService:
    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(str(_TEMPLATE_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_html(self, payment: Payment, user) -> str:
        template = self._env.get_template("receipt.html")
        paid_at = payment.paid_at or payment.created_at
        return template.render(
            receipt_number=payment.receipt_number or payment.reference,
            paid_at=paid_at.strftime("%d %b %Y, %H:%M UTC") if paid_at else "—",
            member_name=user.fullname,
            member_id=user.member_id,
            branch=user.current_branch,
            email=user.email,
            payment_type_label=_TYPE_LABELS.get(payment.payment_type, payment.payment_type),
            reference=payment.reference,
            method_label=_METHOD_LABELS.get(payment.method or "", payment.method or "—"),
            currency=payment.currency,
            amount_ghs=f"{float(payment.amount_ghs):,.2f}",
            generated_at=datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC"),
        )

    def render_pdf_bytes(self, payment: Payment, user) -> bytes:
        html = self.render_html(payment, user)
        try:
            from xhtml2pdf import pisa
        except ImportError as exc:
            raise RuntimeError("xhtml2pdf is required for PDF receipts") from exc

        buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer, encoding="utf-8")
        if pisa_status.err:
            raise RuntimeError("Failed to generate PDF receipt")
        return buffer.getvalue()

    def upload_receipt_pdf(self, payment: Payment, user) -> str | None:
        """Upload PDF to cloud storage when configured; return URL or None."""
        try:
            from core.cloudstorage.service.storageservice import StorageService
        except Exception:
            return None

        if not os.getenv("CONTABO_BUCKET"):
            return None

        try:
            storage = StorageService()
            pdf_bytes = self.render_pdf_bytes(payment, user)
            file_name = f"receipts/{payment.receipt_number or payment.id}.pdf"
            url = storage.upload_file(
                io.BytesIO(pdf_bytes),
                file_name,
                content_type="application/pdf",
                subfolder="ymca/",
            )
            return url
        except Exception:
            return None
