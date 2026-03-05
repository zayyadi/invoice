#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR/frontend"

npm ci
NEXT_PUBLIC_API_URL="http://localhost:8000" npm run build

echo "Frontend CI checks passed."
