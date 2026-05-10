from typing import Protocol

from app.models.mock_provider import MockLLMProvider
from app.models.openai_provider import OpenAIProvider
from app.services.settings_service import load_private_settings


class LLMProvider(Protocol):
    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str: ...


def get_llm_provider() -> LLMProvider:
    settings = load_private_settings()
    if settings.get("llm_provider") == "openai":
        return OpenAIProvider(settings.get("openai_api_key", ""), settings.get("openai_model", "gpt-4.1-mini"))
    return MockLLMProvider()
