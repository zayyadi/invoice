from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate, PaymentListItem, PaymentSummary
from app.services.payment_service import (
    create_payment,
    delete_payment,
    get_payment_or_404,
    get_payments_by_invoice,
    list_payments,
    update_payment,
    get_payment_summary,
)

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.get("", response_model=list[PaymentListItem])
def list_payments_endpoint(
    invoice_id: UUID | None = Query(None, description="Filter by invoice ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all payments for the current user."""
    payments = list_payments(
        db, 
        user_id=current_user.id,
        invoice_id=invoice_id,
        limit=limit,
        offset=offset,
    )
    
    # Transform to list items with invoice info
    return [
        PaymentListItem(
            id=payment.id,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            invoice_number=payment.invoice.invoice_number,
            customer_name=payment.invoice.customer_name,
        )
        for payment in payments
    ]


@router.post("", response_model=PaymentRead, status_code=201)
def create_payment_endpoint(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new payment for an invoice."""
    return create_payment(db, payload, current_user)


@router.get("/summary", response_model=PaymentSummary)
def get_payments_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment summary for the current user."""
    return get_payment_summary(db, current_user.id)


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment_endpoint(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific payment by ID."""
    payment = get_payment_or_404(db, payment_id, current_user.id)
    return payment


@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment_endpoint(
    payment_id: str,
    payload: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a payment."""
    payment = get_payment_or_404(db, payment_id, current_user.id)
    return update_payment(db, payment, payload, current_user)


@router.delete("/{payment_id}", status_code=204)
def delete_payment_endpoint(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a payment."""
    payment = get_payment_or_404(db, payment_id, current_user.id)
    delete_payment(db, payment, current_user)
    return None


@router.get("/invoice/{invoice_id}", response_model=list[PaymentRead])
def get_invoice_payments(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all payments for a specific invoice."""
    from app.services.invoice_service import get_invoice_or_404
    
    # Verify invoice belongs to user
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    
    return get_payments_by_invoice(db, UUID(invoice_id), current_user.id)
