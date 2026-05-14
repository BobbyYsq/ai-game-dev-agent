from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from app.config import GENERATED_PROJECTS_DIR
from app.models.image_provider import get_image_provider, validate_image_generation_settings
from app.services.settings_service import load_private_settings


IMAGE_PURPOSES = {
    "concept_art",
    "gdd_reference",
    "2d_sprite_draft",
    "ui_icon",
    "texture_reference",
    "blender_3d_reference",
}


@dataclass
class AssetRecord:
    id: str
    type: str
    purpose: str
    prompt: str
    provider: str
    model: str
    path: str
    created_at: str
    status: str = "generated"
    linked_to_gdd: bool = False
    use_as_blender_reference: bool = False


def get_project_dir(project_slug: str) -> Path:
    project_dir = GENERATED_PROJECTS_DIR / project_slug
    if not project_dir.exists() or not project_dir.is_dir():
        raise FileNotFoundError(f"Project not found: {project_slug}")
    return project_dir


def get_manifest_path(project_dir: Path) -> Path:
    return project_dir / "assets/generated/asset_manifest.json"


def load_asset_manifest(project_dir: Path) -> list[dict[str, Any]]:
    manifest_path = get_manifest_path(project_dir)
    if not manifest_path.exists():
        return []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return data.get("assets", [])


def save_asset_manifest(project_dir: Path, assets: list[dict[str, Any]]) -> None:
    manifest_path = get_manifest_path(project_dir)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({"assets": assets}, indent=2), encoding="utf-8")


def next_asset_id(assets: list[dict[str, Any]]) -> str:
    numbers = []
    for asset in assets:
        asset_id = str(asset.get("id", ""))
        if asset_id.startswith("img_"):
            try:
                numbers.append(int(asset_id.split("_", 1)[1]))
            except ValueError:
                continue
    return f"img_{(max(numbers) + 1) if numbers else 1:03d}"


def list_assets(project_slug: str) -> dict[str, Any]:
    project_dir = get_project_dir(project_slug)
    return {"project_slug": project_slug, "assets": load_asset_manifest(project_dir)}


def generate_image_asset(
    project_slug: str,
    prompt: str,
    purpose: str,
    model: str | None = None,
    size: str = "1024x1024",
    quality: str = "medium",
) -> AssetRecord:
    if purpose not in IMAGE_PURPOSES:
        raise ValueError(f"Unsupported image purpose: {purpose}")
    project_dir = get_project_dir(project_slug)
    settings = load_private_settings()
    validate_image_generation_settings(size=size, quality=quality)
    image_model = model or settings.get("openai_image_model", "gpt-image-1.5")
    provider = get_image_provider()
    generated = provider.generate_image(prompt=prompt, model=image_model, size=size, quality=quality)

    assets = load_asset_manifest(project_dir)
    asset_id = next_asset_id(assets)
    relative_path = Path("assets/generated/cache/images") / f"{asset_id}.{generated.extension}"
    output_path = project_dir / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(generated.content)

    record = AssetRecord(
        id=asset_id,
        type="image",
        purpose=purpose,
        prompt=prompt,
        provider=generated.provider,
        model=generated.model,
        path=relative_path.as_posix(),
        created_at=datetime.now(timezone.utc).isoformat(),
        use_as_blender_reference=purpose == "blender_3d_reference",
    )
    assets.append(asdict(record))
    save_asset_manifest(project_dir, assets)
    if record.use_as_blender_reference:
        write_blender_reference_notes(project_dir, assets)
    return record


def find_asset(assets: list[dict[str, Any]], asset_id: str) -> dict[str, Any]:
    for asset in assets:
        if asset.get("id") == asset_id:
            return asset
    raise FileNotFoundError(f"Asset not found: {asset_id}")


def attach_asset_to_gdd(project_slug: str, asset_id: str) -> dict[str, Any]:
    project_dir = get_project_dir(project_slug)
    assets = load_asset_manifest(project_dir)
    asset = find_asset(assets, asset_id)
    gdd_path = project_dir / "docs/GDD.md"
    gdd_path.parent.mkdir(parents=True, exist_ok=True)
    current = gdd_path.read_text(encoding="utf-8") if gdd_path.exists() else f"# {project_slug} GDD\n"
    if "## Generated Visual References" not in current:
        current = current.rstrip() + "\n\n## Generated Visual References\n"
    title = asset.get("purpose", "Generated Image").replace("_", " ").title()
    image_line = f"\n![{title}](../{asset['path']})\n"
    if image_line.strip() not in current:
        current = current.rstrip() + image_line
    gdd_path.write_text(current + "\n", encoding="utf-8")
    asset["linked_to_gdd"] = True
    save_asset_manifest(project_dir, assets)
    return asset


def mark_blender_reference(project_slug: str, asset_id: str) -> dict[str, Any]:
    project_dir = get_project_dir(project_slug)
    assets = load_asset_manifest(project_dir)
    asset = find_asset(assets, asset_id)
    asset["use_as_blender_reference"] = True
    save_asset_manifest(project_dir, assets)
    write_blender_reference_notes(project_dir, assets)
    return asset


def write_blender_reference_notes(project_dir: Path, assets: list[dict[str, Any]]) -> Path:
    refs = [asset for asset in assets if asset.get("use_as_blender_reference")]
    notes_path = project_dir / "docs/BLENDER_REFERENCE_NOTES.md"
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Blender Reference Notes", ""]
    if not refs:
        lines.append("No Blender reference images have been selected yet.")
    for asset in refs:
        lines.extend(
            [
                f"## {asset['id']} - {asset.get('purpose', 'image')}",
                "",
                f"- Path: `{asset['path']}`",
                f"- Model: `{asset.get('model', '')}`",
                f"- Prompt: {asset.get('prompt', '')}",
                "",
            ]
        )
    notes_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return notes_path
