from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.hastur_skill_service import (
    delete_skill,
    get_skill_metadata,
    list_hastur_skills,
    upload_skill,
)

router = APIRouter()


class SkillUploadFile(BaseModel):
    filename: str
    data: str
    relative_path: str = ""
    media_type: str = ""


class SkillUploadRequest(BaseModel):
    scope: str = "global"
    project_slug: str = ""
    files: list[SkillUploadFile]


@router.get("/api/skills")
def get_skills(project_slug: str = ""):
    return {"skills": [skill.__dict__ for skill in list_hastur_skills(project_slug or None)]}


@router.get("/api/skills/{scope}/{name}/metadata")
def get_skill(scope: str, name: str, project_slug: str = Query(default="")):
    try:
        return {"skill": get_skill_metadata(name, project_slug=project_slug or None, scope=scope).__dict__}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/skills/upload")
def upload_skill_route(payload: SkillUploadRequest):
    try:
        return upload_skill(
            scope=payload.scope,
            project_slug=payload.project_slug or None,
            files=[item.model_dump() for item in payload.files],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/api/skills/{scope}/{name}")
def delete_skill_route(scope: str, name: str, project_slug: str = Query(default="")):
    try:
        return delete_skill(scope, name, project_slug=project_slug or None)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
