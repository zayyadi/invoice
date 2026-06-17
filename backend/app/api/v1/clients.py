from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate, ClientListItem
from app.schemas.invoice import InvoiceRead
from app.services import client_service
from app.services.invoice_service import get_invoice

router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


@router.get("", response_model=list[ClientListItem])
def list_clients(
    search: str | None = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all clients with invoice statistics."""
    return client_service.list_clients_with_stats(db, current_user.id, search=search)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new client."""
    return client_service.create_client(db, payload, current_user)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific client by ID."""
    client = client_service.get_client_or_404(db, client_id, current_user.id)
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: UUID,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a client."""
    client = client_service.get_client_or_404(db, client_id, current_user.id)
    return client_service.update_client(db, client, payload)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a client."""
    client = client_service.get_client_or_404(db, client_id, current_user.id)
    client_service.delete_client(db, client)
    return None


@router.get("/{client_id}/invoices", response_model=list[InvoiceRead])
def get_client_invoices(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all invoices for a specific client."""
    # First verify the client exists and belongs to the user
    client_service.get_client_or_404(db, client_id, current_user.id)
    return client_service.get_client_invoices(db, client_id, current_user.id)
