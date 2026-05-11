from dataclasses import dataclass
import base64

import httpx
from openai import OpenAI

from app.services.settings_service import load_private_settings


@dataclass
class GeneratedImage:
    content: bytes
    extension: str = "png"
    provider: str = "mock"
    model: str = "mock-image"


MOCK_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAARklEQVR4nO3PQQ0A"
    "IBDAMMC/5+ONAvZoFSzZnNnV3QPg1wEJSAASkIAEJCAByf8CJJ83BgAAAAAA"
    "AAAAAADg6wRIQALyJwIb6wTz4AAAAABJRU5ErkJggg=="
)


class MockImageProvider:
    provider_name = "mock"

    def generate_image(self, prompt: str, model: str, size: str, quality: str) -> GeneratedImage:
        return GeneratedImage(
            content=base64.b64decode(MOCK_PNG_BASE64),
            provider=self.provider_name,
            model="mock-image",
        )


class OpenAIImageProvider:
    provider_name = "openai"

    def __init__(self, api_key: str, base_url: str | None = None, provider_name: str = "openai"):
        if not api_key:
            raise ValueError("Image API key is not configured.")
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.provider_name = provider_name

    def generate_image(self, prompt: str, model: str, size: str, quality: str) -> GeneratedImage:
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        item = response.data[0]
        b64_json = getattr(item, "b64_json", None)
        if b64_json:
            content = base64.b64decode(b64_json)
        else:
            image_url = getattr(item, "url", None)
            if not image_url:
                raise ValueError("Image response did not include base64 image data or a download URL.")
            with httpx.Client(timeout=60.0) as client:
                download = client.get(image_url)
                download.raise_for_status()
                content = download.content
        return GeneratedImage(
            content=content,
            provider=self.provider_name,
            model=model,
        )


def get_image_provider():
    settings = load_private_settings()
    provider = settings.get("image_provider", "mock")
    api_key = settings.get("image_api_key") or settings.get("openai_api_key", "")
    base_url = settings.get("image_base_url") or ""
    if provider == "openai":
        return OpenAIImageProvider(api_key)
    if provider == "openai_compatible":
        return OpenAIImageProvider(api_key, base_url or None, provider)
    return MockImageProvider()
