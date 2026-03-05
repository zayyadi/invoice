# Deployment Guide (Nginx + systemd + CI/CD)

## 1. Files in this folder

- `nginx/invoice.conf`: Nginx reverse proxy config
- `systemd/invoice-backend.service`: FastAPI service
- `systemd/invoice-frontend.service`: Next.js service
- `systemd/invoice-telegram-bot.service`: Telegram bot service
- `scripts/bootstrap_server.sh`: first-time package install
- `scripts/deploy_remote.sh`: deploy/update script used by CI
- `scripts/ci_backend.sh`: backend CI checks
- `scripts/ci_frontend.sh`: frontend CI checks

## 2. Server prerequisites

- Ubuntu/Debian host
- Domain name pointing to server
- SSH access with a sudo-capable user
- PostgreSQL already available and reachable from backend

Optional one-time bootstrap:

```bash
bash deploy/scripts/bootstrap_server.sh
```

## 3. Required environment files on server

- `/opt/invoice/backend/.env`
- `/opt/invoice/frontend/.env`

## 4. Install and start services manually (first setup)

```bash
APP_ROOT=/opt/invoice bash /opt/invoice/deploy/scripts/deploy_remote.sh
```

## 5. GitHub Actions secrets

Add these repository secrets:

- `SSH_PRIVATE_KEY` (private key for server login)
- `SSH_HOST` (server hostname/IP)
- `SSH_USER` (deploy user)
- `SSH_PORT` (optional, defaults to `22`)
- `APP_ROOT` (optional, defaults to `/opt/invoice`)

## 6. TLS certificate

After Nginx config is installed and DNS resolves:

```bash
sudo certbot --nginx -d invoice.example.com
```

Then update `server_name` and cert paths in `deploy/nginx/invoice.conf`.
