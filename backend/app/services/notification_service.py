import logging

logger = logging.getLogger("invoice.notification")


def send_invoice_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str | None = None,
    smtp_host: str = "localhost",
    smtp_port: int = 587,
    smtp_user: str | None = None,
    smtp_password: str | None = None,
    from_email: str | None = None,
) -> bool:
    logger.info("Email notifications are disabled; skipping invoice email to %s.", to_email)
    return False


def format_whatsapp_message(invoice_number: str, amount: str, due_date: str) -> str:
    return (
        f"Hello, your invoice *{invoice_number}* is ready.\n"
        f"Amount: {amount}\n"
        f"Due date: {due_date}\n\n"
        f"Please review and arrange payment. Thank you!"
    )


def build_whatsapp_url(phone: str, message: str) -> str:
    import urllib.parse
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{phone.lstrip('+')}?text={encoded}"
