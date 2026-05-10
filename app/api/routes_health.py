from fastapi import APIRouter
from app.config import APP_VERSION

router = APIRouter()

@router.get('/api/health')
def health_check():
    return {'status':'ok','version':APP_VERSION,'runtime':'local'}
