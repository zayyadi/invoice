#!/usr/bin/env bash
set -euo pipefail

# Ubuntu/Debian bootstrap script for first-time setup.
# Run as a sudo-capable user.

sudo apt-get update
sudo apt-get install -y \
  nginx \
  python3 \
  python3-venv \
  python3-pip \
  nodejs \
  npm \
  postgresql-client \
  certbot \
  python3-certbot-nginx

# Optional: create deploy root owner/group
sudo mkdir -p /opt/invoice
sudo chown -R "$USER":"$USER" /opt/invoice

echo "Server bootstrap complete."
