from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import GENERATED_PROJECTS_DIR
from app.services.git_service import commit_all, ensure_godot_vcs_metadata, init_repo
from app.services.project_service import slugify
from app.services.settings_service import load_private_settings
from app.tools.godot_templates.base import (
    create_minimal_main_scene,
    create_minimal_project_godot,
    ensure_default_folders,
    install_hastur_addon,
    write_godot_project_notes,
)


@dataclass
class GodotProjectResult:
    success: bool
    project_slug: str
    project_path: str
    generated_files: list[str]
    project_template: str
    broker_host: str
    broker_port: int
    message: str = "Project created."
    git: dict | None = None


def create_godot_project(
    project_name: str,
    game_type: str = "blank",
    project_template: str = "2d",
    engine: str = "Godot 4.6",
    broker_host: str | None = None,
    broker_port: int | None = None,
    enable_git: bool = True,
) -> GodotProjectResult:
    settings = load_private_settings()
    host = broker_host or str(settings.get("hastur_broker_host", "localhost"))
    port = int(broker_port or settings.get("hastur_broker_tcp_port", 5301))

    slug = slugify(project_name)
    project_dir = GENERATED_PROJECTS_DIR / slug
    project_dir.mkdir(parents=True, exist_ok=True)
    files = _generate_blank_hastur_project(project_dir, project_name, host, port)
    ensure_godot_vcs_metadata(project_dir)
    files.extend([project_dir / ".gitignore", project_dir / ".gitattributes"])
    write_godot_project_notes(project_dir, engine, host, port)
    files.append(project_dir / "docs" / "GODOT_PROJECT.md")
    git_result = None
    if enable_git:
        init_repo(project_dir)
        git_result = commit_all(project_dir, "Initial Godot project")
    message = "Project created."
    if git_result and not git_result.get("committed"):
        message = "Project already exists/refreshed; local Git had no new changes to commit."

    return GodotProjectResult(
        success=True,
        project_slug=slug,
        project_path=str(project_dir),
        generated_files=sorted({str(path.relative_to(project_dir)) for path in files if path.is_file()}),
        project_template=project_template,
        broker_host=host,
        broker_port=port,
        message=message,
        git=git_result,
    )


def _generate_blank_hastur_project(project_dir: Path, project_name: str, broker_host: str, broker_port: int) -> list[Path]:
    ensure_default_folders(project_dir)
    files = [
        create_minimal_project_godot(project_dir, project_name, broker_host, broker_port),
        create_minimal_main_scene(project_dir),
    ]
    files.extend(install_hastur_addon(project_dir))
    return files
