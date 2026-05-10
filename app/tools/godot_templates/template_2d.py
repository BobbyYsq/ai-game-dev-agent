from pathlib import Path

from app.tools.godot_templates.base import (
    create_project_godot,
    create_shared_scripts,
    ensure_default_folders,
    write_text,
)


def generate_2d_playable_template(project_dir: Path, project_name: str, game_type: str) -> list[Path]:
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

[ext_resource type="PackedScene" path="res://scenes/TestLevel2D.tscn" id="1_level"]
[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="2_player"]
[ext_resource type="PackedScene" path="res://scenes/Enemy.tscn" id="3_enemy"]
[ext_resource type="PackedScene" path="res://scenes/UI.tscn" id="4_ui"]

[node name="Main" type="Node2D"]

[node name="TestLevel2D" parent="." instance=ExtResource("1_level")]

[node name="Player" parent="." instance=ExtResource("2_player")]
position = Vector2(0, 0)

[node name="Enemy" parent="." instance=ExtResource("3_enemy")]
position = Vector2(220, 0)

[node name="UI" parent="." instance=ExtResource("4_ui")]
""",
    )


def _write_player_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/Player.tscn",
        """[gd_scene load_steps=4 format=3]

[ext_resource type="Script" path="res://scripts/Player2D.gd" id="1_script"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_player"]
size = Vector2(28, 28)

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1_script")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_player")

[node name="Visual" type="Polygon2D" parent="."]
color = Color(0.2, 0.75, 1, 1)
polygon = PackedVector2Array(-14, -14, 14, -14, 14, 14, -14, 14)

[node name="Camera2D" type="Camera2D" parent="."]
enabled = true
zoom = Vector2(0.85, 0.85)
""",
    )


def _write_enemy_scene(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scenes/Enemy.tscn",
        """[gd_scene load_steps=4 format=3]

[ext_resource type="Script" path="res://scripts/Enemy2D.gd" id="1_script"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_enemy"]
size = Vector2(24, 24)

[node name="Enemy" type="CharacterBody2D"]
script = ExtResource("1_script")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_enemy")

[node name="Visual" type="Polygon2D" parent="."]
color = Color(1, 0.35, 0.25, 1)
polygon = PackedVector2Array(-12, -12, 12, -12, 12, 12, -12, 12)
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
        project_dir / "scenes/TestLevel2D.tscn",
        """[gd_scene load_steps=5 format=3]

[sub_resource type="RectangleShape2D" id="FloorShape"]
size = Vector2(720, 360)

[sub_resource type="RectangleShape2D" id="WallShape"]
size = Vector2(32, 360)

[node name="TestLevel2D" type="Node2D"]

[node name="Floor" type="StaticBody2D" parent="."]
position = Vector2(0, 80)

[node name="CollisionShape2D" type="CollisionShape2D" parent="Floor"]
shape = SubResource("FloorShape")

[node name="FloorVisual" type="Polygon2D" parent="Floor"]
color = Color(0.12, 0.16, 0.18, 1)
polygon = PackedVector2Array(-360, -180, 360, -180, 360, 180, -360, 180)

[node name="WallLeft" type="StaticBody2D" parent="."]
position = Vector2(-376, 80)

[node name="CollisionShape2D" type="CollisionShape2D" parent="WallLeft"]
shape = SubResource("WallShape")

[node name="WallVisual" type="Polygon2D" parent="WallLeft"]
color = Color(0.24, 0.28, 0.32, 1)
polygon = PackedVector2Array(-16, -180, 16, -180, 16, 180, -16, 180)

[node name="WallRight" type="StaticBody2D" parent="."]
position = Vector2(376, 80)

[node name="CollisionShape2D" type="CollisionShape2D" parent="WallRight"]
shape = SubResource("WallShape")

[node name="WallVisual" type="Polygon2D" parent="WallRight"]
color = Color(0.24, 0.28, 0.32, 1)
polygon = PackedVector2Array(-16, -180, 16, -180, 16, 180, -16, 180)
""",
    )


def _write_player_script(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scripts/Player2D.gd",
        """extends CharacterBody2D

@export var speed := 220.0

func _physics_process(_delta: float) -> void:
    var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = direction * speed
    move_and_slide()
""",
    )


def _write_enemy_script(project_dir: Path) -> Path:
    return write_text(
        project_dir / "scripts/Enemy2D.gd",
        """extends CharacterBody2D

@export var speed := 90.0
@export var patrol_distance := 160.0

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
