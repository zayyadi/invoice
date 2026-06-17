# VPS Deployment Guide

This app deploys as three local services behind Nginx:

- FastAPI backend on `127.0.0.1:8000`
- Next.js frontend on `127.0.0.1:3000`
- Optional Telegram bot worker
- PostgreSQL, either local on the VPS or external/managed

The recommended entrypoint is `deploy/scripts/deploy_vps.sh`.

## Server Requirements

- Ubuntu 22.04/24.04 or Debian 12 VPS
- A sudo-capable SSH user
- A domain A record pointing to the VPS, or the server public IP for HTTP-only deployment
- At least 1 GB RAM, 2 GB preferred for Next.js builds and Playwright/WeasyPrint

The script installs Nginx, Python, Node.js 22 when needed, Certbot, PostgreSQL client tools, and native libraries needed by PDF/image rendering.

## First Deploy With Public IP

SSH into the VPS, clone or upload the repo, then run:

```bash
cd /path/to/invoice
DOMAIN=203.0.113.10 \
INSTALL_POSTGRES=true \
bash deploy/scripts/deploy_vps.sh
```

Replace `203.0.113.10` with your VPS public IP. This deploys the app over plain HTTP at `http://203.0.113.10`.

Let's Encrypt normally does not issue certificates for bare public IP addresses, so keep `ENABLE_TLS=false` when using an IP. If you later add a domain, point the domain to the VPS and rerun the script with `ENABLE_TLS=true`.

## First Deploy With Domain

SSH into the VPS, clone or upload the repo, then run:

```bash
cd /path/to/invoice
DOMAIN=invoice.example.com \
EMAIL=admin@example.com \
ENABLE_TLS=true \
INSTALL_POSTGRES=true \
bash deploy/scripts/deploy_vps.sh
```

Use your real domain and email. With `INSTALL_POSTGRES=true`, the script installs PostgreSQL locally, creates the database/user, writes env files, runs migrations, builds the frontend, writes systemd units, configures Nginx, and requests a Let's Encrypt certificate.

If DNS is not ready yet, deploy HTTP first:

```bash
DOMAIN=invoice.example.com \
INSTALL_POSTGRES=true \
bash deploy/scripts/deploy_vps.sh
```

After DNS resolves, rerun with TLS:

```bash
DOMAIN=invoice.example.com \
EMAIL=admin@example.com \
ENABLE_TLS=true \
bash deploy/scripts/deploy_vps.sh
```

## Managed PostgreSQL

If you use a managed database, leave `INSTALL_POSTGRES=false` and set `/opt/invoice/backend/.env` before rerunning the script:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DB_NAME
```

The script preserves existing `.env` values by default. To intentionally rewrite deploy-managed keys, run with `OVERWRITE_ENV=true`.

## Useful Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ROOT` | `/opt/invoice` | Final app directory on the VPS |
| `APP_USER` | `www-data` | systemd runtime user/group |
| `DOMAIN` | `invoice.example.com` | Nginx server name and public app URL; can be a public IP for HTTP |
| `EMAIL` | empty | Let's Encrypt registration email |
| `ENABLE_TLS` | `false` | Run Certbot and redirect HTTP to HTTPS; requires a real DNS name |
| `INSTALL_POSTGRES` | `false` | Install and configure local PostgreSQL |
| `DB_NAME` | `invoice_db` | Local database name |
| `DB_USER` | `invoice` | Local database user |
| `DB_PASSWORD` | generated | Local database password |
| `BACKEND_PORT` | `8000` | Backend bind port |
| `FRONTEND_PORT` | `3000` | Frontend bind port |
| `RUN_TELEGRAM_BOT` | `auto` | `auto`, `true`, or `false` |
| `OVERWRITE_ENV` | `false` | Replace existing env values when true |

## Environment Files

The deploy script creates these files if they do not exist:

- `/opt/invoice/backend/.env`
- `/opt/invoice/frontend/.env`

Backend production values should look like:

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+psycopg2://invoice:password@127.0.0.1:5432/invoice_db
BACKEND_BASE_URL=https://invoice.example.com
CORS_ORIGINS=["https://invoice.example.com"]
MEDIA_ROOT=/opt/invoice/backend/media
LOGOS_DIR=/opt/invoice/backend/media/logos
EXPORTS_DIR=/opt/invoice/backend/media/exports
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USER_IDS=[]
```

Frontend production value:

```env
NEXT_PUBLIC_API_URL=https://invoice.example.com
```

Set `TELEGRAM_BOT_TOKEN` before deployment if you want the bot service enabled automatically.

## Updating an Existing VPS

Pull or upload the latest code, then rerun the deploy script:

```bash
cd /path/to/invoice
DOMAIN=invoice.example.com \
ENABLE_TLS=true \
EMAIL=admin@example.com \
bash deploy/scripts/deploy_vps.sh
```

The script syncs code into `APP_ROOT`, reinstalls dependencies as needed, runs Alembic migrations, rebuilds the frontend, and restarts services.

## Service Commands

```bash
sudo systemctl status invoice-backend
sudo systemctl status invoice-frontend
sudo systemctl status invoice-telegram-bot
sudo journalctl -u invoice-backend -f
sudo journalctl -u invoice-frontend -f
sudo journalctl -u invoice-telegram-bot -f
```

Restart services manually:

```bash
sudo systemctl restart invoice-backend invoice-frontend
sudo systemctl restart invoice-telegram-bot
sudo systemctl reload nginx
```

## Nginx

The script writes `/etc/nginx/sites-available/invoice.conf` and enables it. The tracked template lives at `deploy/nginx/invoice.conf` for manual installs.

Manual install:

```bash
sudo cp deploy/nginx/invoice.conf /etc/nginx/sites-available/invoice.conf
sudo sed -i 's/invoice.example.com/your-domain.com/g' /etc/nginx/sites-available/invoice.conf
sudo ln -sfn /etc/nginx/sites-available/invoice.conf /etc/nginx/sites-enabled/invoice.conf
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```

## Firewall

If UFW is enabled:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Do not expose ports `8000`, `3000`, or `5432` publicly unless you have a specific reason.

## Verification

Run these after deployment:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -I http://203.0.113.10
```

Use `curl -I https://invoice.example.com` instead after deploying with a domain and `ENABLE_TLS=true`.

In the browser, create an invoice, upload a logo, and export PDF/PNG. Those paths verify FastAPI, Next.js, PostgreSQL, Nginx proxying, media permissions, Playwright, and WeasyPrint.

## Files in This Folder

- `scripts/deploy_vps.sh`: main VPS bootstrap/deploy script
- `scripts/bootstrap_server.sh`: small legacy bootstrap helper
- `scripts/deploy_remote.sh`: legacy CI deploy/update helper
- `scripts/ci_backend.sh`: backend CI checks
- `scripts/ci_frontend.sh`: frontend CI checks
- `nginx/invoice.conf`: manual Nginx reverse proxy template
- `systemd/*.service`: legacy static service templates
