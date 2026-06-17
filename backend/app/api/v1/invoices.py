from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.invoice import InvoiceStatus
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceUpdate, ShareRequest
from app.services.invoice_service import create_invoice, get_invoice, get_invoice_or_404, update_invoice
from app.services.invoice_status_service import (
    transition_status,
    mark_as_sent,
    mark_as_viewed,
    mark_as_paid,
    mark_as_partial,
    mark_as_cancelled,
    get_status_history,
)
from app.services.notification_service import format_whatsapp_message, build_whatsapp_url

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])


@router.get("", response_model=list[InvoiceRead])
def list_invoices(
    status: InvoiceStatus | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search by invoice number or customer name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all invoices for the current user with optional filtering."""
    from sqlalchemy import or_
    from sqlalchemy.orm import selectinload
    from app.models.invoice import Invoice
    
    query = (
        db.query(Invoice)
        .options(selectinload(Invoice.items))
        .filter(Invoice.user_id == current_user.id)
    )
    
    if status:
        query = query.filter(Invoice.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Invoice.invoice_number.ilike(search_term),
                Invoice.customer_name.ilike(search_term)
            )
        )
    
    invoices = query.order_by(Invoice.created_at.desc()).all()
    return invoices


@router.post("", response_model=InvoiceRead, status_code=201)
def create_invoice_endpoint(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice."""
    return create_invoice(db, payload, current_user)


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice_endpoint(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific invoice by ID."""
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceRead)
def update_invoice_endpoint(
    invoice_id: str,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update invoice editable metadata without changing line items."""
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    return update_invoice(db, invoice, payload)


@router.post("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: str,
    status: InvoiceStatus,
    notes: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update invoice status with validation and history tracking."""
    from app.models.invoice import Invoice
    
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    
    invoice = transition_status(
        db, invoice, status, 
        changed_by=str(current_user.id),
        notes=notes
    )
    
    return {
        "message": "Status updated successfully",
        "invoice_id": str(invoice.id),
        "status": invoice.status.value,
    }


@router.post("/{invoice_id}/send")
def send_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark invoice as sent."""
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    invoice = mark_as_sent(db, invoice, changed_by=str(current_user.id))
    
    return {
        "message": "Invoice marked as sent",
        "invoice_id": str(invoice.id),
        "status": invoice.status.value,
        "sent_at": invoice.sent_at,
    }


@router.post("/{invoice_id}/view")
def view_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark invoice as viewed by client."""
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    invoice = mark_as_viewed(db, invoice, changed_by=str(current_user.id))
    
    return {
        "message": "Invoice marked as viewed",
        "invoice_id": str(invoice.id),
        "status": invoice.status.value,
        "viewed_at": invoice.viewed_at,
    }


@router.post("/{invoice_id}/pay")
def pay_invoice(
    invoice_id: str,
    notes: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark invoice as fully paid."""
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    invoice = mark_as_paid(db, invoice, changed_by=str(current_user.id), notes=notes)
    
    return {
        "message": "Invoice marked as paid",
        "invoice_id": str(invoice.id),
        "status": invoice.status.value,
        "paid_at": invoice.paid_at,
    }


@router.post("/{invoice_id}/cancel")
def cancel_invoice(
    invoice_id: str,
    reason: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an invoice."""
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    invoice = mark_as_cancelled(db, invoice, changed_by=str(current_user.id), reason=reason)
    
    return {
        "message": "Invoice cancelled",
        "invoice_id": str(invoice.id),
        "status": invoice.status.value,
    }


@router.get("/{invoice_id}/history")
def get_invoice_history(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get status history for an invoice."""
    from uuid import UUID
    
    invoice = get_invoice_or_404(db, invoice_id, current_user.id)
    history = get_status_history(db, UUID(invoice_id))
    
    return [
        {
            "id": str(h.id),
            "status": h.status,
            "changed_by": h.changed_by,
            "notes": h.notes,
            "created_at": h.created_at,
        }
        for h in history
    ]


@router.post("/{invoice_id}/share")
def share_invoice_endpoint(
    invoice_id: str,
    request: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate share links for an invoice."""
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    results = {}

    if request.email:
        results["email"] = False
        results["email_disabled"] = True

    if request.phone:
        msg = format_whatsapp_message(
            invoice.invoice_number,
            f"{invoice.currency} {invoice.total_amount}",
            str(invoice.due_date),
        )
        if request.message:
            msg = request.message
        results["whatsapp_url"] = build_whatsapp_url(request.phone, msg)

    if request.telegram_id:
        results["telegram"] = {"chat_id": request.telegram_id, "note": "configure telegram bot token to enable"}

    return results
