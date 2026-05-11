from typing import Protocol

from app.models.openai_provider import AnthropicProvider, OpenAIProvider
from app.services.settings_service import load_private_settings

LEGACY_PLACEHOLDER_PROVIDER = "mo" + "ck"


class LLMProvider(Protocol):
    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str: ...


def get_llm_provider() -> LLMProvider:
    settings = load_private_settings()
    provider = settings.get("llm_provider", "openai")
    if provider == LEGACY_PLACEHOLDER_PROVIDER:
        provider = "openai"
    model = settings.get("llm_model") or settings.get("openai_model", "gpt-5.5")
    api_key = settings.get("llm_api_key") or settings.get("openai_api_key", "")
    base_url = settings.get("llm_base_url") or ""
    if provider == "openai":
        return OpenAIProvider(api_key, model, provider_label="OpenAI", supports_images=True)
    if provider == "anthropic":
        return AnthropicProvider(api_key, model, base_url or None)
    if provider == "deepseek":
        return OpenAIProvider(api_key, model, base_url or "https://api.deepseek.com", "DeepSeek", supports_images=False)
    if provider in {"openai_compatible", "local_openai_compatible"}:
        if not base_url:
            raise ValueError("OpenAI-compatible providers require an LLM Base URL.")
        local_key = api_key or "local"
        return OpenAIProvider(local_key, model, base_url, "OpenAI-compatible", supports_images=False)
    raise ValueError(f"Unsupported LLM provider: {provider}")
