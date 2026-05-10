from pathlib import Path

from app.tools.godot_templates.base import (
    create_project_godot,
    create_shared_scripts,
    ensure_default_folders,
    write_text,
)


def generate_3d_playable_template(project_dir: Path, project_name: str, game_type: str) -> list[Path]:
    ensure_default_folders(project_dir)
    files = [create_project_godot(project_dir, project_name)]
    files.extend(
        [
            _write_main_scene(project_dir),
            _write_player_scene(project_dir),
            _write_enemy_scene(project_dir),
            _write_ui_scene(project_dir),
            _write_test_level_scene(project_dir),
            _write_player_script(project_dir),
            _write_enemy_script(project_dir),
        ]
    )
    files.extend(create_shared_scripts(project_dir))
    return files


def _write_main_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/Main.tscn",
        """[gd_scene load_steps=5 format=3]

[ext_resource type="PackedScene" path="res://scenes/TestLevel3D.tscn" id="1_level"]
[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="2_player"]
[ext_resource type="PackedScene" path="res://scenes/Enemy.tscn" id="3_enemy"]
[ext_resource type="PackedScene" path="res://scenes/UI.tscn" id="4_ui"]

[node name="Main" type="Node3D"]

[node name="TestLevel3D" parent="." instance=ExtResource("1_level")]

[node name="Player" parent="." instance=ExtResource("2_player")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.2, 0)

[node name="Enemy" parent="." instance=ExtResource("3_enemy")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 4, 1.0, -2)

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866, -0.25, 0.433, 0, 0.866, 0.5, -0.5, -0.433, 0.75, 0, 6, 0)
light_energy = 1.5

[node name="UI" parent="." instance=ExtResource("4_ui")]
""",
    )


def _write_player_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/Player.tscn",
        """[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/Player3D.gd" id="1_script"]

[sub_resource type="CapsuleShape3D" id="CapsuleShape3D_player"]
radius = 0.35
height = 1.4

[sub_resource type="CapsuleMesh" id="CapsuleMesh_player"]
radius = 0.35
height = 1.4

[node name="Player" type="CharacterBody3D"]
script = ExtResource("1_script")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("CapsuleShape3D_player")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("CapsuleMesh_player")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.819, 0.574, 0, -0.574, 0.819, 0, 2.6, 4.5)
current = true
""",
    )


def _write_enemy_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/Enemy.tscn",
        """[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/Enemy3D.gd" id="1_script"]

[sub_resource type="BoxShape3D" id="BoxShape3D_enemy"]
size = Vector3(0.8, 0.8, 0.8)

[sub_resource type="BoxMesh" id="BoxMesh_enemy"]
size = Vector3(0.8, 0.8, 0.8)

[node name="Enemy" type="CharacterBody3D"]
script = ExtResource("1_script")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("BoxShape3D_enemy")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("BoxMesh_enemy")
""",
    )


def _write_ui_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/UI.tscn",
        """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/UIController.gd" id="1_script"]

[node name="UI" type="CanvasLayer"]
script = ExtResource("1_script")

[node name="Control" type="Control" parent="."]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Panel" type="Panel" parent="Control"]
offset_left = 16.0
offset_top = 16.0
offset_right = 340.0
offset_bottom = 72.0

[node name="StatusLabel" type="Label" parent="Control/Panel"]
offset_left = 12.0
offset_top = 12.0
offset_right = 300.0
offset_bottom = 44.0
text = "Prototype ready"
""",
    )


def _write_test_level_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/TestLevel3D.tscn",
        """[gd_scene load_steps=4 format=3]

[sub_resource type="BoxShape3D" id="GroundShape"]
size = Vector3(12, 0.2, 12)

[sub_resource type="BoxMesh" id="GroundMesh"]
size = Vector3(12, 0.2, 12)

[node name="TestLevel3D" type="Node3D"]

[node name="Ground" type="StaticBody3D" parent="."]

[node name="CollisionShape3D" type="CollisionShape3D" parent="Ground"]
shape = SubResource("GroundShape")

[node name="MeshInstance3D" type="MeshInstance3D" parent="Ground"]
mesh = SubResource("GroundMesh")
""",
    )


def _write_player_script(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scripts/Player3D.gd",
        """extends CharacterBody3D

@export var speed := 5.0
@export var gravity := 18.0

func _physics_process(delta: float) -> void:
    var input_dir := Vector2.ZERO
    input_dir.x = Input.get_action_strength("move_right") - Input.get_action_strength("move_left")
    input_dir.y = Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
    var direction := Vector3(input_dir.x, 0.0, input_dir.y).normalized()

    velocity.x = direction.x * speed
    velocity.z = direction.z * speed
    if not is_on_floor():
        velocity.y -= gravity * delta
    else:
        velocity.y = 0.0

    move_and_slide()
""",
    )


def _write_enemy_script(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scripts/Enemy3D.gd",
        """extends CharacterBody3D

@export var speed := 1.6
@export var patrol_distance := 3.0

var start_x := 0.0
var direction := 1.0

func _ready() -> void:
    start_x = global_position.x

func _physics_process(_delta: float) -> void:
    velocity.x = speed * direction
    if abs(global_position.x - start_x) > patrol_distance:
        direction *= -1.0
    move_and_slide()
""",
    )
