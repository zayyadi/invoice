import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings


template_dir = Path(__file__).resolve().parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


def _abs_logo_url(logo_path: str | None) -> str | None:
    if not logo_path:
        return None
    return f"{settings.backend_base_url}{logo_path}"


def render_invoice_html(invoice) -> str:
    template = env.get_template("invoice.html")
    context = {
        "invoice": invoice,
        "logo_abs_url": _abs_logo_url(getattr(invoice, "logo_path", None)),
    }
    return template.render(**context)
