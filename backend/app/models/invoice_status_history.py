import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InvoiceStatusHistory(Base):
    __tablename__ = "invoice_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # User ID or "system"
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    invoice: Mapped["Invoice"] = relationship(
        "Invoice", back_populates="status_history"
    )
