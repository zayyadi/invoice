import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentMethod(str):
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    MOBILE_MONEY = "mobile_money"
    OTHER = "other"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationships
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    
    # Payment details
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="bank_transfer")
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    user: Mapped["User"] = relationship("User", back_populates="payments")
