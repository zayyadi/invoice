#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-http://localhost:8000}"
OUT_DIR="${2:-/tmp/invoice-smoke}"
mkdir -p "$OUT_DIR"

payload_file="$OUT_DIR/payload.json"
cat > "$payload_file" << 'JSON'
{
  "invoice_number": "INV-SMOKE-00001",
  "customer_name": "Smoke Test Customer",
  "customer_email": "smoke@example.com",
  "issue_date": "2026-03-04",
  "due_date": "2026-03-11",
  "currency": "NGN",
  "notes": "Automated smoke test invoice",
  "tax_rate": 7.5,
  "items": [
    { "description": "Website design", "quantity": 1, "unit_price": 250000 },
    { "description": "Hosting", "quantity": 2, "unit_price": 35000 }
  ]
}
JSON

create_resp="$OUT_DIR/create.json"
curl -fsS -X POST "$API_URL/api/v1/invoices" \
  -H 'Content-Type: application/json' \
  --data-binary "@$payload_file" > "$create_resp"

invoice_id="$(python3 - << 'PY' "$create_resp"
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data['id'])
PY
)"

# Minimal 1x1 PNG
logo_file="$OUT_DIR/logo.png"
base64 -d > "$logo_file" << 'B64'
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7YJY4AAAAASUVORK5CYII=
B64

curl -fsS -X POST "$API_URL/api/v1/invoices/$invoice_id/logo" \
  -F "logo=@$logo_file;type=image/png" > "$OUT_DIR/logo_upload.json"

curl -fsS -X POST "$API_URL/api/v1/invoices/$invoice_id/export/pdf" > "$OUT_DIR/invoice.pdf"
curl -fsS -X POST "$API_URL/api/v1/invoices/$invoice_id/export/image?format=png" > "$OUT_DIR/invoice.png"
curl -fsS -X POST "$API_URL/api/v1/invoices/$invoice_id/export/image?format=jpg" > "$OUT_DIR/invoice.jpg"

printf 'Smoke test passed. Invoice ID: %s\nArtifacts: %s\n' "$invoice_id" "$OUT_DIR"
