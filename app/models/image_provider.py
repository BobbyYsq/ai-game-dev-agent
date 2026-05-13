from dataclasses import dataclass
import base64

import httpx
from openai import APIError, OpenAI

from app.services.settings_service import load_private_settings

LEGACY_PLACEHOLDER_PROVIDER = "mo" + "ck"
SUPPORTED_IMAGE_SIZES = {"1024x1024", "1024x1536", "1536x1024", "auto"}
SUPPORTED_IMAGE_QUALITIES = {"low", "medium", "high", "auto"}


@dataclass
class GeneratedImage:
    content: bytes
    extension: str = "png"
    provider: str = "openai"
    model: str = "gpt-image-1"


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
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )
        except APIError as exc:
            raise ValueError(_openai_error_message(exc)) from exc
        item = response.data[0]
        b64_json = getattr(item, "b64_json", None)
        if b64_json:
            content = base64.b64decode(b64_json)
        else:
            image_url = getattr(item, "url", None)
            if not image_url:
                raise ValueError("Image response did not include base64 image data or a download URL.")
            with httpx.Client(timeout=60.0) as client:
                try:
                    download = client.get(image_url)
                    download.raise_for_status()
                except httpx.HTTPError as exc:
                    raise ValueError(f"Image download failed: {exc}") from exc
                content = download.content
        return GeneratedImage(
            content=content,
            provider=self.provider_name,
            model=model,
        )


def get_image_provider():
    settings = load_private_settings()
    provider = settings.get("image_provider", "openai")
    if provider == LEGACY_PLACEHOLDER_PROVIDER:
        provider = "openai"
    api_key = settings.get("image_api_key") or settings.get("openai_api_key", "")
    base_url = settings.get("image_base_url") or ""
    if provider == "openai":
        return OpenAIImageProvider(api_key)
    if provider == "openai_compatible":
        return OpenAIImageProvider(api_key, base_url or None, provider)
    raise ValueError(f"Unsupported image provider: {provider}")


def validate_image_generation_settings(size: str = "1024x1024", quality: str = "medium") -> dict:
    settings = load_private_settings()
    provider = settings.get("image_provider", "openai")
    if provider == LEGACY_PLACEHOLDER_PROVIDER:
        provider = "openai"
    api_key = settings.get("image_api_key") or settings.get("openai_api_key", "")
    if not api_key:
        raise ValueError("Image API key is not configured. Save an image API key in API Settings first.")
    if provider not in {"openai", "openai_compatible"}:
        raise ValueError(f"Unsupported image provider: {provider}")
    if size not in SUPPORTED_IMAGE_SIZES:
        raise ValueError(f"Unsupported image size: {size}. Choose one of {sorted(SUPPORTED_IMAGE_SIZES)}.")
    if quality not in SUPPORTED_IMAGE_QUALITIES:
        raise ValueError(f"Unsupported image quality: {quality}. Choose one of {sorted(SUPPORTED_IMAGE_QUALITIES)}.")
    model = settings.get("openai_image_model", "gpt-image-1.5")
    return {
        "success": True,
        "provider": provider,
        "model": model,
        "size": size,
        "quality": quality,
        "message": "Image configuration is ready.",
    }


def _openai_error_message(exc: APIError) -> str:
    status = getattr(exc, "status_code", None)
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict) and error.get("message"):
            return f"OpenAI image API error{f' ({status})' if status else ''}: {error['message']}"
        if body.get("message"):
            return f"OpenAI image API error{f' ({status})' if status else ''}: {body['message']}"
    message = str(exc).strip()
    return f"OpenAI image API error{f' ({status})' if status else ''}: {message}"
