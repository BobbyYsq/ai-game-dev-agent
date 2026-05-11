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

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is not configured.")
        self.client = OpenAI(api_key=api_key)

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
    if settings.get("image_provider") == "openai":
        return OpenAIImageProvider(settings.get("openai_api_key", ""))
    return MockImageProvider()
