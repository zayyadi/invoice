from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    payment_date: date | None = None
    payment_method: str = "bank_transfer"
    reference_number: str | None = None
    notes: str | None = None


class PaymentCreate(PaymentBase):
    invoice_id: UUID


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    payment_date: date | None = None
    payment_method: str | None = None
    reference_number: str | None = None
    notes: str | None = None


class PaymentRead(PaymentBase):
    id: UUID
    invoice_id: UUID
    user_id: UUID
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True


class PaymentListItem(BaseModel):
    id: UUID
    invoice_id: UUID
    amount: Decimal
    payment_date: date
    payment_method: str
    reference_number: str | None
    invoice_number: str
    customer_name: str
    
    class Config:
        from_attributes = True


class PaymentSummary(BaseModel):
    total_payments: int
    total_amount: float
