from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import secrets
import shutil
import subprocess
import threading
from typing import Any

from app.config import HASTUR_BROKER_DIR
from app.services.settings_service import load_private_settings, save_private_settings


_process: subprocess.Popen | None = None
_logs: deque[str] = deque(maxlen=400)
_lock = threading.Lock()


@dataclass
class BrokerConfig:
    host: str
    http_port: int
    tcp_port: int
    auth_token: str


def _command(name: str) -> str:
    resolved = shutil.which(name) or shutil.which(f"{name}.cmd")
    if not resolved:
        raise FileNotFoundError(f"{name} is not available on PATH.")
    return resolved


def _append_log(line: str) -> None:
    with _lock:
        _logs.append(line.rstrip())


def _read_output(process: subprocess.Popen) -> None:
    if process.stdout is None:
        return
    for line in process.stdout:
        _append_log(str(line).rstrip())


def _load_or_create_config(host: str | None = None, http_port: int | None = None, tcp_port: int | None = None) -> BrokerConfig:
    settings = load_private_settings()
    token = str(settings.get("hastur_auth_token") or secrets.token_hex(32))
    config = BrokerConfig(
        host=host or str(settings.get("hastur_broker_host", "localhost")),
        http_port=int(http_port or settings.get("hastur_broker_http_port", 5302)),
        tcp_port=int(tcp_port or settings.get("hastur_broker_tcp_port", 5301)),
        auth_token=token,
    )
    settings.update(
        {
            "hastur_enabled": True,
            "hastur_base_url": f"http://{config.host}:{config.http_port}",
            "hastur_auth_token": config.auth_token,
            "hastur_broker_host": config.host,
            "hastur_broker_http_port": config.http_port,
            "hastur_broker_tcp_port": config.tcp_port,
            "hastur_target_mode": "project_path",
        }
    )
    save_private_settings(settings)
    return config


def broker_status() -> dict[str, Any]:
    global _process
    running = _process is not None and _process.poll() is None
    settings = load_private_settings()
    return {
        "running": running,
        "pid": _process.pid if running and _process else None,
        "host": settings.get("hastur_broker_host", "localhost"),
        "http_port": int(settings.get("hastur_broker_http_port", 5302)),
        "tcp_port": int(settings.get("hastur_broker_tcp_port", 5301)),
        "base_url": settings.get("hastur_base_url", "http://localhost:5302"),
        "has_auth_token": bool(settings.get("hastur_auth_token")),
    }


def broker_logs() -> dict[str, Any]:
    with _lock:
        return {"logs": list(_logs)}


def start_broker(host: str | None = None, http_port: int | None = None, tcp_port: int | None = None) -> dict[str, Any]:
    global _process
    if _process is not None and _process.poll() is None:
        return {"success": True, "message": "Broker is already running.", "status": broker_status()}

    if not HASTUR_BROKER_DIR.exists():
        raise FileNotFoundError(f"Hastur broker directory not found: {HASTUR_BROKER_DIR}")

    config = _load_or_create_config(host, http_port, tcp_port)
    npm = _command("npm")
    npx = _command("npx")

    _append_log("Preparing Hastur broker-server.")
    if not (HASTUR_BROKER_DIR / "node_modules").exists():
        _append_log("Installing broker-server dependencies with npm install.")
        install = subprocess.run(
            [npm, "install"],
            cwd=HASTUR_BROKER_DIR,
            text=True,
            capture_output=True,
            timeout=180,
        )
        if install.stdout:
            for line in install.stdout.splitlines():
                _append_log(line)
        if install.stderr:
            for line in install.stderr.splitlines():
                _append_log(line)
        if install.returncode != 0:
            return {"success": False, "message": "npm install failed.", "status": broker_status(), "logs": broker_logs()["logs"]}

    command = [
        npx,
        "tsx",
        "src/index.ts",
        "--host",
        config.host,
        "--http-port",
        str(config.http_port),
        "--tcp-port",
        str(config.tcp_port),
        "--auth-token",
        config.auth_token,
    ]
    _append_log(f"Starting broker on {config.host}:{config.http_port} (HTTP), {config.host}:{config.tcp_port} (TCP).")
    _process = subprocess.Popen(
        command,
        cwd=HASTUR_BROKER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    threading.Thread(target=_read_output, args=(_process,), daemon=True).start()
    return {"success": True, "message": "Broker start requested.", "status": broker_status()}


def stop_broker() -> dict[str, Any]:
    global _process
    if _process is None or _process.poll() is not None:
        _process = None
        return {"success": True, "message": "Broker is not running.", "status": broker_status()}
    _append_log("Stopping Hastur broker-server.")
    _process.terminate()
    try:
        _process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _append_log("Broker did not exit after terminate; killing process.")
        _process.kill()
        _process.wait(timeout=5)
    _process = None
    return {"success": True, "message": "Broker stopped.", "status": broker_status()}
