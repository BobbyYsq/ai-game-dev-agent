from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes_health import router as health_router
from app.api.routes_projects import router as projects_router
from app.api.routes_settings import router as settings_router
from app.config import ensure_workspace_dirs


def create_app() -> FastAPI:
    ensure_workspace_dirs()
    app = FastAPI(title="AI Game Development Agent", version="0.2.0")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(health_router)
    app.include_router(settings_router)
    app.include_router(projects_router)
    templates = Jinja2Templates(directory="app/templates")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    return app


app = create_app()
