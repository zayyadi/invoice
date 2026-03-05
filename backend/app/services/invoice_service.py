from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.invoice import Invoice, InvoiceItem
from app.schemas.invoice import InvoiceCreate
from app.utils.money import quantize_money


def _calculate_totals(payload: InvoiceCreate):
    subtotal = Decimal("0")
    item_rows: list[dict] = []

    for item in payload.items:
        line_total = quantize_money(Decimal(item.quantity) * item.unit_price)
        subtotal += line_total
        item_rows.append(
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": quantize_money(item.unit_price),
                "line_total": line_total,
            }
        )

    subtotal = quantize_money(subtotal)
    tax_amount = quantize_money(subtotal * payload.tax_rate / Decimal("100"))
    total_amount = quantize_money(subtotal + tax_amount)

    return item_rows, subtotal, tax_amount, total_amount


def create_invoice(db: Session, payload: InvoiceCreate) -> Invoice:
    existing = db.query(Invoice).filter(Invoice.invoice_number == payload.invoice_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="invoice_number already exists")

    item_rows, subtotal, tax_amount, total_amount = _calculate_totals(payload)

    invoice = Invoice(
        invoice_number=payload.invoice_number,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        currency=payload.currency.upper(),
        notes=payload.notes,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
    )

    invoice.items = [InvoiceItem(**row) for row in item_rows]
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, invoice_id: str) -> Invoice | None:
    try:
        invoice_uuid = UUID(invoice_id)
    except ValueError:
        return None

    return (
        db.query(Invoice)
        .options(selectinload(Invoice.items))
        .filter(Invoice.id == invoice_uuid)
        .first()
    )


def get_invoice_or_404(db: Session, invoice_id: str) -> Invoice:
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
