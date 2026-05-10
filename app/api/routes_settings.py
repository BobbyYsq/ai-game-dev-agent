from fastapi import APIRouter
from pydantic import BaseModel

from app.models.llm_provider import get_llm_provider
from app.services.settings_service import get_public_settings, update_settings

router = APIRouter()

class SettingsUpdateRequest(BaseModel):
    llm_provider: str = 'mock'
    openai_api_key: str | None = None
    openai_model: str = 'gpt-4.1-mini'

@router.get('/api/settings')
def get_settings():
    return get_public_settings()

@router.post('/api/settings')
def save_settings(payload: SettingsUpdateRequest):
    settings = update_settings(payload.model_dump())
    return {'success': True, 'message': 'Settings saved', 'settings': settings}

@router.post('/api/settings/test-llm')
def test_llm_connection():
    llm = get_llm_provider()
    _ = llm.generate_text('ping')
    return {'success': True, 'message': 'LLM connection test succeeded'}
