# Backend: Invoice Generator API + Telegram Bot

## Run Backend API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Checks

```bash
cd backend
python scripts/check_backend.py
```

This compiles the application modules and runs the backend unittest suite with
an isolated in-memory SQLite database.

## Run Telegram Bot

Set in `backend/.env`:

```env
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_ALLOWED_USER_IDS=[123456789]
```

Then run:

```bash
cd backend
source .venv/bin/activate
python -m app.bot.telegram_bot
```

The bot collects invoice details and returns PDF or image (PNG/JPG).
It now includes Bill From / issuer details before the customer details.
