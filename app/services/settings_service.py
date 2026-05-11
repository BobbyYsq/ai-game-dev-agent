import json
from typing import Any

from app.config import SETTINGS_FILE, ensure_workspace_dirs

DEFAULT_SETTINGS = {
    "llm_provider": "mock",
    "openai_model": "gpt-4.1-mini",
    "openai_api_key": "",
    "image_provider": "mock",
    "openai_image_model": "gpt-image-2",
    "image_size": "1024x1024",
    "image_quality": "medium",
    "hastur_enabled": False,
    "hastur_base_url": "http://localhost:5302",
    "hastur_auth_token": "",
    "hastur_target_mode": "project_path",
    "hastur_broker_host": "localhost",
    "hastur_broker_http_port": 5302,
    "hastur_broker_tcp_port": 5301,
}

PRIVATE_SETTING_KEYS = {
    "llm_provider",
    "openai_model",
    "openai_api_key",
    "image_provider",
    "openai_image_model",
    "image_size",
    "image_quality",
    "hastur_enabled",
    "hastur_base_url",
    "hastur_auth_token",
    "hastur_target_mode",
    "hastur_broker_host",
    "hastur_broker_http_port",
    "hastur_broker_tcp_port",
}


def load_private_settings() -> dict[str, Any]:
    ensure_workspace_dirs()
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_private_settings(settings: dict[str, Any]) -> None:
    ensure_workspace_dirs()
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def get_public_settings() -> dict[str, Any]:
    s = load_private_settings()
    return {
        "llm_provider": s.get("llm_provider", "mock"),
        "openai_model": s.get("openai_model", "gpt-4.1-mini"),
        "has_openai_api_key": bool(s.get("openai_api_key")),
        "image_provider": s.get("image_provider", "mock"),
        "openai_image_model": s.get("openai_image_model", "gpt-image-2"),
        "image_size": s.get("image_size", "1024x1024"),
        "image_quality": s.get("image_quality", "medium"),
        "hastur_enabled": bool(s.get("hastur_enabled", False)),
        "hastur_base_url": s.get("hastur_base_url", "http://localhost:5302"),
        "has_hastur_auth_token": bool(s.get("hastur_auth_token")),
        "hastur_target_mode": s.get("hastur_target_mode", "project_path"),
        "hastur_broker_host": s.get("hastur_broker_host", "localhost"),
        "hastur_broker_http_port": int(s.get("hastur_broker_http_port", 5302)),
        "hastur_broker_tcp_port": int(s.get("hastur_broker_tcp_port", 5301)),
    }


def update_settings(update: dict[str, Any]) -> dict[str, Any]:
    current = load_private_settings()
    for key in PRIVATE_SETTING_KEYS:
        if key in update and update[key] is not None:
            current[key] = update[key]
    save_private_settings(current)
    return get_public_settings()
