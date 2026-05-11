from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import GENERATED_PROJECTS_DIR
from app.services.git_service import commit_all, init_repo
from app.services.project_service import slugify
from app.services.settings_service import load_private_settings
from app.tools.godot_templates.base import (
    create_minimal_main_scene,
    create_minimal_project_godot,
    ensure_default_folders,
    install_hastur_addon,
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
    _write_godot_notes(project_dir, engine, host, port)
    files.append(project_dir / "docs" / "GODOT_PROJECT.md")
    if enable_git:
        init_repo(project_dir)
        commit_all(project_dir, "Initial Godot project")

    return GodotProjectResult(
        success=True,
        project_slug=slug,
        project_path=str(project_dir),
        generated_files=sorted({str(path.relative_to(project_dir)) for path in files if path.is_file()}),
        project_template=project_template,
        broker_host=host,
        broker_port=port,
    )


def _write_godot_notes(project_dir: Path, engine: str, broker_host: str, broker_port: int) -> None:
    notes = f"""# Godot Project

- Engine target: {engine}
- Main scene: `res://scenes/Main.tscn`
- Hastur addon: `res://addons/hasturoperationgd/plugin.cfg`
- Hastur broker TCP target: `{broker_host}:{broker_port}`

The Hastur editor plugin is enabled in `project.godot`. Start the broker from the AI Game Development Agent dashboard before opening or reloading the project in Godot.
"""
    notes_path = project_dir / "docs" / "GODOT_PROJECT.md"
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text(notes, encoding="utf-8")


def _generate_blank_hastur_project(project_dir: Path, project_name: str, broker_host: str, broker_port: int) -> list[Path]:
    ensure_default_folders(project_dir)
    files = [
        create_minimal_project_godot(project_dir, project_name, broker_host, broker_port),
        create_minimal_main_scene(project_dir),
    ]
    files.extend(install_hastur_addon(project_dir))
    return files
