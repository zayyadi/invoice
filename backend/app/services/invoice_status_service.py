from datetime import datetime, date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_status_history import InvoiceStatusHistory


VALID_STATUS_TRANSITIONS = {
    InvoiceStatus.DRAFT: [InvoiceStatus.SENT, InvoiceStatus.CANCELLED],
    InvoiceStatus.SENT: [InvoiceStatus.VIEWED, InvoiceStatus.PAID, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED],
    InvoiceStatus.VIEWED: [InvoiceStatus.PAID, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE],
    InvoiceStatus.PARTIAL: [InvoiceStatus.PAID, InvoiceStatus.OVERDUE],
    InvoiceStatus.PAID: [],
    InvoiceStatus.OVERDUE: [InvoiceStatus.PAID, InvoiceStatus.PARTIAL],
    InvoiceStatus.CANCELLED: [],
}


def can_transition(from_status: InvoiceStatus, to_status: InvoiceStatus) -> bool:
    """Check if a status transition is valid."""
    if from_status == to_status:
        return True
    return to_status in VALID_STATUS_TRANSITIONS.get(from_status, [])


def transition_status(
    db: Session,
    invoice: Invoice,
    new_status: InvoiceStatus,
    changed_by: str | None = None,
    notes: str | None = None,
) -> Invoice:
    """Transition invoice to a new status with validation and history tracking."""
    
    if not can_transition(invoice.status, new_status):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {invoice.status.value} to {new_status.value}"
        )
    
    old_status = invoice.status
    invoice.status = new_status
    
    # Update timestamp fields based on status
    now = datetime.utcnow()
    if new_status == InvoiceStatus.SENT and not invoice.sent_at:
        invoice.sent_at = now
    elif new_status == InvoiceStatus.VIEWED and not invoice.viewed_at:
        invoice.viewed_at = now
    elif new_status == InvoiceStatus.PAID and not invoice.paid_at:
        invoice.paid_at = now
        # When marked as paid, update paid_amount to total_amount if not already set
        if invoice.paid_amount == 0:
            invoice.paid_amount = invoice.total_amount
    
    # Create status history record
    history_entry = InvoiceStatusHistory(
        invoice_id=invoice.id,
        status=new_status.value,
        changed_by=changed_by or "system",
        notes=notes,
    )
    db.add(history_entry)
    db.commit()
    db.refresh(invoice)
    
    return invoice


def mark_as_sent(
    db: Session,
    invoice: Invoice,
    changed_by: str | None = None,
) -> Invoice:
    """Mark invoice as sent."""
    return transition_status(db, invoice, InvoiceStatus.SENT, changed_by, "Invoice sent to client")


def mark_as_viewed(
    db: Session,
    invoice: Invoice,
    changed_by: str | None = None,
) -> Invoice:
    """Mark invoice as viewed by client."""
    return transition_status(db, invoice, InvoiceStatus.VIEWED, changed_by, "Invoice viewed by client")


def mark_as_paid(
    db: Session,
    invoice: Invoice,
    changed_by: str | None = None,
    notes: str | None = None,
) -> Invoice:
    """Mark invoice as fully paid."""
    return transition_status(
        db, invoice, InvoiceStatus.PAID, changed_by, notes or "Payment received in full"
    )


def mark_as_partial(
    db: Session,
    invoice: Invoice,
    paid_amount: float,
    changed_by: str | None = None,
    notes: str | None = None,
) -> Invoice:
    """Mark invoice as partially paid."""
    invoice.paid_amount = paid_amount
    return transition_status(
        db, invoice, InvoiceStatus.PARTIAL, changed_by, 
        notes or f"Partial payment received: {paid_amount}"
    )


def mark_as_cancelled(
    db: Session,
    invoice: Invoice,
    changed_by: str | None = None,
    reason: str | None = None,
) -> Invoice:
    """Cancel the invoice."""
    return transition_status(
        db, invoice, InvoiceStatus.CANCELLED, changed_by, reason or "Invoice cancelled"
    )


def check_and_mark_overdue(db: Session, invoice: Invoice) -> bool:
    """Check if invoice is overdue and mark it accordingly."""
    if invoice.status not in [InvoiceStatus.SENT, InvoiceStatus.VIEWED, InvoiceStatus.PARTIAL]:
        return False
    
    if invoice.due_date < date.today():
        transition_status(db, invoice, InvoiceStatus.OVERDUE, "system", "Auto-marked as overdue")
        return True
    
    return False


def get_status_history(db: Session, invoice_id: UUID) -> list[InvoiceStatusHistory]:
    """Get status history for an invoice."""
    return (
        db.query(InvoiceStatusHistory)
        .filter(InvoiceStatusHistory.invoice_id == invoice_id)
        .order_by(InvoiceStatusHistory.created_at.desc())
        .all()
    )
