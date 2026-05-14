import json

from app.services import hastur_skill_service, hastur_task_service
from app.services.hastur_service import HasturExecuteResult


def _event_messages(stream: str) -> list[str]:
    messages = []
    for chunk in stream.split("\n\n"):
        data_line = next((line for line in chunk.splitlines() if line.startswith("data: ")), "")
        if not data_line:
            continue
        try:
            messages.append(json.loads(data_line.removeprefix("data: ")).get("message", ""))
        except json.JSONDecodeError:
            pass
    return messages


def _event_payloads(stream: str, event_type: str) -> list[dict]:
    payloads = []
    marker = f"event: {event_type}"
    for chunk in stream.split("\n\n"):
        if marker not in chunk:
            continue
        data_line = next((line for line in chunk.splitlines() if line.startswith("data: ")), "")
        if data_line:
            payloads.append(json.loads(data_line.removeprefix("data: ")))
    return payloads


def _setup_project(tmp_path, monkeypatch):
    project_root = tmp_path / "generated"
    project = project_root / "shadow-garden"
    project.mkdir(parents=True)
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "godot-remote-executor"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: godot-remote-executor\n"
        "description: Remote Godot editor executor.\n"
        "when_to_use: Use for Godot scene inspection and editor mutations.\n"
        "---\n\n"
        "Use this full skill body before Godot actions.",
        encoding="utf-8",
    )
    monkeypatch.setattr("app.services.asset_service.GENERATED_PROJECTS_DIR", project_root)
    monkeypatch.setattr(hastur_skill_service, "HASTUR_SKILLS_DIR", skills_dir)
    monkeypatch.setattr(hastur_skill_service, "USER_SKILLS_DIR", tmp_path / "global-skills")
    monkeypatch.setattr(hastur_task_service, "hastur_executors", lambda: {"available": True, "executors": [{"id": "one"}]})
    monkeypatch.setattr(hastur_task_service, "load_private_settings", lambda: {"hastur_auth_token": "token", "hastur_enabled": True})
    return project


def test_hastur_task_streams_real_llm_delta_without_agent_status_text(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    planning_prompts = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning live "
            yield "from the model."

        def generate_text(self, prompt, system_prompt=None):
            planning_prompts.append(prompt)
            if "Generate ONE complete GDScript" in prompt:
                assert "Use this full skill body" not in prompt
                return json.dumps({"code": 'executeContext.output("result", "Scene inspected")'})
            assert "Capability registry" in prompt
            assert "Godot docs index" in prompt
            assert "Available skills" in prompt
            assert "Use this full skill body" not in prompt
            return json.dumps(
                {
                    "summary": "Plan ready",
                    "read_only": True,
                    "requires_user_approval": False,
                    "steps": [{"title": "Inspect", "goal": "Inspect the scene"}],
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
    assert "event: task_breakdown" in joined
    breakdown = _event_payloads(joined, "task_breakdown")[0]["detail"]
    assert breakdown["tasks"][0]["title"] == "Inspect"
    assert "event: final" in joined
    assert "event: user_prompt" not in joined
    assert "Loaded project context" not in joined
    assert "After you confirm" not in joined


def test_plan_mode_uses_llm_modal_and_does_not_run_before_confirmation(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    applied = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "I am planning first."

        def generate_text(self, prompt, system_prompt=None):
            assert 'Workflow mode is "plan"' in prompt
            return json.dumps(
                {
                    "mode": "plan",
                    "summary": "Village plan ready",
                    "requires_user_approval": True,
                    "user_prompt": {
                        "title": "Approve village plan",
                        "body": "I can build the village in one approved batch.",
                        "choices": [{"id": "approve", "label": "Approve", "description": "Run the plan", "action": "confirm"}],
                        "requires_input": False,
                    },
                    "steps": [{"title": "Create land", "goal": "Create the terrain"}],
                    "final": "Done",
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: applied.append(True))

    task = hastur_task_service.create_task(
        "shadow-garden",
        "build a village",
        "godot-remote-executor",
        workflow_mode="plan",
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "event: user_prompt" in joined
    assert "Approve village plan" in joined
    assert "Review result" not in joined
    assert applied == []


def test_plan_mode_repairs_direct_code_into_modal_without_execution(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    applied = []
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning only."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if "requires user approval but did not instantiate" in prompt:
                assert 'executeContext.output("result", "ran")' not in prompt
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Review direct request",
                        "requires_user_approval": True,
                        "user_prompt": {
                            "title": "Approve safe plan",
                            "body": "Review the requested editor change before I execute it.",
                            "choices": [{"id": "approve", "label": "Approve", "action": "confirm"}],
                            "input_label": "Notes",
                            "requires_input": False,
                        },
                        "steps": [{"title": "Apply approved change", "goal": "Run the editor update after approval."}],
                    }
                )
            return json.dumps(
                {
                    "mode": "direct",
                    "summary": "Unsafe direct response",
                    "steps": [],
                    "code": 'executeContext.output("result", "ran")',
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: applied.append(True))

    task = hastur_task_service.create_task(
        "shadow-garden",
        "change the scene",
        "godot-remote-executor",
        workflow_mode="plan",
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert calls["count"] == 2
    assert "event: user_prompt" in joined
    assert "Approve safe plan" in joined
    assert "event: final" not in joined
    assert applied == []


def test_resume_after_modal_streams_new_public_thought(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            if "user just responded to an abstract modal" in prompt:
                yield "Continuing from the selected option."
            else:
                yield "Planning first."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Plan ready",
                        "requires_user_approval": True,
                        "user_prompt": {
                            "title": "Approve fix",
                            "body": "Approve this fix?",
                            "choices": [{"id": "approve", "label": "Approve", "action": "confirm"}],
                            "requires_input": False,
                        },
                        "steps": [{"title": "Fix", "goal": "Apply the correction"}],
                    }
                )
            if "Generate ONE complete GDScript" in prompt:
                return json.dumps({"code": 'executeContext.output("result", "Fixed")'})
            raise AssertionError(prompt)

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "Fixed"]]}}
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "fix terrain", "godot-remote-executor", workflow_mode="plan")
    first = "".join(hastur_task_service.stream_task_events(task["task_id"]))
    assert "event: user_prompt" in first

    hastur_task_service.resume_task(task["task_id"], answer="Target the Terrain node.", choice_id="approve")
    second = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Continuing from the selected option." in second
    assert "event: thought_delta" in second
    assert "event: final" in second
    assert apply_calls["count"] == 1


def test_ask_prompt_choice_replans_instead_of_skipping_empty_question_plan(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            if "user just responded to an abstract modal" in prompt:
                yield "Using the selected approach."
            else:
                yield "Checking what to ask."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if calls["count"] == 1:
                return json.dumps(
                    {
                        "mode": "ask",
                        "execution_strategy": "ask_first",
                        "summary": "Need target choice",
                        "user_prompt": {
                            "title": "Choose target method",
                            "body": "Choose how I should find the target.",
                            "choices": [
                                {
                                    "id": "auto_find",
                                    "label": "Auto-detect target",
                                    "description": "Inspect likely continent mesh nodes and then fix the match.",
                                    "action": "continue",
                                },
                                {
                                    "id": "i_will_input",
                                    "label": "I will provide the path",
                                    "description": "Use the custom reply box instead.",
                                },
                            ],
                            "requires_input": False,
                        },
                        "steps": [],
                        "task_breakdown": [{"id": "ask", "title": "Confirm target", "goal": "Ask first"}],
                    }
                )
            assert "Selected option label: Auto-detect target" in prompt
            assert "Selected option details: Inspect likely continent mesh nodes" in prompt
            return json.dumps(
                {
                    "mode": "direct",
                    "summary": "Fix selected target",
                    "steps": [],
                    "code": (
                        'executeContext.output("result", '
                        '"Before: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=-1.00 top_visible=false\\n'
                        'After: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true")'
                    ),
                }
            )

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={
                "data": {
                    "outputs": [
                        [
                            "result",
                            (
                                "Before: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=-1.00 top_visible=false\n"
                                "After: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true"
                            ),
                        ]
                    ]
                }
            },
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "fix continent material", "godot-remote-executor")
    first = "".join(hastur_task_service.stream_task_events(task["task_id"]))
    prompt_detail = _event_payloads(first, "user_prompt")[0]["detail"]
    assert [choice["id"] for choice in prompt_detail["choices"]] == ["auto_find"]

    hastur_task_service.resume_task(task["task_id"], choice_id="auto_find")
    second = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert calls["count"] == 2
    assert apply_calls["count"] == 1
    assert "event: final" in second
    assert "path=GeneratedContent/TerrainMesh" in second
    assert "top_visible=true" in second
    assert "skipped" not in second


def test_plan_confirmation_repairs_missing_llm_modal_content(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    applied = []
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if "requires user approval but did not instantiate" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Plan with modal",
                        "requires_user_approval": True,
                        "user_prompt": {
                            "title": "Approve plan",
                            "body": "Approve this plan?",
                            "choices": [{"id": "approve", "label": "Approve", "action": "confirm"}],
                        },
                        "steps": [{"title": "Create land", "goal": "Create terrain"}],
                    }
                )
            return json.dumps(
                {
                    "mode": "plan",
                    "summary": "Plan without modal",
                    "requires_user_approval": True,
                    "steps": [{"title": "Create land", "goal": "Create terrain"}],
                    "final": "Done",
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: applied.append(True))

    task = hastur_task_service.create_task("shadow-garden", "build a village", "godot-remote-executor", workflow_mode="plan")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert calls["count"] == 2
    assert "event: user_prompt" in joined
    assert "Approve plan" in joined
    assert "event: error" not in joined
    assert applied == []


def test_plan_confirmation_retries_modal_repair_and_preserves_llm_choice_count(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    applied = []
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if calls["count"] == 1:
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Plan without modal",
                        "requires_user_approval": True,
                        "steps": [{"title": "Create land", "goal": "Create terrain"}],
                    }
                )
            if calls["count"] == 2:
                return json.dumps({"mode": "plan", "summary": "Still missing modal"})
            assert "Previous invalid repair response" in prompt
            return json.dumps(
                {
                    "mode": "plan",
                    "summary": "Plan with three choices",
                    "requires_user_approval": True,
                    "user_prompt": {
                        "title": "Choose execution style",
                        "body": "Pick the approach for this plan.",
                        "choices": [
                            {"id": "approve_now", "label": "Approve now", "action": "confirm"},
                            {"id": "inspect_first", "label": "Inspect first", "action": "continue"},
                            {"id": "revise_scope", "label": "Revise scope", "action": "revise"},
                        ],
                        "input_label": "Other instructions",
                        "requires_input": False,
                    },
                    "steps": [{"title": "Create land", "goal": "Create terrain"}],
                }
            )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: applied.append(True))

    task = hastur_task_service.create_task("shadow-garden", "build a village", "godot-remote-executor", workflow_mode="plan")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))
    prompt_detail = _event_payloads(joined, "user_prompt")[0]["detail"]

    assert calls["count"] == 3
    assert "event: user_prompt" in joined
    assert "event: error" not in joined
    assert [choice["label"] for choice in prompt_detail["choices"]] == ["Approve now", "Inspect first", "Revise scope"]
    assert applied == []


def test_confirmed_multi_step_plan_generates_sequential_batches(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    code_prompts = []
    executed = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
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
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "done"]]}},
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "build a village and wall", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert len(code_prompts) == 2
    assert len(executed) == 2
    assert "event: user_prompt" not in joined
    assert "event: final" in joined


def test_sequential_subtasks_emit_progress_and_execute_each_task(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    executed = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning phased work."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "complexity": "multi_step",
                        "execution_strategy": "sequential_subtasks",
                        "summary": "Two task plan",
                        "steps": [
                            {"title": "Inspect mesh", "goal": "Read current state"},
                            {"title": "Fix mesh", "goal": "Apply correction"},
                        ],
                        "task_breakdown": [
                            {"id": "inspect", "title": "Inspect mesh", "goal": "Read current state"},
                            {"id": "fix", "title": "Fix mesh", "goal": "Apply correction"},
                        ],
                    }
                )
            assert "Generate ONE complete GDScript snippet" in prompt
            if "Inspect mesh" in prompt:
                return json.dumps({"code": 'executeContext.output("result", "Before: mesh state\\nAfter: mesh state inspected")'})
            return json.dumps({"code": 'executeContext.output("result", "Before: mesh state inspected\\nAfter: mesh fixed")'})

    def fake_apply(_slug, code, **_kwargs):
        executed.append(code)
        text = "Before: mesh state\nAfter: mesh state inspected" if "state inspected" in code and "mesh fixed" not in code else "Before: mesh state inspected\nAfter: mesh fixed"
        return HasturExecuteResult(success=True, message="ok", gdscript=code, broker_response={"data": {"outputs": [["result", text]]}})

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "inspect then fix mesh", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))
    progress = _event_payloads(joined, "task_progress")

    assert len(executed) == 2
    assert any(event["detail"]["current_task_id"] == "inspect" for event in progress)
    assert any(event["detail"]["current_task_id"] == "fix" for event in progress)
    assert "Before: mesh state" in joined
    assert "After: mesh fixed" in joined


def test_multi_step_plan_forces_sequential_subtasks_even_if_llm_requests_single_batch(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    executed = []

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning phased work."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "complexity": "multi_step",
                        "execution_strategy": "single_batch",
                        "summary": "Complex map plan",
                        "steps": [
                            {"title": "Build terrain", "goal": "Create base land and water"},
                            {"title": "Add biomes", "goal": "Place forests and mountains"},
                        ],
                        "task_breakdown": [
                            {"id": "terrain", "title": "Build terrain", "goal": "Create base land and water"},
                            {"id": "biomes", "title": "Add biomes", "goal": "Place forests and mountains"},
                        ],
                    }
                )
            if "Build terrain" in prompt:
                return json.dumps({"code": 'executeContext.output("result", "terrain done")'})
            return json.dumps({"code": 'executeContext.output("result", "biomes done")'})

    def fake_apply(_slug, code, **_kwargs):
        executed.append(code)
        text = "terrain done" if "terrain done" in code else "biomes done"
        return HasturExecuteResult(success=True, message="ok", gdscript=code, broker_response={"data": {"outputs": [["result", text]]}})

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "make a complex continent map", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))
    breakdown = _event_payloads(joined, "task_breakdown")[0]["detail"]
    progress = _event_payloads(joined, "task_progress")

    assert breakdown["execution_strategy"] == "sequential_subtasks"
    assert len(executed) == 2
    assert any(event["detail"]["current_task_id"] == "terrain" for event in progress)
    assert any(event["detail"]["current_task_id"] == "biomes" for event in progress)
    assert "terrain done" in joined
    assert "biomes done" in joined


def test_hastur_task_repairs_failed_batch_without_streaming_agent_status(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return '{"mode":"plan","summary":"Plan","read_only":true,"steps":[{"title":"Create","goal":"Create terrain"}],"final":"Done"}'
            if "previous complete Hastur GDScript batch failed" in prompt:
                assert "Mixed use of tabs and spaces" in prompt
                return '{"code":"if true:\\n\\tprint(\\"fixed\\")"}'
            return '{"code":"if true:\\n    print(\\"bad\\")"}'

    results = [
        HasturExecuteResult(success=False, message="Hastur compile failed: Mixed use of tabs and spaces for indentation.", gdscript="bad"),
        HasturExecuteResult(
            success=True,
            message="Hastur skill code executed.",
            gdscript="fixed",
            broker_response={"data": {"outputs": [["result", "fixed"]]}},
        ),
    ]

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", lambda *_args, **_kwargs: results.pop(0))

    task = hastur_task_service.create_task("shadow-garden", "make land", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Repairing complete Hastur script" not in joined
    assert "event: thought_delta" in joined
    assert "event: final" in joined
    assert "could not be repaired" not in joined


def test_hastur_task_final_uses_hastur_output(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Reading the scene."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
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


def test_hastur_task_repairs_success_without_scene_tree_output(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Reading the scene."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return '{"mode":"plan","summary":"Read main scene tree","read_only":true,"steps":[{"title":"Read tree","goal":"Return the current scene tree"}],"final":"Repeated plan text"}'
            if "previous complete Hastur GDScript batch failed" in prompt:
                assert "returned no non-empty executeContext.output entries" in prompt
                return '{"code":"executeContext.output(\\"scene_tree\\", \\"Main\\\\n  Camera2D\\")"}'
            return '{"code":"print(\\"forgot output\\")"}'

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        if apply_calls["count"] == 1:
            return HasturExecuteResult(
                success=True,
                message="Hastur skill code executed.",
                gdscript=code,
                broker_response={"success": True, "data": {"outputs": []}},
            )
        return HasturExecuteResult(
            success=True,
            message="Hastur skill code executed.",
            gdscript=code,
            broker_response={"success": True, "data": {"outputs": [["scene_tree", "Main\n  Camera2D"]]}},
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "list the main scene tree", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert apply_calls["count"] == 2
    assert "Main\\n  Camera2D" in joined
    assert '"type": "final", "state": "complete", "message": "Main\\n  Camera2D"' in joined


def test_hastur_task_fails_without_fake_success_when_repairs_have_no_output(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Reading."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return '{"mode":"plan","summary":"Read main scene tree","read_only":true,"steps":[{"title":"Read tree","goal":"Return the current scene tree"}],"final":"Repeated plan text"}'
            return '{"code":"print(\\"still no output\\")"}'

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(
        hastur_task_service,
        "apply_hastur_code",
        lambda _slug, code, **_kwargs: HasturExecuteResult(
            success=True,
            message="Hastur skill code executed.",
            gdscript=code,
            broker_response={"success": True, "data": {"outputs": []}},
        ),
    )

    task = hastur_task_service.create_task("shadow-garden", "list the main scene tree", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))
    visible_messages = "\n".join(_event_messages(joined))

    assert "event: error" in joined
    assert "did not return a displayable scene tree" in visible_messages
    assert "Task completed" not in visible_messages
    assert "Hastur skill code executed" not in visible_messages


def test_hastur_task_mutation_requires_output_and_repairs(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Updating scene."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return '{"mode":"plan","summary":"Add label","read_only":false,"steps":[{"title":"Add label","goal":"Add a Label node and save the scene"}],"final":"Done"}'
            if "previous complete Hastur GDScript batch failed" in prompt:
                assert "must call executeContext.output" in prompt
                return '{"code":"executeContext.output(\\"result\\", \\"Added Label and saved Main.tscn\\")"}'
            return '{"code":"print(\\"changed but forgot output\\")"}'

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        if apply_calls["count"] == 1:
            return HasturExecuteResult(success=True, message="ok", gdscript=code, broker_response={"data": {"outputs": []}})
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "Added Label and saved Main.tscn"]]}},
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "add a label", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert apply_calls["count"] == 2
    assert '"type": "final", "state": "complete", "message": "Added Label and saved Main.tscn"' in joined


def test_direction_fix_requires_before_after_output_and_repairs(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Checking the target first."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Fix continent orientation",
                        "read_only": False,
                        "steps": [{"title": "Fix continent", "goal": "Correct the upside-down continent/map orientation"}],
                        "final": "Done",
                    }
                )
            if "previous complete Hastur GDScript batch failed" in prompt:
                assert "before/after evidence" in prompt or "Before:" in prompt
                return json.dumps({"code": 'executeContext.output("result", "Before: Continent scale.y=-1\\nAfter: Continent scale.y=1")'})
            return json.dumps({"code": 'executeContext.output("result", "Continent orientation fixed")'})

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        if apply_calls["count"] == 1:
            return HasturExecuteResult(
                success=True,
                message="ok",
                gdscript=code,
                broker_response={"data": {"outputs": [["result", "Continent orientation fixed"]]}}
            )
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "Before: Continent scale.y=-1\nAfter: Continent scale.y=1"]]}}
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task("shadow-garden", "fix upside-down continent orientation", "godot-remote-executor", confirmed=True)
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert apply_calls["count"] == 2
    assert "Before: Continent scale.y=-1" in joined
    assert "After: Continent scale.y=1" in joined


def test_mesh_surface_fix_requires_target_orientation_and_visibility_evidence(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Checking the mesh target."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                return json.dumps(
                    {
                        "mode": "plan",
                        "summary": "Fix continent material orientation",
                        "read_only": False,
                        "steps": [{"title": "Fix terrain mesh", "goal": "Fix front transparent back visible continent mesh"}],
                    }
                )
            if "previous complete Hastur GDScript batch failed" in prompt:
                assert "top_visible=true" in prompt
                assert "intended target node path" in prompt
                return json.dumps(
                    {
                        "code": (
                            'executeContext.output("result", '
                            '"Before: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=-1.00 top_visible=false\\n'
                            'After: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true")'
                        )
                    }
                )
            return json.dumps({"code": 'executeContext.output("result", "Continent mesh fixed")'})

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        if apply_calls["count"] == 1:
            return HasturExecuteResult(
                success=True,
                message="ok",
                gdscript=code,
                broker_response={
                    "data": {
                        "outputs": [
                            [
                                "result",
                                (
                                    "Before:\n"
                                    "path=/GeneratedContent/Forest/Tree_30_Leaves surf=1 normY=-0.37 cull=BACK alpha=1.00\n"
                                    "After:\n"
                                    "path=/GeneratedContent/Forest/Tree_30_Leaves surf=1 normY=0.37 cull=BACK alpha=1.00 "
                                    "fix=rewind+opaqueCullBack saved"
                                ),
                            ]
                        ]
                    }
                },
            )
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={
                "data": {
                    "outputs": [
                        [
                            "result",
                            (
                                "Before: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=-1.00 top_visible=false\n"
                                "After: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true"
                            ),
                        ]
                    ]
                }
            },
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task(
        "shadow-garden",
        "修正大陆的材质上下颠倒，正面透明反面有材质",
        "godot-remote-executor",
        confirmed=True,
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert apply_calls["count"] == 2
    assert "did not prove the mesh surface orientation fix on the intended target" in joined
    assert "path=GeneratedContent/TerrainMesh" in joined
    assert "top_visible=true" in joined


def test_mesh_surface_fix_rejects_truncated_internal_path_and_already_visible_before(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    apply_calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Using mesh orientation skill."

        def generate_text(self, prompt, system_prompt=None):
            if "previous complete Hastur GDScript batch failed" in prompt:
                assert "truncated" in prompt.lower()
                return json.dumps(
                    {
                        "code": (
                            'executeContext.output("result", '
                            '"Before: path=GeneratedContent/TerrainMesh inst_trans=1.00 cull=BACK alpha=1.00 normal_y=1.00 top_visible=false\\n'
                            'After: path=GeneratedContent/TerrainMesh inst_trans=0.00 cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true saved=true")'
                        )
                    }
                )
            return json.dumps({"mode": "direct", "summary": "Fix mesh", "steps": [], "code": 'executeContext.output("result", "first")'})

    def fake_apply(_slug, code, **_kwargs):
        apply_calls["count"] += 1
        if apply_calls["count"] == 1:
            return HasturExecuteResult(
                success=True,
                message="ok",
                gdscript=code,
                broker_response={
                    "data": {
                        "outputs": [[
                            "result",
                            "[TRUNCATED: Output exceeded 800 char limit. Actual length: 936] Before: path=/root/@EditorNode@18065/@Panel/Main/GeneratedContinent/TerrainMesh cull=BACK alpha=1.00 normal_y=0.99 top_visible=true",
                        ]]
                    }
                },
            )
        return HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={
                "data": {
                    "outputs": [[
                        "result",
                        "Before: path=GeneratedContent/TerrainMesh inst_trans=1.00 cull=BACK alpha=1.00 normal_y=1.00 top_visible=false\nAfter: path=GeneratedContent/TerrainMesh inst_trans=0.00 cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true saved=true",
                    ]]
                }
            },
        )

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_task_service, "apply_hastur_code", fake_apply)

    task = hastur_task_service.create_task(
        "shadow-garden",
        "修复大陆材质正面透明反面有材质",
        "godot-remote-executor",
        confirmed=True,
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert apply_calls["count"] == 2
    assert "output was truncated" in joined
    assert "inst_trans=0.00" in joined
    assert "top_visible=true" in joined


def test_context_requests_load_small_doc_snippets_on_demand(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Checking docs."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if calls["count"] == 1:
                assert "Godot docs index" in prompt
                assert "Nodes are the fundamental building blocks" not in prompt
                return json.dumps({"context_requests": [{"type": "godot_doc", "path": "godot-docs/getting_started/step_by_step/nodes_and_scenes.rst.txt", "query": "fundamental building blocks"}]})
            assert "Nodes are the fundamental building blocks" in prompt
            return json.dumps(
                {
                    "mode": "direct",
                    "summary": "Read docs",
                    "steps": [],
                    "code": 'executeContext.output("result", "ok")',
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
            broker_response={"data": {"outputs": [["result", "ok"]]}},
        ),
    )

    task = hastur_task_service.create_task("shadow-garden", "use docs", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert calls["count"] == 2
    assert "event: final" in joined


def test_context_requests_dedupe_repeated_doc_snippets(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Checking docs."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if calls["count"] == 1:
                request = {"type": "godot_doc", "path": "godot-docs/getting_started/step_by_step/nodes_and_scenes.rst.txt", "query": "fundamental building blocks"}
                return json.dumps({"context_requests": [request, request]})
            assert prompt.count("Nodes are the fundamental building blocks") == 1
            return json.dumps({"mode": "direct", "summary": "ok", "steps": [], "code": 'executeContext.output("result", "ok")'})

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(
        hastur_task_service,
        "apply_hastur_code",
        lambda _slug, code, **_kwargs: HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "ok"]]}}
        ),
    )

    task = hastur_task_service.create_task("shadow-garden", "use docs", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert calls["count"] == 2
    assert "event: final" in joined


def test_task_image_attachments_are_summarized_with_vision_provider(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    seen = {"vision": 0, "summary_in_prompt": False}

    class FakeLLM:
        supports_images = True

        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Using the uploaded screenshot."

        def generate_text_with_images(self, prompt, images, system_prompt=None):
            seen["vision"] += 1
            assert images[0]["media_type"] == "image/png"
            return "Screenshot shows ContinentTerrain selected; front face is transparent and back face has material."

        def generate_text(self, prompt, system_prompt=None):
            if "creating an execution decision" in prompt:
                seen["summary_in_prompt"] = "front face is transparent" in prompt
                return json.dumps({"mode": "direct", "summary": "Fix material", "code": 'executeContext.output("result", "Before: front transparent\\nAfter: front visible")'})
            raise AssertionError(prompt)

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(
        hastur_task_service,
        "apply_hastur_code",
        lambda _slug, code, **_kwargs: HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "Before: front transparent\nAfter: front visible"]]}}
        ),
    )

    task = hastur_task_service.create_task(
        "shadow-garden",
        "fix the continent material",
        "godot-remote-executor",
        attachments=[{"filename": "shot.png", "media_type": "image/png", "data": "AAAA"}],
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert seen == {"vision": 1, "summary_in_prompt": True}
    assert "Before: front transparent" in joined


def test_auto_skill_detection_respects_manual_only_and_paths(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    skills_root = tmp_path / "skills"
    manual = skills_root / "manual-skill"
    manual.mkdir()
    (manual / "SKILL.md").write_text(
        "---\nname: manual-skill\ndescription: terrain material helper\ndisable-model-invocation: true\n---\n\nBody",
        encoding="utf-8",
    )
    path_skill = skills_root / "path-skill"
    path_skill.mkdir()
    (path_skill / "SKILL.md").write_text(
        "---\nname: path-skill\ndescription: terrain material helper\npaths: [scenes/Main.tscn]\n---\n\nBody",
        encoding="utf-8",
    )

    assert hastur_task_service.detect_skill("use terrain material helper", "shadow-garden") == "godot-remote-executor"
    assert hastur_task_service.detect_skill("use terrain material helper in scenes/Main.tscn", "shadow-garden") == "path-skill"
    listing = hastur_skill_service.skill_listing_for_prompt("shadow-garden")
    assert "manual-skill" not in listing
    assert "path-skill" in listing


def test_auto_detected_skill_loads_full_body_and_announces_invocation(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    marker = "AUTO FULL BODY SHOULD APPEAR"
    path_skill = tmp_path / "skills" / "path-skill"
    path_skill.mkdir()
    (path_skill / "SKILL.md").write_text(
        "---\n"
        "name: path-skill\n"
        "description: terrain material helper\n"
        "paths: [scenes/Main.tscn]\n"
        "---\n\n"
        f"{marker}",
        encoding="utf-8",
    )

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Using the matching skill."

        def generate_text(self, prompt, system_prompt=None):
            if "Reply to the user" in prompt:
                return "Using the matching skill."
            assert "path-skill" in prompt
            assert marker in prompt
            if "Generate ONE complete GDScript" in prompt:
                return json.dumps({"code": 'executeContext.output("result", "ok")'})
            return json.dumps(
                {
                    "mode": "direct",
                    "summary": "Use path skill",
                    "steps": [],
                    "code": 'executeContext.output("result", "ok")',
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
            broker_response={"data": {"outputs": [["result", "ok"]]}}
        ),
    )

    task = hastur_task_service.create_task(
        "shadow-garden",
        "use terrain material helper in scenes/Main.tscn",
        None,
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert task["skill_name"] == "path-skill"
    assert "Invoked Claude Code skill: /path-skill" in joined
    assert "event: final" in joined


def test_disable_model_invocation_skill_body_loads_on_context_request(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    marker = "REQUESTED FULL BODY SHOULD APPEAR"
    path_skill = tmp_path / "skills" / "path-skill"
    path_skill.mkdir()
    (path_skill / "SKILL.md").write_text(
        "---\n"
            "name: path-skill\n"
            "description: terrain material helper\n"
            "disable-model-invocation: true\n"
            "paths: [scenes/Main.tscn]\n"
        "---\n\n"
        f"{marker}",
        encoding="utf-8",
    )
    calls = {"count": 0}

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            assert marker not in prompt
            yield "Requesting targeted context."

        def generate_text(self, prompt, system_prompt=None):
            calls["count"] += 1
            if calls["count"] == 1:
                assert marker not in prompt
                return json.dumps({"context_requests": [{"type": "skill", "name": "path-skill"}]})
            if "creating an execution decision" in prompt:
                assert marker in prompt
                return json.dumps(
                    {
                        "mode": "direct",
                        "summary": "Use requested skill body",
                        "steps": [],
                        "code": 'executeContext.output("result", "ok")',
                    }
                )
            return json.dumps({"code": 'executeContext.output("result", "ok")'})

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(
        hastur_task_service,
        "apply_hastur_code",
        lambda _slug, code, **_kwargs: HasturExecuteResult(
            success=True,
            message="ok",
            gdscript=code,
            broker_response={"data": {"outputs": [["result", "ok"]]}}
        ),
    )

    task = hastur_task_service.create_task(
        "shadow-garden",
        "use terrain material helper in scenes/Main.tscn",
        None,
    )
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert calls["count"] == 2
    assert "event: final" in joined


def test_skill_body_invocation_is_visible_in_work_log(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    skill_dir = tmp_path / "skills" / "direct-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: direct-skill\ndescription: Directly invoked helper\n---\n\nUse direct skill body.",
        encoding="utf-8",
    )

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning with skill."

        def generate_text(self, prompt, system_prompt=None):
            assert "Use direct skill body" in prompt
            return json.dumps({"mode": "direct", "summary": "Use skill", "steps": [], "code": 'executeContext.output("result", "ok")'})

    monkeypatch.setattr(hastur_task_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(
        hastur_task_service,
        "apply_hastur_code",
        lambda _slug, code, **_kwargs: HasturExecuteResult(success=True, message="ok", gdscript=code, broker_response={"data": {"outputs": [["result", "ok"]]}}),
    )

    task = hastur_task_service.create_task("shadow-garden", "/direct-skill run this", "direct-skill")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Invoked Claude Code skill: /direct-skill" in joined
    assert '"kind": "skill"' in joined


def test_auto_invoked_standard_skill_is_visible_for_mesh_surface_issue(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    skill_dir = tmp_path / "skills" / "mesh-surface-orientation-fix"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: mesh-surface-orientation-fix\n"
        "description: Fix continent terrain mesh material front transparent back visible 大陆 材质 正面 透明 反面\n"
        "when_to_use: Use for 大陆的材质上下颠倒 正面看是透明的 反面有材质\n"
        "---\n\n"
        "Skill body: inspect target path, cull, alpha, normal_y, winding, and top_visible=true.",
        encoding="utf-8",
    )

    class FakeLLM:
        def generate_text_stream(self, prompt, system_prompt=None):
            yield "Planning mesh fix."

        def generate_text(self, prompt, system_prompt=None):
            assert "Skill body: inspect target path" in prompt
            return json.dumps(
                {
                    "mode": "direct",
                    "summary": "Fix mesh surface material",
                    "steps": [],
                    "code": (
                        'executeContext.output("result", '
                        '"Before: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=-1.00 top_visible=false\\n'
                        'After: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true")'
                    ),
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
            broker_response={
                "data": {
                    "outputs": [[
                        "result",
                        "Before: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=-1.00 top_visible=false\nAfter: path=GeneratedContent/TerrainMesh cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true",
                    ]]
                }
            },
        ),
    )

    task = hastur_task_service.create_task("shadow-garden", "修复大陆材质正面透明反面有材质", "godot-remote-executor")
    joined = "".join(hastur_task_service.stream_task_events(task["task_id"]))

    assert "Invoked Claude Code skill: /mesh-surface-orientation-fix" in joined
    assert '"kind": "skill"' in joined


def test_visual_clarity_guidance_is_in_planning_codegen_and_repair_prompts(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    session = hastur_task_service.HasturTaskSession(
        task_id="task",
        project_slug="shadow-garden",
        instruction="improve post processing and lighting clarity",
        skill_name="godot-remote-executor",
    )
    docs = hastur_task_service._load_godot_docs()
    plan = {
        "mode": "plan",
        "complexity": "simple",
        "execution_strategy": "single_batch",
        "summary": "Improve visibility",
        "steps": [{"title": "Adjust clarity", "goal": "Make the preview clear"}],
        "task_breakdown": [{"id": "task_1", "title": "Adjust clarity", "goal": "Make the preview clear"}],
    }

    planning_prompt = hastur_task_service._task_prompt(session, tmp_path, docs, "", {}, [])
    code_prompt = hastur_task_service._batch_code_prompt(session, tmp_path, docs, "", {}, plan)
    repair_prompt = hastur_task_service._batch_repair_prompt(
        session,
        tmp_path,
        docs,
        "",
        {},
        plan,
        [{"success": False, "message": "too dark", "broker_response": {}}],
        1,
    )

    for prompt in (planning_prompt, code_prompt, repair_prompt):
        assert "prioritize a clear editor/game preview" in prompt
        assert "dof_blur_near_enabled=false" in prompt
        assert "volumetric fog" in prompt
        assert "keep executeContext.output under 700 characters" in prompt


def test_mesh_surface_orientation_guardrail_is_in_core_prompts(tmp_path, monkeypatch):
    _setup_project(tmp_path, monkeypatch)
    session = hastur_task_service.HasturTaskSession(
        task_id="task",
        project_slug="shadow-garden",
        instruction="continent front is transparent, back side has material, fix upside-down terrain material",
        skill_name="godot-remote-executor",
    )
    docs = hastur_task_service._load_godot_docs()
    plan = {
        "mode": "plan",
        "complexity": "simple",
        "execution_strategy": "single_batch",
        "summary": "Fix terrain surface orientation",
        "steps": [{"title": "Fix winding", "goal": "Make terrain top visible"}],
        "task_breakdown": [{"id": "task_1", "title": "Fix winding", "goal": "Make terrain top visible"}],
    }

    planning_prompt = hastur_task_service._task_prompt(session, tmp_path, docs, "", {}, [])
    code_prompt = hastur_task_service._batch_code_prompt(session, tmp_path, docs, "", {}, plan)
    repair_prompt = hastur_task_service._batch_repair_prompt(
        session,
        tmp_path,
        docs,
        "",
        {},
        plan,
        [{"success": False, "message": "front transparent", "broker_response": {}}],
        1,
    )

    for prompt in (planning_prompt, code_prompt, repair_prompt):
        assert "Mesh surface orientation rule" in prompt
        assert "Godot ArrayMesh triangle front faces use clockwise winding" in prompt
        assert "positive Y" in prompt
        assert "Do not use CULL_DISABLED/two-sided material as the only fix" in prompt
        assert "top_visible=true" in prompt
        assert "Do not fix an incidental tree" in prompt


def test_capability_registry_does_not_define_nonstandard_skills():
    registry = hastur_task_service._capability_registry_text()

    assert "built_in_guardrails" not in registry
    assert "built_in_default_skills" not in registry


def test_public_thought_sanitizer_blocks_code_and_payloads():
    assert hastur_task_service._sanitize_public_thought('{"code":"executeContext.output(\\"result\\", \\"x\\")"}') == ""
    assert hastur_task_service._sanitize_public_thought("```gdscript\nfunc _ready():\n\tpass\n```") == ""
    assert hastur_task_service._sanitize_public_thought("func _ready():\n\tpass") == ""
    assert hastur_task_service._sanitize_public_thought("I will inspect the target node first.") == "I will inspect the target node first."


def test_extract_repair_code_from_steps_and_bare_gdscript():
    assert hastur_task_service._extract_executable_code({"steps": [{"code": "if true:\n\tprint(\"ok\")"}]}) == 'if true:\n\tprint("ok")'
    assert hastur_task_service._extract_executable_code({}, 'extends RefCounted\n\nfunc execute(executeContext):\n\texecuteContext.output("ok", "1")').startswith("extends RefCounted")
    assert hastur_task_service._extract_executable_code({}, 'executeContext.output("result", "1")') == 'executeContext.output("result", "1")'
