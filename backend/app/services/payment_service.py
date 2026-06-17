from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentServiceError(Exception):
    """Custom exception for payment service errors."""
    pass


def get_payment(db: Session, payment_id: UUID, user_id: UUID) -> Payment | None:
    """Get a payment by ID for a specific user."""
    return (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.user_id == user_id)
        .first()
    )


def get_payment_or_404(db: Session, payment_id: str, user_id: UUID) -> Payment:
    """Get a payment by ID or raise 404."""
    payment = get_payment(db, UUID(payment_id), user_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


def list_payments(
    db: Session,
    user_id: UUID,
    invoice_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Payment]:
    """List payments for a user, optionally filtered by invoice."""
    query = db.query(Payment).filter(Payment.user_id == user_id)
    
    if invoice_id:
        query = query.filter(Payment.invoice_id == invoice_id)
    
    return (
        query.order_by(Payment.payment_date.desc(), Payment.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def create_payment(
    db: Session,
    payload: PaymentCreate,
    user: User,
) -> Payment:
    """Create a new payment and update invoice status."""
    from app.services.invoice_service import get_invoice_or_404
    
    # Get the invoice
    invoice = get_invoice_or_404(db, str(payload.invoice_id), user.id)
    
    # Validate payment amount
    outstanding = invoice.total_amount - invoice.paid_amount
    if payload.amount > outstanding:
        raise HTTPException(
            status_code=400,
            detail=f"Payment amount ({payload.amount}) exceeds outstanding balance ({outstanding})"
        )
    
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")
    
    # Create payment record
    payment = Payment(
        invoice_id=payload.invoice_id,
        user_id=user.id,
        amount=payload.amount,
        payment_date=payload.payment_date or date.today(),
        payment_method=payload.payment_method or "bank_transfer",
        reference_number=payload.reference_number,
        notes=payload.notes,
    )
    
    db.add(payment)
    
    # Update invoice paid_amount
    invoice.paid_amount += payload.amount
    
    # Update invoice status based on payment
    if invoice.paid_amount >= invoice.total_amount:
        from app.services.invoice_status_service import mark_as_paid
        mark_as_paid(db, invoice, changed_by=str(user.id), notes=f"Full payment recorded")
    else:
        from app.services.invoice_status_service import transition_status
        transition_status(
            db, invoice, InvoiceStatus.PARTIAL,
            changed_by=str(user.id),
            notes=f"Partial payment of {payload.amount} recorded"
        )
    
    db.commit()
    db.refresh(payment)
    
    return payment


def update_payment(
    db: Session,
    payment: Payment,
    payload: PaymentUpdate,
    user: User,
) -> Payment:
    """Update a payment and recalculate invoice totals."""
    invoice = payment.invoice
    old_amount = payment.amount
    
    # Calculate new paid amount for invoice
    amount_diff = (payload.amount or old_amount) - old_amount
    new_paid_amount = invoice.paid_amount + amount_diff
    
    # Validate new total doesn't exceed invoice total
    if new_paid_amount > invoice.total_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Updated payment would exceed invoice total"
        )
    
    if new_paid_amount < 0:
        raise HTTPException(status_code=400, detail="Payment amount cannot result in negative paid amount")
    
    # Update payment fields
    if payload.amount is not None:
        payment.amount = payload.amount
    if payload.payment_date is not None:
        payment.payment_date = payload.payment_date
    if payload.payment_method is not None:
        payment.payment_method = payload.payment_method
    if payload.reference_number is not None:
        payment.reference_number = payload.reference_number
    if payload.notes is not None:
        payment.notes = payload.notes
    
    # Update invoice paid_amount
    invoice.paid_amount = new_paid_amount
    
    # Update invoice status
    if invoice.paid_amount >= invoice.total_amount:
        invoice.status = InvoiceStatus.PAID
        if not invoice.paid_at:
            from datetime import datetime
            invoice.paid_at = datetime.utcnow()
    elif invoice.paid_amount > 0:
        invoice.status = InvoiceStatus.PARTIAL
    else:
        # Revert to previous status (simplified: go back to sent)
        invoice.status = InvoiceStatus.SENT
    
    db.commit()
    db.refresh(payment)
    
    return payment


def delete_payment(db: Session, payment: Payment, user: User) -> None:
    """Delete a payment and update invoice totals."""
    invoice = payment.invoice
    
    # Subtract payment amount from invoice
    invoice.paid_amount -= payment.amount
    if invoice.paid_amount < 0:
        invoice.paid_amount = Decimal("0")
    
    # Update invoice status
    if invoice.paid_amount == 0:
        invoice.status = InvoiceStatus.SENT
        invoice.paid_at = None
    elif invoice.paid_amount < invoice.total_amount:
        invoice.status = InvoiceStatus.PARTIAL
    
    db.delete(payment)
    db.commit()


def get_payment_summary(db: Session, user_id: UUID) -> dict:
    """Get summary of payments for a user."""
    from sqlalchemy import func
    
    result = (
        db.query(
            func.count(Payment.id).label("total_payments"),
            func.sum(Payment.amount).label("total_amount"),
        )
        .filter(Payment.user_id == user_id)
        .first()
    )
    
    return {
        "total_payments": result.total_payments or 0,
        "total_amount": float(result.total_amount or 0),
    }


def get_payments_by_invoice(db: Session, invoice_id: UUID, user_id: UUID) -> list[Payment]:
    """Get all payments for a specific invoice."""
    return (
        db.query(Payment)
        .filter(Payment.invoice_id == invoice_id, Payment.user_id == user_id)
        .order_by(Payment.payment_date.desc())
        .all()
    )
