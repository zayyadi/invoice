#!/usr/bin/env bash
set -euo pipefail

# Opinionated Ubuntu/Debian VPS deployment for the Invoice app.
# Run from this repository on the server:
#   DOMAIN=203.0.113.10 INSTALL_POSTGRES=true bash deploy/scripts/deploy_vps.sh
# Use ENABLE_TLS=true only when DOMAIN is a real DNS name, not a public IP.

APP_ROOT="${APP_ROOT:-/opt/invoice}"
APP_USER="${APP_USER:-www-data}"
DOMAIN="${DOMAIN:-invoice.example.com}"
EMAIL="${EMAIL:-}"
ENABLE_TLS="${ENABLE_TLS:-false}"
INSTALL_POSTGRES="${INSTALL_POSTGRES:-false}"
DB_NAME="${DB_NAME:-invoice_db}"
DB_USER="${DB_USER:-invoice}"
DB_PASSWORD="${DB_PASSWORD:-}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
RUN_TELEGRAM_BOT="${RUN_TELEGRAM_BOT:-auto}"
OVERWRITE_ENV="${OVERWRITE_ENV:-false}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CURRENT_USER="${SUDO_USER:-$USER}"

if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  SUDO=""
fi

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

log() {
  printf '\n[%s] %s\n' "$(date +%H:%M:%S)" "$*"
}

random_password() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 24 | tr -d '/+=' | cut -c1-24
  else
    date +%s%N | sha256sum | cut -c1-24
  fi
}

is_ip_address() {
  [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

set_env_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  local force="${4:-false}"

  if grep -q "^${key}=" "$file"; then
    if [[ "$OVERWRITE_ENV" == "true" || "$force" == "true" ]]; then
      sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    fi
  else
    printf '%s=%s\n' "$key" "$value" >> "$file"
  fi
}

install_packages() {
  log "Installing system packages"
  $SUDO apt-get update
  $SUDO apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    nginx \
    rsync \
    python3 \
    python3-venv \
    python3-pip \
    postgresql-client \
    certbot \
    python3-certbot-nginx \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info

  local node_major="0"
  if command -v node >/dev/null 2>&1; then
    node_major="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)"
  fi

  if [[ "$node_major" -lt 20 ]]; then
    log "Installing Node.js 22 LTS"
    curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO bash -
    $SUDO apt-get install -y nodejs
  fi

  if [[ "$INSTALL_POSTGRES" == "true" ]]; then
    log "Installing PostgreSQL server"
    $SUDO apt-get install -y postgresql
    $SUDO systemctl enable --now postgresql
  fi
}

sync_source() {
  log "Preparing app root at $APP_ROOT"
  $SUDO mkdir -p "$APP_ROOT"
  $SUDO chown -R "$CURRENT_USER":"$CURRENT_USER" "$APP_ROOT"

  if [[ "$SOURCE_ROOT" != "$APP_ROOT" ]]; then
    rsync -a \
      --exclude '.git/' \
      --exclude '.omx/' \
      --exclude 'backend/.venv/' \
      --exclude 'backend/media/' \
      --exclude 'frontend/.next/' \
      --exclude 'frontend/node_modules/' \
      --exclude 'backend/.env' \
      --exclude 'frontend/.env' \
      "$SOURCE_ROOT/" "$APP_ROOT/"
  fi

  mkdir -p "$APP_ROOT/backend/media/logos" "$APP_ROOT/backend/media/exports"
}

configure_postgres() {
  if [[ "$INSTALL_POSTGRES" != "true" ]]; then
    return
  fi

  if [[ -z "$DB_PASSWORD" ]]; then
    DB_PASSWORD="$(random_password)"
  fi

  log "Configuring local PostgreSQL database"
  $SUDO -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
  ELSE
    ALTER ROLE ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\\gexec
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL
}

configure_env() {
  log "Configuring environment files"
  local backend_env="$APP_ROOT/backend/.env"
  local frontend_env="$APP_ROOT/frontend/.env"
  local public_url
  local database_url
  local backend_force=false
  local frontend_force=false

  public_url="https://${DOMAIN}"
  if [[ "$ENABLE_TLS" != "true" ]]; then
    public_url="http://${DOMAIN}"
  fi

  if [[ "$INSTALL_POSTGRES" == "true" ]]; then
    database_url="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}"
  else
    database_url="postgresql+psycopg2://invoice:change-me@127.0.0.1:5432/invoice_db"
  fi

  if [[ ! -f "$backend_env" || ! -s "$backend_env" ]]; then
    : > "$backend_env"
    backend_force=true
  fi
  if [[ ! -f "$frontend_env" || ! -s "$frontend_env" ]]; then
    : > "$frontend_env"
    frontend_force=true
  fi

  set_env_value "$backend_env" APP_NAME "Invoice Generator API" "$backend_force"
  set_env_value "$backend_env" ENVIRONMENT production "$backend_force"
  set_env_value "$backend_env" DEBUG false "$backend_force"
  set_env_value "$backend_env" DATABASE_URL "$database_url" "$backend_force"
  set_env_value "$backend_env" BACKEND_BASE_URL "$public_url" "$backend_force"
  set_env_value "$backend_env" CORS_ORIGINS "[\"$public_url\"]" "$backend_force"
  set_env_value "$backend_env" MEDIA_ROOT "$APP_ROOT/backend/media" "$backend_force"
  set_env_value "$backend_env" LOGOS_DIR "$APP_ROOT/backend/media/logos" "$backend_force"
  set_env_value "$backend_env" EXPORTS_DIR "$APP_ROOT/backend/media/exports" "$backend_force"
  set_env_value "$backend_env" TELEGRAM_BOT_TOKEN "" "$backend_force"
  set_env_value "$backend_env" TELEGRAM_ALLOWED_USER_IDS "[]" "$backend_force"

  set_env_value "$frontend_env" NEXT_PUBLIC_API_URL "$public_url" "$frontend_force"

  chmod 600 "$backend_env" "$frontend_env"
}

install_app() {
  log "Installing backend dependencies"
  cd "$APP_ROOT/backend"
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip wheel
  pip install -r requirements.txt
  python -m playwright install-deps chromium
  PLAYWRIGHT_BROWSERS_PATH="$APP_ROOT/.ms-playwright" python -m playwright install chromium

  log "Running database migrations"
  alembic upgrade head

  log "Installing frontend dependencies and building"
  cd "$APP_ROOT/frontend"
  npm ci
  npm run build
}

write_systemd_units() {
  log "Writing systemd service units"
  $SUDO tee /etc/systemd/system/invoice-backend.service >/dev/null <<EOF
[Unit]
Description=Invoice FastAPI Backend
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_ROOT/backend
EnvironmentFile=$APP_ROOT/backend/.env
Environment=PLAYWRIGHT_BROWSERS_PATH=$APP_ROOT/.ms-playwright
ExecStart=$APP_ROOT/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port $BACKEND_PORT
Restart=always
RestartSec=5
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF

  $SUDO tee /etc/systemd/system/invoice-frontend.service >/dev/null <<EOF
[Unit]
Description=Invoice Next.js Frontend
After=network.target invoice-backend.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_ROOT/frontend
EnvironmentFile=$APP_ROOT/frontend/.env
Environment=NODE_ENV=production
ExecStart=/usr/bin/env npm run start -- -H 127.0.0.1 -p $FRONTEND_PORT
Restart=always
RestartSec=5
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF

  $SUDO tee /etc/systemd/system/invoice-telegram-bot.service >/dev/null <<EOF
[Unit]
Description=Invoice Telegram Bot
After=network.target invoice-backend.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_ROOT/backend
EnvironmentFile=$APP_ROOT/backend/.env
Environment=PLAYWRIGHT_BROWSERS_PATH=$APP_ROOT/.ms-playwright
ExecStart=$APP_ROOT/backend/.venv/bin/python -m app.bot.telegram_bot
Restart=always
RestartSec=5
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF
}

write_nginx_config() {
  log "Writing Nginx reverse proxy"
  $SUDO tee /etc/nginx/sites-available/invoice.conf >/dev/null <<EOF
upstream invoice_backend {
    server 127.0.0.1:$BACKEND_PORT;
    keepalive 32;
}

upstream invoice_frontend {
    server 127.0.0.1:$FRONTEND_PORT;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 10M;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location /media/ {
        alias $APP_ROOT/backend/media/;
        autoindex off;
        add_header Cache-Control "public, max-age=300";
    }

    location /api/ {
        proxy_pass http://invoice_backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 120s;
    }

    location /docs {
        proxy_pass http://invoice_backend/docs;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /openapi.json {
        proxy_pass http://invoice_backend/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://invoice_backend/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /_next/ {
        proxy_pass http://invoice_frontend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        proxy_pass http://invoice_frontend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

  $SUDO ln -sfn /etc/nginx/sites-available/invoice.conf /etc/nginx/sites-enabled/invoice.conf
  if [[ -e /etc/nginx/sites-enabled/default ]]; then
    $SUDO rm -f /etc/nginx/sites-enabled/default
  fi
  $SUDO nginx -t
}

set_permissions() {
  log "Setting runtime permissions"
  $SUDO chown -R "$CURRENT_USER":"$CURRENT_USER" "$APP_ROOT"
  if [[ -d "$APP_ROOT/.ms-playwright" ]]; then
    $SUDO chown -R "$APP_USER":"$APP_USER" "$APP_ROOT/.ms-playwright"
  fi
  $SUDO chown "$CURRENT_USER":"$APP_USER" "$APP_ROOT/backend/.env" "$APP_ROOT/frontend/.env"
  $SUDO chmod 640 "$APP_ROOT/backend/.env" "$APP_ROOT/frontend/.env"
  $SUDO chown -R "$APP_USER":"$APP_USER" "$APP_ROOT/backend/media"
  $SUDO chmod 755 "$APP_ROOT" "$APP_ROOT/backend" "$APP_ROOT/frontend"
}

restart_services() {
  log "Starting services"
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable invoice-backend invoice-frontend
  $SUDO systemctl restart invoice-backend invoice-frontend

  local bot_token
  bot_token="$(grep -E '^TELEGRAM_BOT_TOKEN=' "$APP_ROOT/backend/.env" | cut -d= -f2- || true)"
  if [[ "$RUN_TELEGRAM_BOT" == "true" || ( "$RUN_TELEGRAM_BOT" == "auto" && -n "$bot_token" ) ]]; then
    $SUDO systemctl enable invoice-telegram-bot
    $SUDO systemctl restart invoice-telegram-bot
  else
    $SUDO systemctl disable --now invoice-telegram-bot >/dev/null 2>&1 || true
  fi

  $SUDO systemctl enable nginx
  $SUDO systemctl reload nginx
}

configure_tls() {
  if [[ "$ENABLE_TLS" != "true" ]]; then
    return
  fi

  if [[ "$DOMAIN" == "invoice.example.com" ]]; then
    echo "ENABLE_TLS=true requires DOMAIN to be set to your real domain." >&2
    exit 1
  fi
  if is_ip_address "$DOMAIN"; then
    echo "Let's Encrypt cannot issue a normal certificate for a public IP. Use a DNS name or run with ENABLE_TLS=false." >&2
    exit 1
  fi
  if [[ -z "$EMAIL" ]]; then
    echo "ENABLE_TLS=true requires EMAIL for Let's Encrypt registration." >&2
    exit 1
  fi

  log "Requesting Let's Encrypt certificate"
  $SUDO certbot --nginx \
    --non-interactive \
    --agree-tos \
    --redirect \
    -m "$EMAIL" \
    -d "$DOMAIN"
}

health_check() {
  log "Checking local health endpoint"
  curl -fsS "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null
  echo "Deployment complete: http://$DOMAIN"
  if [[ "$ENABLE_TLS" == "true" ]]; then
    echo "TLS enabled: https://$DOMAIN"
  fi
}

main() {
  require_command apt-get
  require_command curl

  install_packages
  sync_source
  configure_postgres
  configure_env
  install_app
  write_systemd_units
  write_nginx_config
  set_permissions
  restart_services
  configure_tls
  health_check
}

main "$@"
