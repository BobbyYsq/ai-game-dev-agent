#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "[bootstrap] Starting on macOS"
echo "First launch requires internet access to download runtime and dependencies."
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
