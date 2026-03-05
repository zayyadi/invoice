from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class InvoiceItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=50)
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
    invoice_number: str
    customer_name: str
    customer_email: str | None
    issue_date: date
    due_date: date
    currency: str
    notes: str | None
    logo_path: str | None
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    items: list[InvoiceItemRead]

    model_config = {"from_attributes": True}
