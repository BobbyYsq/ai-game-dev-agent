from pathlib import Path
import shutil

from app.config import HASTUR_ADDON_DIR, HASTUR_LICENSE_FILE


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
    "addons",
    "licenses",
]


def ensure_default_folders(project_dir: Path) -> None:
    for folder in DEFAULT_FOLDERS:
        (project_dir / folder).mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def create_project_godot(project_dir: Path, project_name: str, broker_host: str = "localhost", broker_port: int = 5301) -> Path:
    return write_text(
        project_dir / "project.godot",
        f"""; Engine configuration file.
config_version=5

[application]
config/name="{project_name}"
run/main_scene="res://scenes/Main.tscn"

[hastur_operation]
broker_host="{broker_host}"
broker_port={int(broker_port)}

[editor_plugins]
enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")

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


def create_minimal_project_godot(project_dir: Path, project_name: str, broker_host: str = "localhost", broker_port: int = 5301) -> Path:
    return write_text(
        project_dir / "project.godot",
        f"""; Engine configuration file.
config_version=5

[application]
config/name="{project_name}"
run/main_scene="res://scenes/Main.tscn"

[hastur_operation]
broker_host="{broker_host}"
broker_port={int(broker_port)}

[editor_plugins]
enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")
""",
    )


def create_minimal_main_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/Main.tscn",
        """[gd_scene format=3]

[node name="Main" type="Node2D"]
""",
    )


def write_godot_project_notes(project_dir: Path, engine: str, broker_host: str, broker_port: int) -> Path:
    notes = f"""# Godot Project

- Engine target: {engine}
- Main scene: `res://scenes/Main.tscn`
- Hastur addon: `res://addons/hasturoperationgd/plugin.cfg`
- Hastur broker TCP target: `{broker_host}:{broker_port}`

The Hastur editor plugin is enabled in `project.godot`. Start the broker from the AI Game Development Agent dashboard before opening or reloading the project in Godot.
"""
    return write_text(project_dir / "docs" / "GODOT_PROJECT.md", notes)


def install_hastur_addon(project_dir: Path) -> list[Path]:
    if not HASTUR_ADDON_DIR.exists():
        raise FileNotFoundError(f"Hastur addon not found: {HASTUR_ADDON_DIR}")

    addon_target = project_dir / "addons" / "hasturoperationgd"
    addon_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HASTUR_ADDON_DIR, addon_target, dirs_exist_ok=True)

    license_target = project_dir / "licenses" / "HASTUR_OPERATION_PLUGIN_LICENSE.md"
    license_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HASTUR_LICENSE_FILE, license_target)

    notice = write_text(
        project_dir / "THIRD_PARTY_NOTICES.md",
        """# Third-Party Notices

## Hastur Operation Plugin

This Godot project includes the Hastur Operation Plugin addon under `addons/hasturoperationgd/`.

- Copyright: Copyright (c) 2026 Raiix
- License: MIT License
- Full license: `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`

The plugin is enabled in `project.godot` for editor-side automation through a local broker.
""",
    )

    return [
        path
        for path in [notice, license_target, *addon_target.rglob("*")]
        if path.is_file()
    ]


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
