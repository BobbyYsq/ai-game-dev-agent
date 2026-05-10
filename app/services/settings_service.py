import json
from typing import Any

from app.config import SETTINGS_FILE, ensure_workspace_dirs

DEFAULT_SETTINGS = {
    "llm_provider": "mock",
    "openai_model": "gpt-4.1-mini",
    "openai_api_key": "",
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
    }


def update_settings(update: dict[str, Any]) -> dict[str, Any]:
    current = load_private_settings()
    for key in ["llm_provider", "openai_model", "openai_api_key"]:
        if key in update and update[key] is not None:
            current[key] = update[key]
    save_private_settings(current)
    return get_public_settings()
