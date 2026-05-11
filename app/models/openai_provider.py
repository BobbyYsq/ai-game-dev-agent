import httpx
from openai import OpenAI


class OpenAIProvider:
    def __init__(self, api_key: str, model: str, base_url: str | None = None, provider_label: str = "OpenAI"):
        if not api_key:
            raise ValueError(f"{provider_label} API key is not configured.")
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content or ""


class AnthropicProvider:
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        if not api_key:
            raise ValueError("Anthropic API key is not configured.")
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or "https://api.anthropic.com").rstrip("/")

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{self.base_url}/v1/messages", json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        chunks = data.get("content", [])
        return "".join(chunk.get("text", "") for chunk in chunks if chunk.get("type") == "text")
