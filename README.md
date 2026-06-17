# Invoice Generator (FastAPI + Next.js)

Production-oriented full-stack invoice generator with:
- Invoice creation (NGN/Naira)
- Bill From issuer/contractor details on invoices
- Secure logo upload
- Invoice export as PDF and PNG/JPG
- Telegram bot invoice wizard (PDF/PNG/JPG output)
- FastAPI backend + PostgreSQL
- Next.js + Material UI frontend

## Run with Docker

```bash
docker compose up --build
```

Apps:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Telegram Bot: `telegram-bot` service (requires `TELEGRAM_BOT_TOKEN`)

## Smoke Test

After services are running, execute:

```bash
./scripts/smoke_test.sh
```

This verifies:
- invoice creation
- logo upload
- PDF export
- PNG/JPG export

## API Endpoints

- `POST /api/v1/invoices` create invoice
- `GET /api/v1/invoices/{invoice_id}` fetch invoice
- `POST /api/v1/invoices/{invoice_id}/logo` upload logo
- `POST /api/v1/invoices/{invoice_id}/export/pdf` export PDF
- `POST /api/v1/invoices/{invoice_id}/export/image?format=png|jpg` export image

## Telegram Bot

Start locally after backend dependencies are installed:

```bash
cd backend
source .venv/bin/activate
python -m app.bot.telegram_bot
```

Conversation flow asks for:
- invoice number
- bill from / issuer details
- customer details
- issue/due dates
- tax rate
- line items (repeatable)
- notes
- optional logo upload
- export format (`pdf`, `png`, `jpg`)

Set env in `backend/.env`:
- `TELEGRAM_BOT_TOKEN=<your_bot_token>`
- `TELEGRAM_ALLOWED_USER_IDS=[123456789]` (optional allowlist; empty means open)

## Local Run (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Notes

- For production file storage, move `media` to S3.
- Alembic is configured with an initial migration at `backend/alembic/versions/20260304_0001_init_invoices.py`.
- Consider background jobs for export generation at scale.
- Nginx, systemd, and CI/CD assets are in `deploy/` (see `deploy/DEPLOYMENT.md`).
