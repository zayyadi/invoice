from __future__ import annotations

import os
import uuid
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.media import configure_media_dirs
from app.schemas.invoice import InvoiceCreate, InvoiceItemCreate
from app.services.export_service import generate_image, generate_pdf
from app.services.invoice_service import create_invoice, get_invoice_or_404

(
    INVOICE_NUMBER,
    CUSTOMER_NAME,
    CUSTOMER_EMAIL,
    ISSUE_DATE,
    DUE_DATE,
    TAX_RATE,
    ITEM_DESCRIPTION,
    ITEM_QUANTITY,
    ITEM_UNIT_PRICE,
    ADD_ANOTHER_ITEM,
    NOTES,
    LOGO,
    OUTPUT_FORMAT,
) = range(13)

MAX_LOGO_BYTES = 2 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
logger = logging.getLogger("invoice.telegram_bot")


def _draft(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    if "invoice_draft" not in context.user_data:
        context.user_data["invoice_draft"] = {}
    return context.user_data["invoice_draft"]


def _parse_date(text: str):
    return datetime.strptime(text.strip(), "%Y-%m-%d").date()


def _parse_decimal(text: str) -> Decimal:
    return Decimal(text.strip())


def _is_allowed_user(user_id: int) -> bool:
    allowed = settings.telegram_allowed_user_ids
    return len(allowed) == 0 or user_id in allowed


def _attach_logo_to_invoice(db, invoice_id: str, logo_bytes: bytes, extension: str) -> None:
    extension = extension.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        extension = ".jpg"

    os.makedirs(settings.logos_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = Path(settings.logos_dir) / filename

    with open(destination, "wb") as file:
        file.write(logo_bytes)

    invoice = get_invoice_or_404(db, invoice_id)
    invoice.logo_path = f"/media/logos/{filename}"
    db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if not user or not _is_allowed_user(user.id):
        await update.message.reply_text("Access denied for this bot.")
        return ConversationHandler.END

    context.user_data["invoice_draft"] = {"currency": "NGN", "items": []}

    await update.message.reply_text(
        "Invoice wizard started. Type /cancel any time to stop.\n\n"
        "Step 1/10: Enter invoice number (example: INV-1001).",
        reply_markup=ReplyKeyboardRemove(),
    )
    return INVOICE_NUMBER


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("invoice_draft", None)
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def invoice_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Invoice number cannot be empty. Enter invoice number:")
        return INVOICE_NUMBER

    _draft(context)["invoice_number"] = text
    await update.message.reply_text("Step 2/10: Enter Bill To name (person who should pay):")
    return CUSTOMER_NAME


async def customer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Bill To name cannot be empty. Enter Bill To name:")
        return CUSTOMER_NAME

    _draft(context)["customer_name"] = text
    await update.message.reply_text("Step 3/10: Enter Bill To email or type `skip`.")
    return CUSTOMER_EMAIL


async def customer_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    _draft(context)["customer_email"] = None if text.lower() == "skip" else text
    await update.message.reply_text("Step 4/10: Enter issue date in YYYY-MM-DD format:")
    return ISSUE_DATE


async def issue_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    try:
        parsed = _parse_date(text)
    except ValueError:
        await update.message.reply_text("Invalid date. Use YYYY-MM-DD (example: 2026-03-04):")
        return ISSUE_DATE

    _draft(context)["issue_date"] = parsed
    await update.message.reply_text("Step 5/10: Enter due date in YYYY-MM-DD format:")
    return DUE_DATE


async def due_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    try:
        parsed = _parse_date(text)
    except ValueError:
        await update.message.reply_text("Invalid date. Use YYYY-MM-DD:")
        return DUE_DATE

    draft = _draft(context)
    if parsed < draft["issue_date"]:
        await update.message.reply_text("Due date cannot be before issue date. Enter due date again:")
        return DUE_DATE

    draft["due_date"] = parsed
    await update.message.reply_text("Step 6/10: Enter tax rate (example: 7.5, or 0):")
    return TAX_RATE


async def tax_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    try:
        value = _parse_decimal(text)
        if value < 0:
            raise ValueError("negative")
    except (InvalidOperation, ValueError):
        await update.message.reply_text("Invalid tax rate. Enter a non-negative number:")
        return TAX_RATE

    _draft(context)["tax_rate"] = value
    await update.message.reply_text("Step 7/10: Enter first item description:")
    return ITEM_DESCRIPTION


async def item_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Description cannot be empty. Enter item description:")
        return ITEM_DESCRIPTION

    _draft(context)["current_item"] = {"description": text}
    await update.message.reply_text("Enter item quantity (integer > 0):")
    return ITEM_QUANTITY


async def item_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    try:
        qty = int(text)
        if qty <= 0:
            raise ValueError("non-positive")
    except ValueError:
        await update.message.reply_text("Invalid quantity. Enter an integer greater than 0:")
        return ITEM_QUANTITY

    _draft(context)["current_item"]["quantity"] = qty
    await update.message.reply_text("Enter item unit price in Naira (example: 25000.00):")
    return ITEM_UNIT_PRICE


async def item_unit_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    try:
        price = _parse_decimal(text)
        if price < 0:
            raise ValueError("negative")
    except (InvalidOperation, ValueError):
        await update.message.reply_text("Invalid unit price. Enter a non-negative number:")
        return ITEM_UNIT_PRICE

    draft = _draft(context)
    item = draft["current_item"]
    item["unit_price"] = price
    draft["items"].append(item)
    draft.pop("current_item", None)

    keyboard = [["yes", "no"]]
    await update.message.reply_text(
        "Add another item? (yes/no)",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return ADD_ANOTHER_ITEM


async def add_another_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip().lower()
    if text == "yes":
        await update.message.reply_text("Enter next item description:", reply_markup=ReplyKeyboardRemove())
        return ITEM_DESCRIPTION
    if text == "no":
        await update.message.reply_text("Step 8/10: Enter notes or type `skip`:", reply_markup=ReplyKeyboardRemove())
        return NOTES

    await update.message.reply_text("Please reply with `yes` or `no`.")
    return ADD_ANOTHER_ITEM


async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    _draft(context)["notes"] = None if text.lower() == "skip" else text

    await update.message.reply_text(
        "Step 9/10: Send company logo as image/document, or type `skip`.")
    return LOGO


async def logo_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["pdf", "png", "jpg"]]
    await update.message.reply_text(
        "Step 10/10: Choose export format (pdf/png/jpg):",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return OUTPUT_FORMAT


async def logo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1] if update.message.photo else None
    document = update.message.document

    if not photo and not document:
        await update.message.reply_text("Send an image/document logo, or type `skip`.")
        return LOGO

    ext = ".jpg"
    if document and document.file_name:
        ext = Path(document.file_name).suffix.lower() or ".jpg"

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        await update.message.reply_text("Unsupported logo extension. Use PNG/JPG/SVG or type `skip`.")
        return LOGO

    telegram_file = await (photo.get_file() if photo else document.get_file())
    file_bytes = await telegram_file.download_as_bytearray()

    if len(file_bytes) > MAX_LOGO_BYTES:
        await update.message.reply_text("Logo too large. Max size is 2MB. Send a smaller file or type `skip`.")
        return LOGO

    draft = _draft(context)
    draft["logo_bytes"] = bytes(file_bytes)
    draft["logo_ext"] = ext

    keyboard = [["pdf", "png", "jpg"]]
    await update.message.reply_text(
        "Step 10/10: Choose export format (pdf/png/jpg):",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return OUTPUT_FORMAT


async def output_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = (update.message.text or "").strip().lower()
    if choice not in {"pdf", "png", "jpg"}:
        await update.message.reply_text("Invalid choice. Reply with pdf, png, or jpg.")
        return OUTPUT_FORMAT

    draft = _draft(context)
    if len(draft.get("items", [])) == 0:
        await update.message.reply_text("At least one item is required. Restart with /start.")
        return ConversationHandler.END

    payload = InvoiceCreate(
        invoice_number=draft["invoice_number"],
        customer_name=draft["customer_name"],
        customer_email=draft.get("customer_email"),
        issue_date=draft["issue_date"],
        due_date=draft["due_date"],
        currency="NGN",
        notes=draft.get("notes"),
        tax_rate=draft["tax_rate"],
        items=[
            InvoiceItemCreate(
                description=item["description"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
            for item in draft["items"]
        ],
    )

    await update.message.reply_text("Generating invoice. Please wait...", reply_markup=ReplyKeyboardRemove())

    try:
        configure_media_dirs()
        with SessionLocal() as db:
            invoice = create_invoice(db, payload)
            invoice_id = str(invoice.id)

            if draft.get("logo_bytes"):
                _attach_logo_to_invoice(db, invoice_id, draft["logo_bytes"], draft.get("logo_ext", ".jpg"))

            if choice == "pdf":
                output_path = generate_pdf(db, invoice_id)
            else:
                output_path = await generate_image(db, invoice_id, fmt=choice)

        with open(output_path, "rb") as file:
            await update.message.reply_document(
                document=file,
                filename=f"invoice-{invoice_id}.{choice}",
                caption=f"Invoice #{payload.invoice_number} ({choice.upper()})",
            )

        await update.message.reply_text(
            f"Done. Invoice ID: {invoice_id}\n"
            f"Use /start to create another invoice."
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Invoice generation failed")
        await update.message.reply_text(
            f"Failed to generate invoice: {exc}\n"
            "Check bot logs for stack trace."
        )

    context.user_data.pop("invoice_draft", None)
    return ConversationHandler.END


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to create an invoice, or /cancel to stop.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "An internal error occurred. Please try again or /cancel and restart."
        )


def build_application() -> Application:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in environment.")

    app = Application.builder().token(settings.telegram_bot_token).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INVOICE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, invoice_number)],
            CUSTOMER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, customer_name)],
            CUSTOMER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, customer_email)],
            ISSUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue_date)],
            DUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, due_date)],
            TAX_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tax_rate)],
            ITEM_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_description)],
            ITEM_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_quantity)],
            ITEM_UNIT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_unit_price)],
            ADD_ANOTHER_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_another_item)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, notes)],
            LOGO: [
                MessageHandler(filters.Regex(r"(?i)^skip$"), logo_skip),
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, logo_upload),
            ],
            OUTPUT_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, output_format)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))
    app.add_error_handler(on_error)
    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    configure_media_dirs()
    logger.info("Starting Telegram bot")
    app = build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
