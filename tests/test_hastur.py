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


def test_normalize_gdscript_promotes_execute_function_to_full_class():
    raw = """func _execute(executeContext):
    print(1)
    executeContext.output("result", "1")"""

    script = normalize_gdscript_code(raw)

    assert script.startswith("extends RefCounted\n\nfunc execute(executeContext):")
    assert "\n\tprint(1)" in script
    assert "\n\texecuteContext.output" in script


def test_normalize_gdscript_promotes_batch_helper_to_full_class():
    raw = """func _hastur_batch(executeContext):
    executeContext.output("result", "ok")"""

    script = normalize_gdscript_code(raw)

    assert script.startswith("extends RefCounted\n\nfunc execute(executeContext):")
    assert "\n\t_hastur_batch(executeContext)" in script
    assert "\nfunc _hastur_batch(executeContext):" in script


def test_normalize_gdscript_converts_full_class_run_entrypoint():
    raw = """extends RefCounted

func run(executeContext) -> void:
    var text: String = "hello world"
    print(text)
    executeContext.output("result", text)"""

    script = normalize_gdscript_code(raw)

    assert script.startswith("extends RefCounted\n\nfunc execute(executeContext) -> void:")
    assert "\nfunc run(executeContext)" not in script
    assert "\n\texecuteContext.output" in script


def test_normalize_gdscript_converts_full_class_execute_alias():
    raw = """extends RefCounted

func _execute(executeContext):
    executeContext.output("result", "1")"""

    script = normalize_gdscript_code(raw)

    assert script.startswith("extends RefCounted\n\nfunc execute(executeContext):")
    assert "\nfunc _execute(executeContext)" not in script


def test_normalize_gdscript_bridges_full_class_zero_arg_run():
    raw = """extends RefCounted

func run():
    executeContext.output("result", "ok")"""

    script = normalize_gdscript_code(raw)

    assert script.startswith("extends RefCounted\n\nvar executeContext\n\nfunc execute(executeContext):")
    assert "\n\tself.executeContext = executeContext" in script
    assert "\n\trun()" in script
    assert "\nfunc run():" in script


def test_apply_hastur_code_treats_compile_failure_as_failure(tmp_path, monkeypatch):
    captured = {}

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

        def post(self, *_args, **kwargs):
            captured.update(kwargs.get("json") or {})
            return FakeResponse()

    monkeypatch.setattr(hastur_service, "get_project_dir", lambda _slug: tmp_path)
    monkeypatch.setattr(hastur_service, "get_hastur_settings", lambda: {"enabled": True, "base_url": "http://localhost:5302", "auth_token": ""})
    monkeypatch.setattr(hastur_service.httpx, "Client", FakeClient)

    result = apply_hastur_code("shadow-garden", "if true:\n    print(\"ok\")")

    assert result.success is False
    assert "compile failed" in result.message.lower()
    assert "\n\tprint" in result.gdscript
    assert captured["project_path"] == tmp_path.resolve().as_posix()


def test_apply_hastur_code_returns_executor_mismatch_guidance(tmp_path, monkeypatch):
    class FakeResponse:
        status_code = 404
        reason_phrase = "Not Found"
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "success": False,
                "error": "No connected Hastur Executor matched the query",
                "hint": "Use GET /api/executors to list available executors.",
            }

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

    result = apply_hastur_code("shadow-garden", 'print("1")', executor_type="editor")

    assert result.success is False
    assert "No connected Hastur executor matched this project" in result.message
    assert "localhost:5301" in result.message
    assert "DAP" in result.message


def test_apply_hastur_code_migrates_missing_project_hastur_settings(tmp_path, monkeypatch):
    project_file = tmp_path / "project.godot"
    project_file.write_text(
        """config_version=5

[application]
config/name="shadow-garden"

[editor_plugins]
enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")
""",
        encoding="utf-8",
    )

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": True, "data": {"compile_success": True, "run_success": True, "outputs": []}}

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
    monkeypatch.setattr(
        hastur_service,
        "get_hastur_settings",
        lambda: {
            "enabled": True,
            "base_url": "http://localhost:5302",
            "auth_token": "",
            "hastur_broker_host": "localhost",
            "hastur_broker_tcp_port": 5301,
        },
    )
    monkeypatch.setattr(hastur_service.httpx, "Client", FakeClient)

    result = apply_hastur_code("shadow-garden", 'print("1")')

    text = project_file.read_text(encoding="utf-8")
    assert result.success is True
    assert "[hastur_operation]" in text
    assert 'broker_host="localhost"' in text
    assert "broker_port=5301" in text


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
