from pathlib import Path
from app.tools.godot_project_tools import generate_godot_template_project


def generate_godot_project(project_dir: Path, project_name: str, game_type: str, project_template: str = "2d") -> list[Path]:
    return generate_godot_template_project(project_dir, project_name, game_type, project_template)
