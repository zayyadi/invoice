from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=1000)
    tax_id: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    default_currency: str | None = Field(default=None, max_length=3)


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=1000)
    tax_id: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    default_currency: str | None = Field(default=None, max_length=3)


class ClientRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    email: str | None
    phone: str | None
    address: str | None
    tax_id: str | None
    notes: str | None
    default_currency: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientListItem(BaseModel):
    id: UUID
    name: str
    email: str | None
    phone: str | None
    default_currency: str | None
    invoice_count: int = 0
    total_invoiced: str = "0.00"
    total_paid: str = "0.00"

    class Config:
        from_attributes = True
