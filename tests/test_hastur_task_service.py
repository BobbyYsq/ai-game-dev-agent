import json

from app.services import hastur_skill_service, hastur_task_service
from app.services.hastur_service import HasturExecuteResult


def _setup_project(tmp_path, monkeypatch):
    project_root = tmp_path / "generated"
    project = project_root / "shadow-garden"
    project.mkdir(parents=True)
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "godot-remote-executor"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("Use this skill before Godot actions.", encoding="utf-8")
    monkeypatch.setattr("app.services.asset_service.GENERATED_PROJECTS_DIR", project_root)
    monkeypatch.setattr(hastur_skill_service, "HASTUR_SKILLS_DIR", skills_dir)
    monkeypatch.setattr(hastur_task_service, "hastur_executors", lambda: {"available": True, "executors": [{"id": "one"}]})
    monkeypatch.setattr(hastur_task_service, "load_private_settings", lambda: {"hastur_auth_token": "token", "hastur_enabled": True})
    return project


def test_hastur_task_streams_real_llm_delta_without_hardcoded_intro(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning live "
            yield "from the model."

        def generate_text(self, prompt, system_prompt=None):
            assert "Use this skill before Godot actions." in prompt
            assert "Nodes and Scenes" in prompt
            if "Generate ONE complete GDScript" in prompt:
                return json.dumps({"code": 'executeContext.output("result", "Scene inspected")'})
            return json.dumps(
                {
                    "summary": "Plan ready",
                    "read_only": True,
                    "requires_user_approval": False,
                    "steps": [{"title": "Inspect", "goal": "Inspect the scene", "needs_visual_check": False}],
                    "final": "Done",
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(
        hastur_task_service,
        "apply_hastur_code",
        lambda _slug, code, **_kwargs: HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "Scene inspected"]]}},
        ),
    )

    task = hastur_task_service.create_task("shadow-garden", "inspect scene", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Planning live " in joined
    assert "from the model." in joined
    assert "event: thought_delta" in joined
    assert "event: assistant_delta" in joined
    assert "event: final" in joined
    assert "event: user_prompt" not in joined
    assert "event: git" not in joined
    assert "我会先读取" not in joined


def test_complex_task_prompts_for_plan_confirmation_without_running_first(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    applied = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "I will split this into small steps."

        def generate_text(self, prompt, system_prompt=None):
            return json.dumps(
                {
                    "summary": "Village plan ready",
                    "mode": "plan",
                    "requires_user_approval": True,
                    "steps": [
                        {"title": "Create land", "goal": "Create the terrain"},
                        {"title": "Add sun", "goal": "Add conservative sunny lighting", "needs_visual_check": False},
                    ],
                    "final": "Done",
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: applied.append(True))

    task = hastur_task_service.create_task("shadow-garden", "build a village and add sunny post-processing", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "event: user_prompt" in joined
    assert "event: plan_review" not in joined
    assert "event: final" not in joined
    assert applied == []


def test_direct_task_executes_without_plan_or_confirmation(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    executed = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "I can run this directly."

        def generate_text(self, prompt, system_prompt=None):
            assert "You decide whether the request needs a visible plan" in prompt
            return json.dumps(
                {
                    "mode": "direct",
                    "summary": "Print 1",
                    "read_only": False,
                    "steps": [],
                    "code": 'print("1")\nexecuteContext.output("result", "1")',
                    "final": "Printed 1",
                }
            )

    def fake_apply(_slug, code, **_kwargs):
        executed.append(code)
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "1"]]}},
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "打印1", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert executed == ['print("1")\nexecuteContext.output("result", "1")']
    assert "event: user_prompt" not in joined
    assert "Plan:" not in joined
    assert '"message": "1"' in joined


def test_confirmed_plan_generates_one_complete_batch(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    code_prompts = []
    executed = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "You decide whether the request needs a visible plan" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Plan",
                        "requires_user_approval": False,
                        "steps": [
                            {"title": "Create land", "goal": "Create terrain"},
                            {"title": "Create wall", "goal": "Create a wall"},
                        ],
                        "final": "Done",
                    }
                )
            assert "Generate ONE complete GDScript snippet" in prompt
            assert "entire confirmed plan in one run" in prompt
            code_prompts.append(prompt)
            return json.dumps({"code": 'executeContext.output("batch", "done")'})

    def fake_apply(_slug, code, **_kwargs):
        executed.append(code)
        return HasturExecuteResult(success=True, message="ok", gdscript=code)

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "build a village and wall", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert len(code_prompts) == 1
    assert len(executed) == 1
    assert "event: user_prompt" not in joined
    assert "event: step_result" not in joined
    assert "event: final" in joined


def test_llm_user_prompt_uses_unified_prompt_event(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "I need one design choice."

        def generate_text(self, prompt, system_prompt=None):
            return json.dumps(
                {
                    "summary": "Need direction",
                    "user_prompt": {
                        "title": "Choose style",
                        "body": "Which village style should I use?",
                        "choices": [{"id": "cozy", "label": "Cozy", "description": "Warm and bright"}],
                    },
                    "steps": [{"title": "Build village", "goal": "Create the selected style"}],
                    "final": "Done",
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())

    task = hastur_task_service.create_task("shadow-garden", "build a village", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "event: user_prompt" in joined
    assert "Choose style" in joined
    assert "event: plan_review" not in joined
    assert "event: visual_checkpoint" not in joined
    assert "event: step_result" not in joined


def test_hastur_task_repairs_failed_step_code(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def __init__(self):
            self.repair = False

        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "You decide whether the request needs a visible plan" in prompt:
                return '{"mode":"plan","summary":"Plan","read_only":true,"steps":[{"title":"Create","goal":"Create terrain"}],"final":"Done"}'
            if "previous complete Hastur GDScript batch failed" in prompt:
                self.repair = True
                assert "Mixed use of tabs and spaces" in prompt
                return '{"code":"if true:\\n\\tprint(\\"fixed\\")"}'
            return '{"code":"if true:\\n    print(\\"bad\\")"}'

    results = [
        HasturExecuteResult(success=False, message="Hastur compile failed: Mixed use of tabs and spaces for indentation.", gdscript="bad"),
        HasturExecuteResult(success=True, message="Hastur skill code executed.", gdscript="fixed"),
    ]

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: results.pop(0))

    task = hastur_task_service.create_task("shadow-garden", "make land", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Repairing complete Hastur script" in joined
    assert "event: thought_delta" in joined
    assert "event: final" in joined
    assert "could not be repaired" not in joined


def test_hastur_task_keeps_repairing_until_success(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    repair_prompts = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "You decide whether the request needs a visible plan" in prompt:
                return '{"mode":"plan","summary":"Plan","read_only":true,"steps":[{"title":"Create","goal":"Create terrain"}],"final":"Done"}'
            if "previous complete Hastur GDScript batch failed" in prompt:
                repair_prompts.append(prompt)
                assert "compile failed" in prompt.lower() or "runtime failed" in prompt.lower()
                if len(repair_prompts) < 3:
                    return '{"code":"if true:\\n\\tprint(\\"still bad\\")"}'
                return '{"code":"if true:\\n\\tprint(\\"fixed\\")"}'
            return '{"code":"if true:\\n\\tprint(\\"bad\\")"}'

    results = [
        HasturExecuteResult(success=False, message="Hastur compile failed: first compile failed", gdscript="bad", broker_response={"data": {"compile_success": False, "compile_error": "first compile failed"}}),
        HasturExecuteResult(success=False, message="Hastur compile failed: second compile failed", gdscript="bad2", broker_response={"data": {"compile_success": False, "compile_error": "second compile failed"}}),
        HasturExecuteResult(success=False, message="Hastur runtime failed: third runtime failed", gdscript="bad3", broker_response={"data": {"run_success": False, "run_error": "third runtime failed"}}),
        HasturExecuteResult(success=True, message="Hastur skill code executed.", gdscript="fixed"),
    ]

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: results.pop(0))

    task = hastur_task_service.create_task("shadow-garden", "make land", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert len(repair_prompts) == 3
    assert "event: final" in joined
    assert "could not be repaired" not in joined


def test_hastur_task_final_uses_hastur_output(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Reading the scene."

        def generate_text(self, prompt, system_prompt=None):
            if "You decide whether the request needs a visible plan" in prompt:
                return '{"mode":"plan","summary":"Plan","read_only":true,"steps":[{"title":"Read tree","goal":"Return the current scene tree"}],"final":"Repeated plan text"}'
            assert 'executeContext.output("result", text)' in prompt
            assert "Generate ONE complete GDScript" in prompt
            return '{"code":"executeContext.output(\\"scene_tree\\", \\"Main\\\\n  Label\\")"}'

    def fake_apply(_slug, code, **_kwargs):
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["scene_tree", "Main\n  Label"]]}},
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "list the full scene tree", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Main\\n  Label" in joined
    assert '"type": "final", "state": "complete", "message": "Main\\n  Label"' in joined


def test_visual_checkpoint_pauses_with_llm_driven_user_prompt(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        supports_images = False

        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "You decide whether the request needs a visible plan" in prompt:
                return '{"mode":"plan","summary":"Plan","steps":[{"title":"Add sun","goal":"Add sunny lighting","needs_visual_check":true}],"final":"Done"}'
            return '{"code":"executeContext.output(\\"ok\\", \\"1\\")"}'

    results = [
        HasturExecuteResult(success=True, message="step ok", gdscript="step"),
        HasturExecuteResult(success=True, message="screenshot missing but command ok", gdscript="shot", broker_response={"data": {"outputs": [["image_path", "res://assets/generated/visual_checkpoints/missing.png"]]}}),
    ]

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: results.pop(0))

    task = hastur_task_service.create_task("shadow-garden", "add sunny lighting", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "event: user_prompt" in joined
    assert "event: visual_checkpoint" not in joined
    assert "image_status" in joined
    assert "missing" in joined


def test_visual_checkpoint_only_exposes_verified_non_empty_png(tmp_path, monkeypatch):
    project = _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        supports_images = False

        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "You decide whether the request needs a visible plan" in prompt:
                return '{"mode":"plan","summary":"Plan","steps":[{"title":"Add camera","goal":"Adjust camera","needs_visual_check":true}],"final":"Done"}'
            return '{"code":"executeContext.output(\\"ok\\", \\"1\\")"}'

    calls = {"count": 0}

    def fake_apply(_slug, code, **_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return HasturExecuteResult(success=True, message="batch ok", gdscript=code)
        checkpoint = project / "assets" / "generated" / "visual_checkpoints" / "verified.png"
        checkpoint.parent.mkdir(parents=True)
        checkpoint.write_bytes(b"\x89PNG\r\n\x1a\nnonempty")
        return HasturExecuteResult(
            success=True,
            message="screenshot ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["image_status", "available"], ["image_path", "res://assets/generated/visual_checkpoints/verified.png"]]}},
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "adjust camera visual", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "event: user_prompt" in joined
    assert '"image_status": "available"' in joined
    assert "/api/projects/shadow-garden/visual-checkpoints/verified.png" in joined


def test_extract_repair_code_from_steps_and_bare_gdscript():
    assert hastur_task_service._extract_executable_code({"steps": [{"code": "if true:\n\tprint(\"ok\")"}]}) == 'if true:\n\tprint("ok")'
    assert hastur_task_service._extract_executable_code({}, 'extends RefCounted\n\nfunc execute(executeContext):\n\texecuteContext.output("ok", "1")').startswith("extends RefCounted")
