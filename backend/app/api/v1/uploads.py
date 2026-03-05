from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.file_service import save_logo_for_invoice

router = APIRouter(prefix="/api/v1/invoices", tags=["Uploads"])


@router.post("/{invoice_id}/logo")
async def upload_logo_endpoint(
    invoice_id: str,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logo_path = await save_logo_for_invoice(db, invoice_id, logo)
    return {"logo_path": logo_path}
