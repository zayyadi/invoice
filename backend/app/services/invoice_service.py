from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.invoice import Invoice, InvoiceItem
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
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


from uuid import UUID
from app.models.user import User
from app.models.client import Client

def create_invoice(db: Session, payload: InvoiceCreate, user: User) -> Invoice:
    existing = db.query(Invoice).filter(
        Invoice.invoice_number == payload.invoice_number,
        Invoice.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="invoice_number already exists")

    # If client_id is provided, fetch client and use their details
    client_id = None
    if payload.client_id:
        try:
            client_uuid = UUID(payload.client_id)
            client = db.query(Client).filter(
                Client.id == client_uuid,
                Client.user_id == user.id
            ).first()
            if client:
                client_id = client.id
        except ValueError:
            pass  # Invalid UUID, ignore

    item_rows, subtotal, tax_amount, total_amount = _calculate_totals(payload)

    invoice = Invoice(
        user_id=user.id,
        client_id=client_id,
        invoice_number=payload.invoice_number,
        issuer_name=payload.issuer_name or user.full_name,
        issuer_email=payload.issuer_email,
        issuer_phone=payload.issuer_phone or user.phone,
        issuer_address=payload.issuer_address,
        payment_bank_name=payload.payment_bank_name,
        payment_account_number=payload.payment_account_number,
        payment_account_name=payload.payment_account_name,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        currency=payload.currency.upper() if payload.currency else user.default_currency,
        tax_rate=payload.tax_rate,
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


def get_invoice(db: Session, invoice_id: str, user_id: UUID | None = None) -> Invoice | None:
    try:
        invoice_uuid = UUID(invoice_id)
    except ValueError:
        return None

    query = (
        db.query(Invoice)
        .options(selectinload(Invoice.items))
        .filter(Invoice.id == invoice_uuid)
    )
    
    if user_id:
        query = query.filter(Invoice.user_id == user_id)
    
    return query.first()


def get_invoice_or_404(db: Session, invoice_id: str, user_id: UUID | None = None) -> Invoice:
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


def update_invoice(db: Session, invoice: Invoice, payload: InvoiceUpdate) -> Invoice:
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "currency" and value:
            value = value.upper()
        setattr(invoice, field, value)

    if "tax_rate" in update_data:
        invoice.tax_amount = quantize_money(invoice.subtotal * invoice.tax_rate / Decimal("100"))
        invoice.total_amount = quantize_money(invoice.subtotal + invoice.tax_amount)

    db.commit()
    db.refresh(invoice)
    return invoice
