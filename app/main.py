from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes_assets import router as assets_router
from app.api.routes_hastur import router as hastur_router
from app.api.routes_health import router as health_router
from app.api.routes_git import router as git_router
from app.api.routes_godot_projects import router as godot_projects_router
from app.api.routes_projects import router as projects_router
from app.api.routes_settings import router as settings_router
from app.api.routes_skills import router as skills_router
from app.config import APP_VERSION, ensure_workspace_dirs


def create_app() -> FastAPI:
    ensure_workspace_dirs()
    app = FastAPI(title="AI Game Development Agent", version=APP_VERSION)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(health_router)
    app.include_router(settings_router)
    app.include_router(projects_router)
    app.include_router(godot_projects_router)
    app.include_router(assets_router)
    app.include_router(hastur_router)
    app.include_router(git_router)
    app.include_router(skills_router)
    templates = Jinja2Templates(directory="app/templates")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse(request, "index.html")

    return app


app = create_app()
