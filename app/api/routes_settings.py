from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.llm_provider import get_llm_provider
from app.services.settings_service import get_public_settings, update_settings

router = APIRouter()

class SettingsUpdateRequest(BaseModel):
    llm_provider: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None
    image_provider: str | None = None
    openai_image_model: str | None = None
    image_api_key: str | None = None
    image_base_url: str | None = None
    image_size: str | None = None
    image_quality: str | None = None
    hastur_enabled: bool | None = None
    hastur_base_url: str | None = None
    hastur_auth_token: str | None = None
    hastur_target_mode: str | None = None
    hastur_broker_host: str | None = None
    hastur_broker_http_port: int | None = None
    hastur_broker_tcp_port: int | None = None

@router.get('/api/settings')
def get_settings():
    return get_public_settings()

@router.post('/api/settings')
def save_settings(payload: SettingsUpdateRequest):
    settings = update_settings(payload.model_dump())
    return {'success': True, 'message': 'Settings saved', 'settings': settings}

@router.post('/api/settings/test-llm')
def test_llm_connection():
    try:
        llm = get_llm_provider()
        _ = llm.generate_text('ping')
        return {'success': True, 'message': 'LLM connection test succeeded'}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"LLM connection failed: {exc}") from exc
