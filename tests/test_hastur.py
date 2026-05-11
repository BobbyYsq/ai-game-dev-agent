import pytest

from app.agent.godot_operation_planner import parse_operation_plan
from app.models.mock_provider import MockLLMProvider
from app.services.hastur_service import GodotOperation, build_gdscript


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


def test_mock_llm_returns_valid_operation_plan_for_planner_prompt():
    raw = MockLLMProvider().generate_text("Return only JSON\nAllowed operation values:")
    plan = parse_operation_plan(raw)

    assert plan.operations[0].operation == "open_scene"
