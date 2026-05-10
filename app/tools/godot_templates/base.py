from pathlib import Path


DEFAULT_FOLDERS = [
    "scenes",
    "scripts",
    "docs",
    "assets/art/concepts",
    "assets/art/sprites",
    "assets/art/ui",
    "assets/art/icons",
    "assets/audio/bgm",
    "assets/audio/sfx",
    "assets/models",
    "assets/generated/cache/images",
    "assets/generated/cache/audio",
    "assets/generated/cache/models",
]


def ensure_default_folders(project_dir: Path) -> None:
    for folder in DEFAULT_FOLDERS:
        (project_dir / folder).mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def create_project_godot(project_dir: Path, project_name: str) -> Path:
    return write_text(
        project_dir / "project.godot",
        f"""; Engine configuration file.
config_version=5

[application]
config/name="{project_name}"
run/main_scene="res://scenes/Main.tscn"

[input]
move_left={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":65)]}}
move_right={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":68)]}}
move_up={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":87)]}}
move_down={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":83)]}}
jump={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":32)]}}
attack={{"deadzone":0.2,"events":[Object(InputEventMouseButton,"resource_local_to_scene":false,"button_index":1)]}}
interact={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":69)]}}
pause={{"deadzone":0.2,"events":[Object(InputEventKey,"resource_local_to_scene":false,"physical_keycode":27)]}}
""",
    )


def create_shared_scripts(project_dir: Path) -> list[Path]:
    return [
        write_text(
            project_dir / "scripts/GameManager.gd",
            """extends Node

var score := 0

func add_score(amount: int) -> void:
    score += amount
""",
        ),
        write_text(
            project_dir / "scripts/UIController.gd",
            """extends CanvasLayer

@onready var status_label: Label = $Control/Panel/StatusLabel

func _ready() -> void:
    set_status_text("Prototype ready")

func set_status_text(text: String) -> void:
    if status_label:
        status_label.text = text
""",
        ),
    ]
