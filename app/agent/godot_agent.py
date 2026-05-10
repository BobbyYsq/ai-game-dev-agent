from pathlib import Path
from app.tools.godot_project_tools import create_basic_scenes, create_basic_scripts, create_default_folders, create_godot_project_file

def generate_godot_project(project_dir: Path, project_name: str, game_type: str) -> list[Path]:
    create_default_folders(project_dir)
    out=[create_godot_project_file(project_dir, project_name)]
    out+=create_basic_scenes(project_dir)
    out+=create_basic_scripts(project_dir)
    return out
