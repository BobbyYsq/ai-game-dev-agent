from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.asset_service import (
    IMAGE_PURPOSES,
    attach_asset_to_gdd,
    find_asset,
    generate_image_asset,
    get_project_dir,
    load_asset_manifest,
    list_assets,
    mark_blender_reference,
)

router = APIRouter()


class GenerateImageRequest(BaseModel):
    prompt: str
    purpose: str = "concept_art"
    model: str | None = None
    size: str = "1024x1024"
    quality: str = "medium"


@router.get("/api/projects/{project_slug}/assets")
def get_project_assets(project_slug: str):
    try:
        return list_assets(project_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/assets/images/generate")
def generate_project_image(project_slug: str, payload: GenerateImageRequest):
    if payload.purpose not in IMAGE_PURPOSES:
        raise HTTPException(status_code=422, detail=f"purpose must be one of {sorted(IMAGE_PURPOSES)}")
    if not payload.prompt.strip():
        raise HTTPException(status_code=422, detail="prompt is required")
    try:
        asset = generate_image_asset(
            project_slug=project_slug,
            prompt=payload.prompt.strip(),
            purpose=payload.purpose,
            model=payload.model,
            size=payload.size,
            quality=payload.quality,
        )
        return {"success": True, "asset": asset.__dict__}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Image generation failed: {exc}") from exc


@router.get("/api/projects/{project_slug}/assets/{asset_id}/file")
def get_project_asset_file(project_slug: str, asset_id: str):
    try:
        project_dir = get_project_dir(project_slug)
        asset = find_asset(load_asset_manifest(project_dir), asset_id)
        path = project_dir / asset["path"]
        if not path.exists():
            raise FileNotFoundError(f"Asset file not found: {asset_id}")
        return FileResponse(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd")
def attach_project_asset_to_gdd(project_slug: str, asset_id: str):
    try:
        return {"success": True, "asset": attach_asset_to_gdd(project_slug, asset_id)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference")
def mark_project_asset_blender_reference(project_slug: str, asset_id: str):
    try:
        return {"success": True, "asset": mark_blender_reference(project_slug, asset_id)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
