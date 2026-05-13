#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[ai-game-dev-agent] %s\n' "$1"
}

fail() {
  printf '\n[ai-game-dev-agent] Startup failed: %s\n' "$1" >&2
  exit 1
}

find_free_port() {
  for port in 8000 8001 8002 8003; do
    if command -v lsof >/dev/null 2>&1; then
      if ! lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
        printf '%s\n' "$port"
        return 0
      fi
    elif command -v ss >/dev/null 2>&1; then
      if ! ss -ltn "sport = :$port" | grep -q ":$port"; then
        printf '%s\n' "$port"
        return 0
      fi
    else
      if python3 - "$port" <<'PY'
import socket
import sys

port = int(sys.argv[1])
with socket.socket() as sock:
    sys.exit(0 if sock.connect_ex(("127.0.0.1", port)) != 0 else 1)
PY
      then
        printf '%s\n' "$port"
        return 0
      fi
    fi
    log "Port $port is busy, trying next candidate."
  done
  return 1
}

install_micromamba() {
  if [ -x "$MAMBA" ]; then
    log "Portable micromamba already exists."
    return 0
  fi

  local arch platform archive
  arch="$(uname -m)"
  case "$arch" in
    aarch64|arm64) platform="linux-aarch64" ;;
    ppc64le) platform="linux-ppc64le" ;;
    *) platform="linux-64" ;;
  esac

  log "Downloading portable micromamba for $platform."
  archive="$MAMBA_DIR/micromamba.tar.bz2"
  curl -fsSL "https://micro.mamba.pm/api/micromamba/${platform}/latest" -o "$archive"

  log "Extracting micromamba."
  tar -xjf "$archive" -C "$MAMBA_DIR"
  if [ ! -x "$MAMBA_DIR/bin/micromamba" ]; then
    fail "Downloaded micromamba archive did not contain bin/micromamba."
  fi
  cp "$MAMBA_DIR/bin/micromamba" "$MAMBA"
  chmod +x "$MAMBA"
}

ensure_runtime_environment() {
  if [ -x "$ENV_DIR/bin/python" ]; then
    log "Runtime environment already exists."
    return 0
  fi

  if [ -d "$ENV_DIR" ]; then
    log "Found incomplete runtime environment. Removing it before retry."
    rm -rf "$ENV_DIR"
  fi

  log "Creating Python runtime with conda-forge only. This can take several minutes on first launch."
  "$MAMBA" create -y -p "$ENV_DIR" -c conda-forge --override-channels python=3.11 pip

  log "Installing Python packages from requirements.txt."
  "$MAMBA" run -p "$ENV_DIR" python -m pip install -r "$ROOT/requirements.txt"
}

open_dashboard() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
  elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser "$URL" >/dev/null 2>&1 || true
  fi
}

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$ROOT/runtime"
MAMBA_DIR="$RUNTIME_DIR/micromamba"
MAMBA="$MAMBA_DIR/micromamba"
ENV_DIR="$RUNTIME_DIR/envs/ai-game-dev-agent"

log "Project root: $ROOT"
mkdir -p "$MAMBA_DIR" "$(dirname "$ENV_DIR")"

install_micromamba
ensure_runtime_environment

PORT="$(find_free_port)" || fail "No free port available in 8000-8003."
URL="http://127.0.0.1:${PORT}"
log "Starting FastAPI on $URL"
open_dashboard

cd "$ROOT"
"$MAMBA" run -p "$ENV_DIR" python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" --app-dir "$ROOT"
