from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.export_service import generate_image, generate_pdf
from app.services.invoice_service import get_invoice

router = APIRouter(prefix="/api/v1/invoices", tags=["Exports"])


@router.post("/{invoice_id}/export/pdf")
def export_invoice_pdf(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export invoice as PDF."""
    # Verify the invoice belongs to the current user
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    try:
        output = generate_pdf(db, invoice_id, current_user.id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return FileResponse(output, media_type="application/pdf", filename=f"invoice-{invoice_id}.pdf")


@router.post("/{invoice_id}/export/image")
async def export_invoice_image(
    invoice_id: str,
    format: str = Query(default="png", pattern="^(png|jpg)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export invoice as PNG or JPG image."""
    # Verify the invoice belongs to the current user
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    try:
        output = await generate_image(db, invoice_id, current_user.id, fmt=format)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    media_type = "image/png" if format == "png" else "image/jpeg"
    return FileResponse(output, media_type=media_type, filename=f"invoice-{invoice_id}.{format}")
