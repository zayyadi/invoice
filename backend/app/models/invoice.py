import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InvoiceStatus(str, PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    invoice_number: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, index=True
    )

    # Issuer info (snapshot at creation time)
    issuer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issuer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issuer_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issuer_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Client info (snapshot at creation time for history)
    customer_name: Mapped[str] = mapped_column(String(255))
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Payment instructions
    payment_bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_account_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Dates
    issue_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    viewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Financials
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="invoices")
    client: Mapped["Client | None"] = relationship("Client", back_populates="invoices")
    items: Mapped[list["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["InvoiceStatusHistory"]] = relationship(
        "InvoiceStatusHistory", back_populates="invoice", cascade="all, delete-orphan",
        order_by="InvoiceStatusHistory.created_at.desc()"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan",
        order_by="Payment.payment_date.desc()"
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(String(500))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    invoice: Mapped[Invoice] = relationship("Invoice", back_populates="items")
