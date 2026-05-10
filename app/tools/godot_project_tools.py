from pathlib import Path

from app.tools.godot_templates.template_2d import generate_2d_playable_template
from app.tools.godot_templates.template_3d import generate_3d_playable_template


def generate_godot_template_project(
    project_dir: Path,
    project_name: str,
    game_type: str,
    project_template: str = "2d",
) -> list[Path]:
    if project_template == "2d":
        return generate_2d_playable_template(project_dir, project_name, game_type)
    if project_template == "3d":
        return generate_3d_playable_template(project_dir, project_name, game_type)
    raise ValueError(f"Unknown Godot project template: {project_template}")
