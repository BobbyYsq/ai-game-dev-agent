from pathlib import Path


def create_godot_project_file(project_dir: Path, project_name: str) -> Path:
    p = project_dir / "project.godot"
    p.write_text(
        f"""; Engine configuration file.
config_version=5

[application]
config/name=\"{project_name}\"
run/main_scene=\"res://scenes/Main.tscn\"

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
        encoding="utf-8",
    )
    return p


def create_default_folders(project_dir: Path) -> None:
    for d in ["scenes", "scripts", "docs", "assets/art", "assets/audio", "assets/models", "assets/generated/cache/images", "assets/generated/cache/audio", "assets/generated/cache/models"]:
        (project_dir / d).mkdir(parents=True, exist_ok=True)


def _write(p: Path, c: str) -> Path:
    p.write_text(c, encoding="utf-8")
    return p


def generate_godot_template_project(project_dir: Path, project_name: str, game_type: str, project_template: str = "2d") -> list[Path]:
    create_default_folders(project_dir)
    files = [create_godot_project_file(project_dir, project_name)]
    if project_template == "2d":
        files += [
            _write(project_dir / "scenes/Main.tscn", "[gd_scene format=3]\n[node name=\"Main\" type=\"Node2D\"]\n"),
            _write(project_dir / "scenes/Player.tscn", "[gd_scene format=3]\n[node name=\"Player\" type=\"CharacterBody2D\"]\n"),
            _write(project_dir / "scenes/Enemy.tscn", "[gd_scene format=3]\n[node name=\"Enemy\" type=\"CharacterBody2D\"]\n"),
            _write(project_dir / "scenes/UI.tscn", "[gd_scene format=3]\n[node name=\"UI\" type=\"CanvasLayer\"]\n[node name=\"Control\" type=\"Control\" parent=\".\"]\n[node name=\"Label\" type=\"Label\" parent=\"Control\"]\n"),
            _write(project_dir / "scenes/TestLevel2D.tscn", "[gd_scene format=3]\n[node name=\"TestLevel2D\" type=\"Node2D\"]\n"),
            _write(project_dir / "scripts/Player2D.gd", "extends CharacterBody2D\n@export var speed := 220.0\nfunc _physics_process(delta):\n\tvar direction := Input.get_vector(\"move_left\",\"move_right\",\"move_up\",\"move_down\")\n\tvelocity = direction * speed\n\tmove_and_slide()\n"),
            _write(project_dir / "scripts/Enemy2D.gd", "extends CharacterBody2D\n@export var speed := 120.0\nvar dir := 1.0\nfunc _physics_process(delta):\n\tvelocity.x = speed * dir\n\tif abs(position.x) > 150:\n\t\tdir *= -1.0\n\tmove_and_slide()\n"),
        ]
    elif project_template == "3d":
        files += [
            _write(project_dir / "scenes/Main.tscn", "[gd_scene format=3]\n[node name=\"Main\" type=\"Node3D\"]\n[node name=\"DirectionalLight3D\" type=\"DirectionalLight3D\" parent=\".\"]\n"),
            _write(project_dir / "scenes/Player.tscn", "[gd_scene format=3]\n[node name=\"Player\" type=\"CharacterBody3D\"]\n"),
            _write(project_dir / "scenes/Enemy.tscn", "[gd_scene format=3]\n[node name=\"Enemy\" type=\"CharacterBody3D\"]\n"),
            _write(project_dir / "scenes/UI.tscn", "[gd_scene format=3]\n[node name=\"UI\" type=\"CanvasLayer\"]\n"),
            _write(project_dir / "scenes/TestLevel3D.tscn", "[gd_scene format=3]\n[node name=\"TestLevel3D\" type=\"Node3D\"]\n"),
            _write(project_dir / "scripts/Player3D.gd", "extends CharacterBody3D\n@export var speed := 5.0\nfunc _physics_process(delta):\n\tvar input_dir = Vector2.ZERO\n\tinput_dir.x = Input.get_action_strength(\"move_right\") - Input.get_action_strength(\"move_left\")\n\tinput_dir.y = Input.get_action_strength(\"move_down\") - Input.get_action_strength(\"move_up\")\n\tvar direction = Vector3(input_dir.x,0,input_dir.y).normalized()\n\tvelocity.x = direction.x * speed\n\tvelocity.z = direction.z * speed\n\tmove_and_slide()\n"),
            _write(project_dir / "scripts/Enemy3D.gd", "extends CharacterBody3D\nfunc _physics_process(delta):\n\tmove_and_slide()\n"),
        ]
    else:
        raise ValueError(f"Unknown Godot project template: {project_template}")
    files += [
        _write(project_dir / "scripts/GameManager.gd", "extends Node\n"),
        _write(project_dir / "scripts/UIController.gd", "extends CanvasLayer\nfunc set_status_text(text: String) -> void:\n\t$Control/Label.text = text\n"),
    ]
    return files
