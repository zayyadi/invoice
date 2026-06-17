from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.client import Client
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate


def create_client(db: Session, data: ClientCreate, user: User) -> Client:
    client = Client(
        user_id=user.id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        address=data.address,
        tax_id=data.tax_id,
        notes=data.notes,
        default_currency=data.default_currency or user.default_currency,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: UUID, user_id: UUID) -> Client | None:
    return (
        db.query(Client)
        .filter(Client.id == client_id, Client.user_id == user_id)
        .first()
    )


def get_client_or_404(db: Session, client_id: UUID, user_id: UUID) -> Client:
    client = get_client(db, client_id, user_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


def list_clients(
    db: Session,
    user_id: UUID,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Client]:
    query = db.query(Client).filter(Client.user_id == user_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Client.name.ilike(search_term) | Client.email.ilike(search_term)
        )

    return query.order_by(Client.name).offset(skip).limit(limit).all()


def list_clients_with_stats(
    db: Session,
    user_id: UUID,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """List clients with invoice statistics."""
    from sqlalchemy import func, case

    query = (
        db.query(
            Client,
            func.count(Invoice.id).label("invoice_count"),
            func.coalesce(func.sum(Invoice.total_amount), 0).label("total_invoiced"),
            func.coalesce(func.sum(Invoice.paid_amount), 0).label("total_paid"),
        )
        .outerjoin(Invoice, Client.id == Invoice.client_id)
        .filter(Client.user_id == user_id)
        .group_by(Client.id)
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Client.name.ilike(search_term) | Client.email.ilike(search_term)
        )

    results = query.order_by(Client.name).offset(skip).limit(limit).all()

    return [
        {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "default_currency": client.default_currency,
            "invoice_count": invoice_count,
            "total_invoiced": str(total_invoiced),
            "total_paid": str(total_paid),
        }
        for client, invoice_count, total_invoiced, total_paid in results
    ]


def update_client(
    db: Session, client: Client, data: ClientUpdate
) -> Client:
    if data.name is not None:
        client.name = data.name
    if data.email is not None:
        client.email = data.email
    if data.phone is not None:
        client.phone = data.phone
    if data.address is not None:
        client.address = data.address
    if data.tax_id is not None:
        client.tax_id = data.tax_id
    if data.notes is not None:
        client.notes = data.notes
    if data.default_currency is not None:
        client.default_currency = data.default_currency

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client: Client) -> None:
    """Delete a client. Invoices linked to this client will have client_id set to NULL."""
    db.delete(client)
    db.commit()


def get_client_invoices(
    db: Session, client_id: UUID, user_id: UUID
) -> list[Invoice]:
    """Get all invoices for a specific client."""
    return (
        db.query(Invoice)
        .filter(Invoice.client_id == client_id, Invoice.user_id == user_id)
        .order_by(Invoice.issue_date.desc())
        .all()
    )
