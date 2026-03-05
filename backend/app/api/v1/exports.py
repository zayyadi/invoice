from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.export_service import generate_image, generate_pdf

router = APIRouter(prefix="/api/v1/invoices", tags=["Exports"])


@router.post("/{invoice_id}/export/pdf")
def export_invoice_pdf(invoice_id: str, db: Session = Depends(get_db)):
    try:
        output = generate_pdf(db, invoice_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return FileResponse(output, media_type="application/pdf", filename=f"invoice-{invoice_id}.pdf")


@router.post("/{invoice_id}/export/image")
async def export_invoice_image(
    invoice_id: str,
    format: str = Query(default="png", pattern="^(png|jpg)$"),
    db: Session = Depends(get_db),
):
    try:
        output = await generate_image(db, invoice_id, fmt=format)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    media_type = "image/png" if format == "png" else "image/jpeg"
    return FileResponse(output, media_type=media_type, filename=f"invoice-{invoice_id}.{format}")
