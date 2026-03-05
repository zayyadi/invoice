#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/invoice}"
BACKEND_DIR="$APP_ROOT/backend"
FRONTEND_DIR="$APP_ROOT/frontend"

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required for service and nginx updates"
  exit 1
fi

echo "[1/8] Backend dependencies"
cd "$BACKEND_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install browser only if playwright exists and browser not installed.
if python -c "import playwright" >/dev/null 2>&1; then
  playwright install chromium || true
fi

echo "[2/8] Database migrations"
alembic upgrade head

echo "[3/8] Frontend dependencies + build"
cd "$FRONTEND_DIR"
npm ci
npm run build

echo "[4/8] Install systemd unit files"
sudo cp "$APP_ROOT/deploy/systemd/invoice-backend.service" /etc/systemd/system/
sudo cp "$APP_ROOT/deploy/systemd/invoice-frontend.service" /etc/systemd/system/
sudo cp "$APP_ROOT/deploy/systemd/invoice-telegram-bot.service" /etc/systemd/system/

echo "[5/8] Reload and restart services"
sudo systemctl daemon-reload
sudo systemctl enable invoice-backend invoice-frontend invoice-telegram-bot
sudo systemctl restart invoice-backend invoice-frontend invoice-telegram-bot

echo "[6/8] Install nginx config"
sudo cp "$APP_ROOT/deploy/nginx/invoice.conf" /etc/nginx/sites-available/invoice.conf
sudo ln -sfn /etc/nginx/sites-available/invoice.conf /etc/nginx/sites-enabled/invoice.conf

echo "[7/8] Validate nginx"
sudo nginx -t

echo "[8/8] Reload nginx"
sudo systemctl reload nginx

echo "Deployment complete."
