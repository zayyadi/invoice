from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.invoice import InvoiceStatus


class InvoiceItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=50)
    client_id: str | None = Field(default=None, description="Optional client ID to auto-populate customer details")
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    issuer_email: EmailStr | None = None
    issuer_phone: str | None = Field(default=None, min_length=1, max_length=50)
    issuer_address: str | None = Field(default=None, min_length=1, max_length=1000)
    payment_bank_name: str | None = Field(default=None, min_length=1, max_length=255)
    payment_account_number: str | None = Field(default=None, min_length=1, max_length=50)
    payment_account_name: str | None = Field(default=None, min_length=1, max_length=255)
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr | None = None
    issue_date: date
    due_date: date
    currency: str = Field(default="NGN", min_length=3, max_length=3)
    notes: str | None = None
    tax_rate: Decimal = Field(default=0, ge=0)
    items: list[InvoiceItemCreate] = Field(min_length=1)


class InvoiceItemRead(BaseModel):
    id: int
    description: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = {"from_attributes": True}


class InvoiceRead(BaseModel):
    id: UUID
    user_id: UUID
    invoice_number: str
    status: InvoiceStatus
    issuer_name: str | None
    issuer_email: str | None
    issuer_phone: str | None
    issuer_address: str | None
    payment_bank_name: str | None
    payment_account_number: str | None
    payment_account_name: str | None
    customer_name: str
    customer_email: str | None
    issue_date: date
    due_date: date
    currency: str
    notes: str | None
    logo_path: str | None
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    items: list[InvoiceItemRead]
    sent_at: datetime | None
    viewed_at: datetime | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShareRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    telegram_id: int | None = None
    message: str | None = None


class InvoiceUpdate(BaseModel):
    invoice_number: str | None = Field(default=None, min_length=1, max_length=50)
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    issuer_email: EmailStr | None = None
    issuer_phone: str | None = Field(default=None, min_length=1, max_length=50)
    issuer_address: str | None = Field(default=None, min_length=1, max_length=1000)
    payment_bank_name: str | None = Field(default=None, min_length=1, max_length=255)
    payment_account_number: str | None = Field(default=None, min_length=1, max_length=50)
    payment_account_name: str | None = Field(default=None, min_length=1, max_length=255)
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)
    customer_email: EmailStr | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    notes: str | None = None
    tax_rate: Decimal | None = Field(default=None, ge=0)
