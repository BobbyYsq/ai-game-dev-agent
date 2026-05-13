import json
from typing import Any

from app.config import SETTINGS_FILE, ensure_workspace_dirs

LLM_PROVIDER_DEFAULT_MODELS = {
    "openai": "gpt-5.5",
    "anthropic": "claude-opus-4-1-20250805",
    "deepseek": "deepseek-chat",
    "openai_compatible": "gpt-5.5",
    "local_openai_compatible": "gpt-5.5",
}

IMAGE_PROVIDER_DEFAULT_MODELS = {
    "openai": "gpt-image-1.5",
    "openai_compatible": "gpt-image-1.5",
}

DEFAULT_SETTINGS = {
    "llm_provider": "openai",
    "llm_model": LLM_PROVIDER_DEFAULT_MODELS["openai"],
    "llm_api_key": "",
    "llm_base_url": "",
    "openai_model": LLM_PROVIDER_DEFAULT_MODELS["openai"],
    "openai_api_key": "",
    "image_provider": "openai",
    "openai_image_model": IMAGE_PROVIDER_DEFAULT_MODELS["openai"],
    "image_api_key": "",
    "image_base_url": "",
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

LEGACY_PLACEHOLDER_PROVIDER = "mo" + "ck"
LEGACY_IMAGE_MODELS = {"", "mock-image", "gpt-image-2"}

PRIVATE_SETTING_KEYS = {
    "llm_provider",
    "llm_model",
    "llm_api_key",
    "llm_base_url",
    "openai_model",
    "openai_api_key",
    "image_provider",
    "openai_image_model",
    "image_api_key",
    "image_base_url",
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
    _migrate_legacy_settings(merged)
    return merged


def save_private_settings(settings: dict[str, Any]) -> None:
    ensure_workspace_dirs()
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def get_public_settings() -> dict[str, Any]:
    s = load_private_settings()
    llm_provider = _public_provider(str(s.get("llm_provider", "openai")), "openai")
    image_provider = _public_provider(str(s.get("image_provider", "openai")), "openai")
    return {
        "llm_provider": llm_provider,
        "llm_model": s.get("llm_model") or s.get("openai_model") or LLM_PROVIDER_DEFAULT_MODELS.get(llm_provider, "gpt-5.5"),
        "llm_base_url": s.get("llm_base_url", ""),
        "openai_model": s.get("openai_model", LLM_PROVIDER_DEFAULT_MODELS["openai"]),
        "has_llm_api_key": bool(s.get("llm_api_key") or s.get("openai_api_key")),
        "has_openai_api_key": bool(s.get("openai_api_key") or s.get("llm_api_key")),
        "image_provider": image_provider,
        "openai_image_model": s.get("openai_image_model", IMAGE_PROVIDER_DEFAULT_MODELS["openai"]),
        "image_base_url": s.get("image_base_url", ""),
        "has_image_api_key": bool(s.get("image_api_key") or s.get("openai_api_key")),
        "image_size": s.get("image_size", "1024x1024"),
        "image_quality": s.get("image_quality", "medium"),
        "hastur_enabled": bool(s.get("hastur_enabled", False)),
        "hastur_base_url": s.get("hastur_base_url", "http://localhost:5302"),
        "has_hastur_auth_token": bool(s.get("hastur_auth_token")),
        "hastur_target_mode": s.get("hastur_target_mode", "project_path"),
        "hastur_broker_host": s.get("hastur_broker_host", "localhost"),
        "hastur_broker_http_port": int(s.get("hastur_broker_http_port", 5302)),
        "hastur_broker_tcp_port": int(s.get("hastur_broker_tcp_port", 5301)),
        "llm_defaults": LLM_PROVIDER_DEFAULT_MODELS,
        "image_defaults": IMAGE_PROVIDER_DEFAULT_MODELS,
        "supported_llm_providers": ["openai", "anthropic", "deepseek", "openai_compatible", "local_openai_compatible"],
        "supported_image_providers": ["openai", "openai_compatible"],
    }


def update_settings(update: dict[str, Any]) -> dict[str, Any]:
    current = load_private_settings()
    _infer_providers(update)
    for key in PRIVATE_SETTING_KEYS:
        if key in update and update[key] is not None:
            current[key] = update[key]
    _apply_default_models(current, update)
    _migrate_legacy_settings(current)
    save_private_settings(current)
    return get_public_settings()


def _migrate_legacy_settings(settings: dict[str, Any]) -> None:
    if not settings.get("llm_model") and settings.get("openai_model"):
        settings["llm_model"] = settings["openai_model"]
    if not settings.get("openai_model") and settings.get("llm_model"):
        settings["openai_model"] = settings["llm_model"]
    if not settings.get("llm_api_key") and settings.get("openai_api_key"):
        settings["llm_api_key"] = settings["openai_api_key"]
    if not settings.get("image_api_key") and settings.get("openai_api_key"):
        settings["image_api_key"] = settings["openai_api_key"]
    settings["llm_provider"] = _public_provider(str(settings.get("llm_provider", "openai")), "openai")
    settings["image_provider"] = _public_provider(str(settings.get("image_provider", "openai")), "openai")
    image_provider = str(settings.get("image_provider", "openai"))
    image_model = str(settings.get("openai_image_model", ""))
    if image_model in LEGACY_IMAGE_MODELS:
        settings["openai_image_model"] = IMAGE_PROVIDER_DEFAULT_MODELS.get(
            image_provider,
            IMAGE_PROVIDER_DEFAULT_MODELS["openai"],
        )


def _infer_providers(update: dict[str, Any]) -> None:
    llm_key = str(update.get("llm_api_key") or "")
    if llm_key and not update.get("llm_provider"):
        if llm_key.startswith("sk-ant"):
            update["llm_provider"] = "anthropic"
        else:
            update["llm_provider"] = "openai"
    image_key = str(update.get("image_api_key") or "")
    if image_key and not update.get("image_provider"):
        update["image_provider"] = "openai"


def _apply_default_models(settings: dict[str, Any], update: dict[str, Any]) -> None:
    provider = _public_provider(str(settings.get("llm_provider", "openai")), "openai")
    if ("llm_provider" in update or not settings.get("llm_model")) and not update.get("llm_model"):
        settings["llm_model"] = LLM_PROVIDER_DEFAULT_MODELS.get(provider, LLM_PROVIDER_DEFAULT_MODELS["openai"])
    if provider == "openai":
        settings["openai_model"] = settings.get("llm_model", LLM_PROVIDER_DEFAULT_MODELS["openai"])

    image_provider = _public_provider(str(settings.get("image_provider", "openai")), "openai")
    if ("image_provider" in update or not settings.get("openai_image_model")) and not update.get("openai_image_model"):
        settings["openai_image_model"] = IMAGE_PROVIDER_DEFAULT_MODELS.get(image_provider, IMAGE_PROVIDER_DEFAULT_MODELS["openai"])


def _public_provider(provider: str, fallback: str) -> str:
    if provider == LEGACY_PLACEHOLDER_PROVIDER:
        return fallback
    return provider
