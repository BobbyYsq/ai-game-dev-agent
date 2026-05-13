import pytest

from app.agent.godot_operation_planner import parse_operation_plan
from app.services import hastur_service
from app.services.hastur_service import GodotOperation, apply_hastur_code, build_gdscript, normalize_gdscript_code


def test_godot_operation_validation_requires_node_fields():
    with pytest.raises(ValueError):
        GodotOperation(operation="create_node", node_type="Node2D")


def test_build_gdscript_for_create_node_is_controlled():
    operation = GodotOperation(
        operation="create_node",
        node_type="Node2D",
        node_name="AgentGeneratedNode",
        parent_path=".",
    )

    script = build_gdscript(operation)

    assert "ClassDB.instantiate" in script
    assert "AgentGeneratedNode" in script
    assert "EditorInterface.mark_scene_as_unsaved" in script


def test_normalize_gdscript_strips_fences_and_uses_tabs():
    raw = """```gdscript
if true:
    print("keeps    inner spaces")
\t  if false:
\t    print("nested")
```"""

    script = normalize_gdscript_code(raw)

    assert script.startswith("if true:")
    assert "\n\tprint(\"keeps    inner spaces\")" in script
    assert "\n\t\tif false:" in script
    assert "```" not in script


def test_normalize_gdscript_rewrites_keyword_identifier():
    raw = "func ensure_node(parent, node_name, class_name):\n    return ClassDB.instantiate(class_name)"

    script = normalize_gdscript_code(raw)

    assert "class_name" not in script
    assert "node_type_name" in script


def test_apply_hastur_code_treats_compile_failure_as_failure(tmp_path, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": True, "data": {"compile_success": False, "compile_error": "Mixed use of tabs and spaces for indentation."}}

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr(hastur_service, "get_project_dir", lambda _slug: tmp_path)
    monkeypatch.setattr(hastur_service, "get_hastur_settings", lambda: {"enabled": True, "base_url": "http://localhost:5302", "auth_token": ""})
    monkeypatch.setattr(hastur_service.httpx, "Client", FakeClient)

    result = apply_hastur_code("shadow-garden", "if true:\n    print(\"ok\")")

    assert result.success is False
    assert "compile failed" in result.message.lower()
    assert "\n\tprint" in result.gdscript


def test_parse_operation_plan_validates_operations():
    plan = parse_operation_plan(
        {
            "operations": [
                {"operation": "open_scene", "target_scene": "res://scenes/Main.tscn"},
                {"operation": "save_scene"},
            ]
        }
    )

    assert len(plan.operations) == 2


def test_planner_json_fixture_returns_valid_operation_plan():
    raw = '{"operations": [{"operation": "open_scene", "target_scene": "res://scenes/Main.tscn"}]}'
    plan = parse_operation_plan(raw)

    assert plan.operations[0].operation == "open_scene"
