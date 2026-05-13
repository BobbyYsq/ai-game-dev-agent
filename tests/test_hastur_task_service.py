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
            return json.dumps(
                {
                    "summary": "Plan ready",
                    "requires_user_approval": False,
                    "steps": [{"title": "Inspect", "goal": "Inspect the scene", "needs_visual_check": False}],
                    "final": "Done",
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())

    task = hastur_task_service.create_task("shadow-garden", "inspect scene", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Planning live " in joined
    assert "from the model." in joined
    assert "event: thought_delta" in joined
    assert "event: assistant_delta" not in joined
    assert "event: final" in joined
    assert "event: user_prompt" not in joined
    assert "event: git" not in joined
    assert "我会先读取" not in joined


def test_complex_task_runs_without_prompt_when_llm_does_not_need_input(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    applied = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "I will split this into small steps."

        def generate_text(self, prompt, system_prompt=None):
            return json.dumps(
                {
                    "summary": "Village plan ready",
                    "requires_user_approval": False,
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

    assert "event: user_prompt" not in joined
    assert "event: plan_review" not in joined
    assert "event: final" in joined
    assert applied == []


def test_confirmed_plan_generates_code_one_step_at_a_time(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    code_prompts = []
    executed = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "Do not write GDScript in this planning response" in prompt:
                return json.dumps(
                    {
                        "summary": "Plan",
                        "requires_user_approval": False,
                        "steps": [
                            {"title": "Create land", "goal": "Create terrain"},
                            {"title": "Create wall", "goal": "Create a wall"},
                        ],
                        "final": "Done",
                    }
                )
            assert "Generate the smallest safe GDScript snippet" in prompt
            code_prompts.append(prompt)
            return json.dumps({"code": f'executeContext.output("step", "{len(code_prompts)}")'})

    def fake_apply(_slug, code, **_kwargs):
        executed.append(code)
        return HasturExecuteResult(success=True, message="ok", gdscript=code)

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "build a village and wall", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert len(code_prompts) == 2
    assert len(executed) == 2
    assert "event: user_prompt" not in joined
    assert "event: step_result" in joined
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
            if "Do not write GDScript in this planning response" in prompt:
                return '{"summary":"Plan","steps":[{"title":"Create","goal":"Create terrain"}],"final":"Done"}'
            if "previous GDScript failed" in prompt:
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

    assert "event: repair" in joined
    assert "event: final" in joined
    assert "could not be repaired" not in joined


def test_visual_checkpoint_pauses_with_llm_driven_user_prompt(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        supports_images = False

        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "Do not write GDScript in this planning response" in prompt:
                return '{"summary":"Plan","steps":[{"title":"Add sun","goal":"Add sunny lighting","needs_visual_check":true}],"final":"Done"}'
            if "Create the user-facing confirmation prompt" in prompt:
                return '{"title":"Review lighting","body":"The screenshot needs review.","choices":[{"id":"continue","label":"Continue","description":"Looks good","action":"continue"}]}'
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
    assert "Review lighting" in joined


def test_extract_repair_code_from_steps_and_bare_gdscript():
    assert hastur_task_service._extract_executable_code({"steps": [{"code": "if true:\n\tprint(\"ok\")"}]}) == 'if true:\n\tprint("ok")'
    assert hastur_task_service._extract_executable_code({}, 'extends RefCounted\n\nfunc execute(executeContext):\n\texecuteContext.output("ok", "1")').startswith("extends RefCounted")
