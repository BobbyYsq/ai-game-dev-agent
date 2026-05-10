from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import GENERATED_PROJECTS_DIR
from app.services.project_service import create_ai_game_project

router = APIRouter()


class CreateProjectRequest(BaseModel):
    project_name: str
    game_idea: str
    project_template: str = "2d"
    game_type: str = "2D top-down action"
    engine: str = "Godot 4"
    prototype_scope: str = "vertical slice"
    enable_git: bool = True
    generate_docs: bool = True
    generate_godot_skeleton: bool = True


@router.post('/api/projects/create')
def create_project(payload: CreateProjectRequest):
    if payload.project_template not in {"2d", "3d"}:
        raise HTTPException(status_code=422, detail="project_template must be 2d or 3d")
    result = create_ai_game_project(payload)
    return result.__dict__


@router.get('/api/projects')
def list_projects():
    projects = []
    if GENERATED_PROJECTS_DIR.exists():
        for p in sorted(GENERATED_PROJECTS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if p.is_dir():
                projects.append({'slug': p.name, 'path': str(p)})
    return {'projects': projects[:20]}


@router.get('/api/projects/{project_slug}')
def get_project(project_slug: str):
    p = GENERATED_PROJECTS_DIR / project_slug
    if not p.exists():
        raise HTTPException(status_code=404, detail='Project not found')
    files = [str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()]
    return {'slug': project_slug, 'path': str(p), 'files': files}
