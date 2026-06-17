import os
import uuid
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.invoice_service import get_invoice_or_404

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/svg+xml"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
MAX_LOGO_BYTES = 2 * 1024 * 1024


async def save_logo_for_invoice(
    db: Session, invoice_id: str, upload: UploadFile, user_id: UUID | None = None
) -> str:
    invoice = get_invoice_or_404(db, invoice_id, user_id)

    content_type = upload.content_type or ""
    extension = os.path.splitext(upload.filename or "")[1].lower()

    if content_type not in ALLOWED_CONTENT_TYPES or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PNG/JPG/SVG logos are allowed")

    payload = await upload.read()
    if len(payload) > MAX_LOGO_BYTES:
        raise HTTPException(status_code=400, detail="Logo exceeds 2MB")

    os.makedirs(settings.logos_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = os.path.join(settings.logos_dir, filename)

    with open(destination, "wb") as logo_file:
        logo_file.write(payload)

    invoice.logo_path = f"/media/logos/{filename}"
    db.commit()

    return invoice.logo_path
