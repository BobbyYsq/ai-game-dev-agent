from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import secrets
import shutil
import subprocess
import threading
import re
from typing import Any

import httpx

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
    _capture_auth_token(line)


def _capture_auth_token(line: str) -> None:
    match = re.search(r"(?:Auto-generated auth token|auth token):\s*([A-Za-z0-9._-]{16,})", line, re.IGNORECASE)
    if not match:
        return
    settings = load_private_settings()
    settings.update(
        {
            "hastur_enabled": True,
            "hastur_auth_token": match.group(1),
            "hastur_target_mode": "project_path",
        }
    )
    save_private_settings(settings)


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
    managed_running = _process is not None and _process.poll() is None
    settings = load_private_settings()
    host = settings.get("hastur_broker_host", "localhost")
    http_port = int(settings.get("hastur_broker_http_port", 5302))
    tcp_port = int(settings.get("hastur_broker_tcp_port", 5301))
    base_url = str(settings.get("hastur_base_url", f"http://{host}:{http_port}")).rstrip("/")
    token = str(settings.get("hastur_auth_token") or "")
    probe = _probe_broker(base_url, token)
    running = managed_running or probe["http_available"]
    return {
        "running": running,
        "managed_running": managed_running,
        "external_running": probe["http_available"] and not managed_running,
        "can_stop": managed_running,
        "pid": _process.pid if managed_running and _process else None,
        "host": host,
        "http_port": http_port,
        "tcp_port": tcp_port,
        "base_url": base_url,
        "has_auth_token": bool(token),
        "token_state": probe["token_state"],
        "http_available": probe["http_available"],
        "health": probe["health"],
        "executors_available": probe["executors_available"],
        "executor_count": len(probe["executors"]),
        "executors": probe["executors"],
        "message": _broker_status_message(managed_running, probe),
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
    existing = _probe_broker(f"http://{config.host}:{config.http_port}", config.auth_token)
    if existing["http_available"]:
        _append_log(f"Broker is already reachable at {config.host}:{config.http_port}.")
        return {"success": True, "message": "Broker is already running outside this dashboard.", "status": broker_status()}
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
        current = broker_status()
        if current.get("external_running"):
            return {
                "success": False,
                "message": "Broker is running outside this dashboard. Stop it from the process that started it.",
                "status": current,
            }
        return {"success": True, "message": "Broker is not running.", "status": current}
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


def _probe_broker(base_url: str, token: str) -> dict[str, Any]:
    probe: dict[str, Any] = {
        "http_available": False,
        "health": None,
        "executors_available": False,
        "executors": [],
        "token_state": "missing" if not token else "unknown",
        "error": "",
    }
    try:
        with httpx.Client(timeout=1.5) as client:
            health = client.get(f"{base_url}/api/health")
            health.raise_for_status()
            probe["http_available"] = True
            probe["health"] = health.json()
            if not token:
                return probe
            executors = client.get(f"{base_url}/api/executors", headers={"Authorization": f"Bearer {token}"})
            if executors.status_code in {401, 403}:
                probe["token_state"] = "invalid"
                return probe
            executors.raise_for_status()
            payload = executors.json()
            data = payload.get("data") if isinstance(payload, dict) else payload
            probe["executors"] = data if isinstance(data, list) else []
            probe["executors_available"] = True
            probe["token_state"] = "ready"
    except (httpx.HTTPError, ValueError) as exc:
        probe["error"] = str(exc)
    return probe


def _broker_status_message(managed_running: bool, probe: dict[str, Any]) -> str:
    if managed_running:
        return "Dashboard-managed broker is running."
    if probe.get("http_available"):
        return "Broker is running outside this dashboard."
    return "Broker is stopped or unreachable."
