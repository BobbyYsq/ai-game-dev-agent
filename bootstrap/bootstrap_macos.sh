#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; RUNTIME_DIR="$ROOT/runtime"; MAMBA_DIR="$RUNTIME_DIR/micromamba"; MAMBA="$MAMBA_DIR/micromamba"; ENV_DIR="$RUNTIME_DIR/envs/ai-game-dev-agent"
find_free_port(){ for p in 8000 8001 8002 8003; do lsof -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1 || { echo "$p"; return 0; }; done; return 1; }
mkdir -p "$MAMBA_DIR" "$(dirname "$ENV_DIR")"
if [ ! -x "$MAMBA" ]; then arch="$(uname -m)"; [ "$arch" = "arm64" ] && platform="osx-arm64" || platform="osx-64"; curl -fsSL "https://micro.mamba.pm/api/micromamba/${platform}/latest" -o "$MAMBA_DIR/micromamba.tar.bz2"; tar -xjf "$MAMBA_DIR/micromamba.tar.bz2" -C "$MAMBA_DIR"; cp "$MAMBA_DIR/bin/micromamba" "$MAMBA"; chmod +x "$MAMBA"; fi
[ -x "$ENV_DIR/bin/python" ] || "$MAMBA" create -y -p "$ENV_DIR" -f "$ROOT/environment.yml"
PORT="$(find_free_port)"; URL="http://127.0.0.1:${PORT}"; open "$URL"; cd "$ROOT"; "$MAMBA" run -p "$ENV_DIR" python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT"
