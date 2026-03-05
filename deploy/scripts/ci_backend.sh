#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR/backend"

python3 -m venv .venv-ci
source .venv-ci/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m py_compile $(find app -name '*.py' -type f)

deactivate
rm -rf .venv-ci

echo "Backend CI checks passed."
