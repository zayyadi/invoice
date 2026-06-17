from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.file_service import save_logo_for_invoice
from app.services.invoice_service import get_invoice

router = APIRouter(prefix="/api/v1/invoices", tags=["Uploads"])


@router.post("/{invoice_id}/logo")
async def upload_logo_endpoint(
    invoice_id: str,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a logo for an invoice."""
    # Verify the invoice belongs to the current user
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    logo_path = await save_logo_for_invoice(db, invoice_id, logo, current_user.id)
    return {"logo_path": logo_path}
