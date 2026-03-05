from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceRead
from app.services.invoice_service import create_invoice, get_invoice

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])


@router.post("", response_model=InvoiceRead, status_code=201)
def create_invoice_endpoint(payload: InvoiceCreate, db: Session = Depends(get_db)):
    return create_invoice(db, payload)


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice_endpoint(invoice_id: str, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
