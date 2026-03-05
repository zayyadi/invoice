import os

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.invoice_service import get_invoice_or_404
from app.services.render_service import render_invoice_html


def generate_pdf(db: Session, invoice_id: str) -> str:
    try:
        from weasyprint import HTML
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PDF export dependency missing: install with `pip install weasyprint`."
        ) from exc

    invoice = get_invoice_or_404(db, invoice_id)
    html = render_invoice_html(invoice)
    os.makedirs(settings.exports_dir, exist_ok=True)
    output_path = os.path.join(settings.exports_dir, f"{invoice_id}.pdf")
    HTML(string=html, base_url=".").write_pdf(output_path)
    return output_path


async def generate_image(db: Session, invoice_id: str, fmt: str = "png") -> str:
    try:
        from playwright.async_api import async_playwright
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Image export dependency missing: install with `pip install playwright` "
            "and run `playwright install chromium`."
        ) from exc

    invoice = get_invoice_or_404(db, invoice_id)
    html = render_invoice_html(invoice)
    os.makedirs(settings.exports_dir, exist_ok=True)
    output_path = os.path.join(settings.exports_dir, f"{invoice_id}.{fmt}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1240, "height": 1754})
        await page.set_content(html, wait_until="networkidle")

        if fmt == "jpg":
            await page.screenshot(path=output_path, full_page=True, type="jpeg", quality=90)
        else:
            await page.screenshot(path=output_path, full_page=True, type="png")

        await browser.close()

    return output_path
