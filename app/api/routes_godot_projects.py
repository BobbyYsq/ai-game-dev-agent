from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.godot_project_service import create_godot_project

router = APIRouter()


class CreateGodotProjectRequest(BaseModel):
    project_name: str
    game_type: str = "2D top-down action"
    project_template: str = "2d"
    engine: str = "Godot 4"
    broker_host: str | None = None
    broker_port: int | None = None
    enable_git: bool = True


@router.post("/api/godot-projects/create")
def create_standalone_godot_project(payload: CreateGodotProjectRequest):
    if payload.project_template not in {"2d", "3d"}:
        raise HTTPException(status_code=422, detail="project_template must be 2d or 3d")
    if not payload.project_name.strip():
        raise HTTPException(status_code=422, detail="project_name is required")
    try:
        return create_godot_project(
            project_name=payload.project_name.strip(),
            game_type=payload.game_type,
            project_template=payload.project_template,
            engine=payload.engine,
            broker_host=payload.broker_host,
            broker_port=payload.broker_port,
            enable_git=payload.enable_git,
        ).__dict__
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
