from __future__ import annotations

from dataclasses import dataclass, field
import base64
import json
import queue
import re
import threading
import time
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from app.config import PROJECT_ROOT
from app.models.llm_provider import get_llm_provider
from app.services.asset_service import get_project_dir
from app.services.hastur_chat_service import (
    _execution_readiness,
    _parse_response,
    _public_attachment_list,
    encode_upload,
)
from app.services.hastur_service import apply_hastur_code, hastur_executors
from app.services.hastur_skill_service import list_hastur_skills, load_hastur_skill
from app.services.settings_service import load_private_settings


TASK_STATES = {
    "intake",
    "context",
    "planning",
    "awaiting_user",
    "executing",
    "repairing",
    "visual_review",
    "verifying",
    "complete",
    "failed",
}

MAX_REPAIR_ATTEMPTS = 2
DEFAULT_SKILL_NAME = "godot-remote-executor"

GODOT_DOCS = [
    "godot-docs/tutorials/plugins/editor/installing_plugins.rst.txt",
    "godot-docs/tutorials/plugins/editor/making_plugins.rst.txt",
    "godot-docs/tutorials/best_practices/project_organization.rst.txt",
    "godot-docs/getting_started/step_by_step/nodes_and_scenes.rst.txt",
    "godot-docs/tutorials/rendering/viewports.rst.txt",
    "godot-docs/classes/class_editorinterface.rst.txt",
    "godot-docs/tutorials/3d/environment_and_post_processing.rst.txt",
]


@dataclass
class HasturTaskSession:
    task_id: str
    project_slug: str
    instruction: str
    skill_name: str
    attachments: list[dict[str, str]] = field(default_factory=list)
    confirmed: bool = False
    answer: str = ""
    choice_id: str = ""
    revision_request: str = ""
    skill_explicit: bool = False
    skill_confirmed: bool = False
    state: str = "intake"
    events: list[dict[str, Any]] = field(default_factory=list)
    event_queue: queue.Queue[dict[str, Any] | None] = field(default_factory=queue.Queue)
    started: bool = False
    completed: bool = False
    pending: str = ""
    pending_step_index: int | None = None
    plan: dict[str, Any] | None = None
    next_step_index: int = 0
    prior_results: list[dict[str, Any]] = field(default_factory=list)
    visual_acknowledged: set[int] = field(default_factory=set)
    visual_adjustments: dict[int, dict[str, str]] = field(default_factory=dict)
    visual_adjustments_applied: set[int] = field(default_factory=set)
    pending_prompt: dict[str, Any] = field(default_factory=dict)


_SESSIONS: dict[str, HasturTaskSession] = {}
_LOCK = threading.Lock()


def create_task(
    project_slug: str,
    instruction: str,
    skill_name: str | None = None,
    attachments: list[dict[str, str]] | None = None,
    confirmed: bool = False,
) -> dict[str, Any]:
    project_dir = get_project_dir(project_slug)
    explicit = _instruction_has_skill_prefix(instruction)
    selected_skill = skill_name if explicit and skill_name else detect_skill(instruction)
    session = HasturTaskSession(
        task_id=uuid4().hex,
        project_slug=project_slug,
        instruction=instruction,
        skill_name=selected_skill,
        attachments=attachments or [],
        confirmed=confirmed,
        skill_explicit=explicit,
        skill_confirmed=explicit or selected_skill == _default_skill_name(),
    )
    with _LOCK:
        _SESSIONS[session.task_id] = session
    return {
        "success": True,
        "task_id": session.task_id,
        "state": session.state,
        "project_slug": project_slug,
        "project_path": str(project_dir),
        "skill_name": selected_skill,
    }


def resume_task(
    task_id: str,
    answer: str = "",
    confirmed: bool = False,
    choice_id: str = "",
    revision_request: str = "",
) -> dict[str, Any]:
    session = get_task(task_id)
    session.answer = answer.strip()
    session.choice_id = choice_id.strip()
    session.revision_request = revision_request.strip()
    if confirmed:
        session.confirmed = True

    if session.pending == "skill_confirmation":
        _resume_skill_confirmation(session)
    elif session.pending in {"choice_request", "user_prompt"}:
        session.plan = None
        session.confirmed = False
        session.next_step_index = 0
        session.prior_results = []
        if session.choice_id:
            session.answer = "\n".join(filter(None, [session.answer, f"Selected option: {session.choice_id}"]))
    elif session.pending == "plan_review":
        if session.choice_id in {"confirm_plan", "confirm", "continue", "execute"} or confirmed:
            session.confirmed = True
        elif session.answer and not session.revision_request:
            session.revision_request = session.answer
        elif session.choice_id:
            session.revision_request = f"Selected option: {session.choice_id}"
        if session.revision_request:
            session.plan = None
            session.confirmed = False
            session.next_step_index = 0
            session.prior_results = []
            session.answer = "\n".join(filter(None, [session.answer, f"Plan revision request: {session.revision_request}"]))
    elif session.pending == "visual_checkpoint" and session.pending_step_index is not None:
        _resume_visual_checkpoint(session)

    session.pending = ""
    session.pending_step_index = None
    session.pending_prompt = {}
    session.started = False
    session.completed = False
    session.events = []
    session.event_queue = queue.Queue()
    session.state = "context"
    return {"success": True, "task_id": task_id, "state": session.state}


def get_task(task_id: str) -> HasturTaskSession:
    with _LOCK:
        session = _SESSIONS.get(task_id)
    if not session:
        raise FileNotFoundError(f"Hastur task not found: {task_id}")
    return session


def stream_task_events(task_id: str) -> Iterator[str]:
    session = get_task(task_id)
    history = list(session.events)
    if not session.started:
        session.started = True
        threading.Thread(target=_run_task, args=(session,), daemon=True).start()
    for event in history:
        yield _sse(event)
    if session.completed:
        return
    while True:
        item = session.event_queue.get()
        if item is None:
            break
        yield _sse(item)


def detect_skill(instruction: str) -> str:
    first = instruction.strip().split(maxsplit=1)[0] if instruction.strip() else ""
    skills = list_hastur_skills()
    names = {skill.name for skill in skills}
    if first.startswith("/") and first[1:] in names:
        return first[1:]
    lower = instruction.lower()
    for skill in skills:
        haystack = f"{skill.name} {skill.description}".lower()
        if skill.name == _default_skill_name():
            continue
        if any(word in haystack for word in re.findall(r"[a-zA-Z][a-zA-Z_-]{3,}", lower)):
            return skill.name
    return _default_skill_name()


def _run_task(session: HasturTaskSession) -> None:
    try:
        project_dir = get_project_dir(session.project_slug)
        docs = _load_godot_docs()
        executors = hastur_executors()
        _emit_activity(
            session,
            "context",
            "context",
            "Loaded project context, Godot docs, and vendored Hastur skill.",
            {
                "project_path": str(project_dir),
                "docs": [item["path"] for item in docs],
                "skill": session.skill_name,
                "attachments": _public_attachment_list(session.attachments),
            },
        )

        readiness = _execution_readiness(load_private_settings(), executors)
        if readiness:
            _emit(session, "error", "failed", readiness, {"executors": executors})
            return

        skill_text = load_hastur_skill(session.skill_name)
        if session.plan is None:
            _stream_planning_text(session, project_dir, docs, skill_text, executors)
            session.plan = _plan_task(session, project_dir, docs, skill_text, executors)
            session.next_step_index = 0
            session.prior_results = []
            session.visual_acknowledged.clear()
            session.visual_adjustments.clear()
            session.visual_adjustments_applied.clear()

        plan = _normalize_plan(session.plan)
        session.plan = plan

        if plan.get("user_prompt") and not (session.answer or session.choice_id):
            _emit_generic_user_prompt(session, plan["user_prompt"], plan)
            return

        if plan.get("question") and not session.answer:
            _emit_choice_request(session, str(plan["question"]), plan)
            return

        choices = plan.get("choices") if isinstance(plan.get("choices"), list) else []
        if choices and not session.choice_id:
            _emit_choice_request(session, str(plan.get("summary") or "Choose how to proceed."), plan)
            return

        if _plan_requires_review(session, plan) and not session.confirmed:
            _emit_safety_prompt(session, plan)
            return

        _apply_pending_visual_adjustments(session, project_dir, docs, skill_text, executors, plan)
        completed = _execute_plan(session, project_dir, docs, skill_text, executors, plan)
        if completed:
            _emit_activity(session, "verification", "verifying", "Checked broker/executor state after execution.", {"executors": hastur_executors()})
            final = str(plan.get("final") or "Task completed. Review local Git changes manually from the Git workbench.")
            _emit(session, "final", "complete", final, {"results": session.prior_results, "summary": final})
    except Exception as exc:
        _emit(session, "error", "failed", str(exc))
    finally:
        _finish(session)


def _stream_planning_text(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> None:
    llm = get_llm_provider()
    prompt = _planning_chat_prompt(session, project_dir, docs, skill_text, executors)
    stream = getattr(llm, "generate_text_stream", None)
    if callable(stream):
        for chunk in stream(prompt, system_prompt=_planning_chat_system_prompt()):
            _emit_thought_delta(session, str(chunk))
        return
    text = llm.generate_text(prompt, system_prompt=_planning_chat_system_prompt())
    _emit_thought_delta(session, text)


def _plan_task(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> dict[str, Any]:
    prompt = _task_prompt(session, project_dir, docs, skill_text, executors)
    raw = get_llm_provider().generate_text(prompt, system_prompt=_task_system_prompt())
    parsed = _parse_response(raw)
    return _normalize_plan(parsed)


def _execute_plan(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
) -> bool:
    steps = plan.get("steps") or []
    if not steps:
        return True

    for index in range(session.next_step_index, len(steps)):
        step = steps[index]
        title = str(step.get("title") or f"Step {index + 1}")
        _emit_activity(session, "execution", "executing", f"Preparing step {index + 1}/{len(steps)}: {title}", {"step": _public_step(step, index)})
        code = _generate_step_code(session, project_dir, docs, skill_text, executors, plan, step, index)
        if not code:
            payload = {"success": True, "message": "No Hastur execution needed for this step.", "step": title}
            session.prior_results.append(payload)
            _emit(session, "step_result", "executing", payload["message"], {"index": index + 1, "step": _public_step(step, index), "result": payload})
            session.next_step_index = index + 1
        else:
            result = apply_hastur_code(
                session.project_slug,
                code,
                executor_id=step.get("executor_id") or None,
                executor_type=step.get("type") or None,
            )
            payload = result.model_dump()
            session.prior_results.append(payload)
            _emit(session, "step_result", "executing", result.message, {"index": index + 1, "step": _public_step(step, index), "result": payload})
            if not result.success:
                repaired = _repair_failed_step(session, project_dir, docs, skill_text, executors, plan, step, session.prior_results, title)
                if not repaired:
                    _emit(
                        session,
                        "error",
                        "failed",
                        "Hastur execution failed and could not be repaired.",
                        {"step": title, "results": session.prior_results},
                    )
                    return False
            session.next_step_index = index + 1

        if _needs_visual_check(step, title) and index not in session.visual_acknowledged:
            checkpoint = _capture_visual_checkpoint(session, project_dir, title)
            checkpoint["analysis"] = _analyze_visual_checkpoint(checkpoint, project_dir)
            prompt = _build_visual_checkpoint_user_prompt(session, project_dir, docs, skill_text, executors, plan, step, checkpoint, index)
            _emit_visual_checkpoint(session, index, step, checkpoint, prompt)
            return False

    return True


def _generate_step_code(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    step: dict[str, Any],
    index: int,
) -> str:
    prompt = _step_code_prompt(session, project_dir, docs, skill_text, executors, plan, step, index)
    raw = get_llm_provider().generate_text(prompt, system_prompt=_step_code_system_prompt())
    parsed = _parse_response(raw)
    return _extract_executable_code(parsed, raw)


def _repair_step(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    failed_step: dict[str, Any],
    prior_results: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = _step_code_prompt(session, project_dir, docs, skill_text, executors, plan, failed_step, session.next_step_index)
    prompt += "\n\nThe previous GDScript failed. Return JSON with one corrected `code` string, or empty code if no repair is safe.\n"
    prompt += "The repair must be small, idempotent, tab-indented GDScript with no Markdown fences.\n"
    prompt += json.dumps({"failed_step": failed_step, "prior_results": prior_results[-3:]}, ensure_ascii=False)
    raw = get_llm_provider().generate_text(prompt, system_prompt=_step_code_system_prompt())
    parsed = _parse_response(raw)
    code = _extract_executable_code(parsed, raw)
    if code:
        parsed["code"] = code
    return parsed


def _repair_failed_step(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    failed_step: dict[str, Any],
    prior_results: list[dict[str, Any]],
    title: str,
) -> bool:
    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        _emit_activity(
            session,
            "repair",
            "repairing",
            f"Repairing failed GDScript, attempt {attempt}/{MAX_REPAIR_ATTEMPTS}.",
            {"step": title, "last_result": prior_results[-1]},
        )
        repaired = _repair_step(session, project_dir, docs, skill_text, executors, plan, failed_step, prior_results)
        repair_code = _extract_executable_code(repaired)
        if not repair_code:
            prior_results.append({"success": False, "message": "Repair response did not include executable GDScript."})
            continue
        repair_result = apply_hastur_code(
            session.project_slug,
            repair_code,
            executor_id=failed_step.get("executor_id") or None,
            executor_type=failed_step.get("type") or None,
        )
        payload = repair_result.model_dump()
        prior_results.append(payload)
        _emit(session, "step_result", "repairing", repair_result.message, {"step": f"{title} repair", "result": payload})
        if repair_result.success:
            return True
    return False


def _apply_pending_visual_adjustments(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
) -> None:
    steps = plan.get("steps") or []
    for index, adjustment in sorted(session.visual_adjustments.items()):
        if index in session.visual_adjustments_applied or index >= len(steps):
            continue
        step = steps[index]
        prompt = _visual_adjustment_prompt(session, project_dir, docs, skill_text, executors, plan, step, adjustment)
        raw = get_llm_provider().generate_text(prompt, system_prompt=_step_code_system_prompt())
        code = _extract_executable_code(_parse_response(raw), raw)
        if not code:
            session.visual_adjustments_applied.add(index)
            continue
        _emit_activity(session, "visual_adjustment", "executing", f"Applying visual adjustment after {step.get('title') or 'step'}.", adjustment)
        result = apply_hastur_code(session.project_slug, code, executor_id=step.get("executor_id") or None, executor_type=step.get("type") or None)
        payload = result.model_dump()
        session.prior_results.append(payload)
        _emit(session, "step_result", "executing", result.message, {"step": "visual adjustment", "result": payload})
        session.visual_adjustments_applied.add(index)


def _capture_visual_checkpoint(session: HasturTaskSession, project_dir: Path, title: str) -> dict[str, Any]:
    filename = f"checkpoint_{int(time.time())}_{uuid4().hex[:8]}.png"
    rel_path = f"assets/generated/visual_checkpoints/{filename}"
    res_path = f"res://{rel_path}"
    code = "\n".join(
        [
            "var viewport := EditorInterface.get_editor_viewport_3d(0)",
            "if viewport == null:",
            "\tviewport = EditorInterface.get_editor_viewport_2d()",
            "if viewport == null:",
            "\tpush_error(\"No editor viewport is available for visual checkpoint capture.\")",
            "else:",
            "\tvar image := viewport.get_texture().get_image()",
            "\tif image == null or image.is_empty():",
            "\t\tpush_error(\"Editor viewport screenshot is empty.\")",
            "\telse:",
            "\t\tvar dir_path := ProjectSettings.globalize_path(\"res://assets/generated/visual_checkpoints\")",
            "\t\tDirAccess.make_dir_recursive_absolute(dir_path)",
            f"\t\tvar image_path := {json.dumps(res_path)}",
            "\t\tvar save_error := image.save_png(ProjectSettings.globalize_path(image_path))",
            "\t\tif save_error != OK:",
            "\t\t\tpush_error(\"Could not save visual checkpoint: \" + error_string(save_error))",
            "\t\telse:",
            "\t\t\texecuteContext.output(\"image_path\", image_path)",
        ]
    )
    result = apply_hastur_code(session.project_slug, code, executor_type="editor")
    payload = result.model_dump()
    output_path = _extract_output_value(payload.get("broker_response"), "image_path") or res_path
    filename_from_output = Path(str(output_path).replace("res://", "")).name
    absolute = project_dir / "assets" / "generated" / "visual_checkpoints" / filename_from_output
    return {
        "success": result.success,
        "title": title,
        "image_path": str(output_path),
        "image_url": f"/api/projects/{session.project_slug}/visual-checkpoints/{filename_from_output}",
        "absolute_path": str(absolute),
        "result": payload,
    }


def _analyze_visual_checkpoint(checkpoint: dict[str, Any], project_dir: Path) -> str:
    path = Path(checkpoint.get("absolute_path") or "")
    if not path.exists():
        return "No screenshot was available for automatic visual analysis."
    llm = get_llm_provider()
    if not getattr(llm, "supports_images", False) or not hasattr(llm, "generate_text_with_images"):
        return "The current LLM provider does not support image input, so visual tuning needs manual confirmation."
    image = {
        "filename": path.name,
        "media_type": "image/png",
        "data": base64.b64encode(path.read_bytes()).decode("ascii"),
    }
    prompt = (
        "Analyze this Godot editor viewport checkpoint for lighting/post-processing balance. "
        "Mention overexposure, low contrast, darkness, and whether the current result should be kept. "
        "Return a concise user-facing recommendation."
    )
    return llm.generate_text_with_images(prompt, [image], system_prompt="You are a practical Godot visual review assistant.")


def _build_visual_checkpoint_user_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    step: dict[str, Any],
    checkpoint: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    prompt = f"""
Create the user-facing confirmation prompt for a Godot visual checkpoint.
The prompt must be concise and must not expose GDScript, raw broker payloads, or hidden reasoning.
You decide whether the user should simply continue, provide feedback, or choose from specific options.
Use only choices that are meaningful for this checkpoint.

User request: {session.instruction}
Project path: {project_dir}
Current step: {json.dumps(_public_step(step, index), ensure_ascii=False)}
Checkpoint analysis: {checkpoint.get("analysis", "")}
Checkpoint metadata: {json.dumps({k: v for k, v in checkpoint.items() if k not in {"result"}}, ensure_ascii=False)}
Plan: {json.dumps(_public_plan(plan), ensure_ascii=False)}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
Docs: {_docs_summary(docs)}
Vendored skill excerpt: {skill_text[:4000]}

Return JSON only:
{{
  "title": "short modal title",
  "body": "what the user is confirming or deciding",
  "input_label": "optional label for freeform feedback",
  "choices": [
    {{"id": "continue", "label": "Continue", "description": "when to choose it", "action": "continue"}},
    {{"id": "adjust_example", "label": "Adjust ...", "description": "what will change", "action": "adjust"}}
  ]
}}

Use action "continue" only for choices that accept the current visual result. Use action "adjust" for choices that require another LLM-generated adjustment.
""".strip()
    try:
        raw = get_llm_provider().generate_text(prompt, system_prompt="You write concise user confirmation prompts as JSON only.")
        parsed = _parse_response(raw)
    except Exception:
        parsed = {}
    choices = [_normalize_choice(choice, choice_index) for choice_index, choice in enumerate(parsed.get("choices") if isinstance(parsed.get("choices"), list) else [])]
    return {
        "title": str(parsed.get("title") or "Visual review"),
        "body": str(parsed.get("body") or checkpoint.get("analysis") or "Review the visual checkpoint before continuing."),
        "input_label": str(parsed.get("input_label") or "Feedback"),
        "choices": choices,
    }


def _extract_executable_code(parsed: dict[str, Any], raw: str = "") -> str:
    code = str(parsed.get("code") or "").strip()
    if code:
        return code
    steps = parsed.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, dict) and str(step.get("code") or "").strip():
                return str(step["code"]).strip()
    message = str(parsed.get("message") or "")
    fenced = re.search(r"```(?:gdscript|gd|gds|text)?\s*(.*?)```", message or raw, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    candidate = (raw or message).strip()
    if _looks_like_gdscript(candidate):
        return candidate
    return ""


def _looks_like_gdscript(text: str) -> bool:
    if not text:
        return False
    first = text.lstrip().splitlines()[0].strip()
    return first.startswith(("extends ", "@tool", "func ", "var ", "if ", "for ", "EditorInterface.", "ProjectSettings."))


def _planning_chat_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> str:
    return f"""
User request:
{session.instruction}

Project slug: {session.project_slug}
Project path: {project_dir}
Selected Hastur skill: {session.skill_name}
Uploaded files: {json.dumps(_public_attachment_list(session.attachments), ensure_ascii=False)}
Connected executors: {json.dumps(executors, ensure_ascii=False)}

Relevant local Godot docs:
{_docs_summary(docs)}

Vendored skill excerpt:
{skill_text[:4000]}

Reply to the user in natural language. Be concise. Explain that you will decompose the request into small executable Godot steps and ask for confirmation when needed. Do not include JSON, GDScript, or fake execution results.
""".strip()


def _planning_chat_system_prompt() -> str:
    return "You are the LLM side of a Godot/Hastur agent. Stream natural user-facing text only."


def _task_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> str:
    answer = f"\nUser answer/selection context:\n{session.answer}\n" if session.answer else ""
    return f"""
You are creating an execution plan for a local Godot project controlled through Hastur.
Use local Godot docs and the vendored Hastur skill as constraints.
Do not write GDScript in this planning response. Plan only small atomic goals.
Complex scene-building tasks must be decomposed into the smallest reasonable steps.
Prefer conservative lighting/post-processing defaults: avoid overexposure, avoid high glow, prefer ACES/AgX/Filmic style tonemapping with controlled exposure/white values when applicable.
Do not ask the user to confirm routine multi-step work. Proceed when you can safely infer the intent.
Only include user_prompt when you need user input to proceed safely, when choices materially change the result, or when a safety-sensitive operation needs explicit confirmation.
Only set needs_visual_check true when you decide a screenshot review is necessary before continuing.

Project slug: {session.project_slug}
Project path: {project_dir}
Selected Hastur skill: {session.skill_name}
Uploaded files: {json.dumps(_public_attachment_list(session.attachments), ensure_ascii=False)}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
{answer}

Godot docs context:
{_docs_context(docs)}

Vendored skill:
{skill_text[:20000]}

User request:
{session.instruction}

Return JSON only:
{{
  "summary": "short user-facing plan summary",
  "question": "",
  "requires_user_approval": false,
  "user_prompt": null,
  "choices": [
    {{"id": "option_a", "label": "short label", "description": "when to choose it"}}
  ],
  "steps": [
    {{
      "title": "atomic step title",
      "goal": "what this step changes or inspects",
      "type": "editor",
      "executor_id": "",
      "requires_confirmation": false,
      "needs_visual_check": false
    }}
  ],
  "final": "short completion summary"
}}

Set question only when information is required before planning safely.
Set requires_confirmation for delete/remove/reset/start/stop/play/autoload/rollback operations.
Keep choices empty unless the user needs to decide between materially different approaches.
If user_prompt is not null, it must be an object with title, body, optional input_label, and optional choices. User-facing choices must come from you, not from fixed defaults.
""".strip()


def _task_system_prompt() -> str:
    return "You are a Godot task planner. Output operational JSON only. Never expose secrets. Do not include GDScript."


def _step_code_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    step: dict[str, Any],
    index: int,
) -> str:
    return f"""
Generate the smallest safe GDScript snippet for one Hastur editor execution step.
Do not include unrelated work from other steps. Do not ask the user to paste code.
The snippet must be idempotent when reasonable, tab-indented, and must not use markdown fences.
Do not use reserved identifiers such as class_name as variable names.
For visual lighting/post-processing, use conservative values and avoid overexposure.
Use EditorInterface and scene/node APIs consistent with the local Godot docs.

Project path: {project_dir}
Selected skill: {session.skill_name}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
User request: {session.instruction}
User answer context: {session.answer}

Overall plan:
{json.dumps(_public_plan(plan), ensure_ascii=False)}

Current step index: {index + 1}
Current step:
{json.dumps(_public_step(step, index), ensure_ascii=False)}

Prior execution results:
{json.dumps(session.prior_results[-5:], ensure_ascii=False)}

Relevant docs:
{_docs_context(docs)}

Vendored skill excerpt:
{skill_text[:12000]}

Return JSON only:
{{"message": "brief internal summary", "code": "GDScript snippet or empty string"}}
""".strip()


def _step_code_system_prompt() -> str:
    return "You write small, repairable Godot editor GDScript for Hastur. Return JSON only."


def _visual_adjustment_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    step: dict[str, Any],
    adjustment: dict[str, str],
) -> str:
    return f"""
Generate one small GDScript adjustment after a visual checkpoint.
Only adjust lighting/post-processing/camera/material parameters related to the user's selected feedback.
Use conservative values and keep the scene usable.

Adjustment:
{json.dumps(adjustment, ensure_ascii=False)}

Step that produced the checkpoint:
{json.dumps(step, ensure_ascii=False)}

Project path: {project_dir}
Executors: {json.dumps(executors, ensure_ascii=False)}
Prior results: {json.dumps(session.prior_results[-5:], ensure_ascii=False)}
Docs: {_docs_summary(docs)}
Skill excerpt: {skill_text[:6000]}

Return JSON only:
{{"message": "brief internal summary", "code": "GDScript snippet or empty string"}}
""".strip()


def _load_godot_docs() -> list[dict[str, str]]:
    docs = []
    for rel in GODOT_DOCS:
        path = PROJECT_ROOT / rel
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        docs.append({"path": rel, "text": text[:6000]})
    return docs


def _docs_context(docs: list[dict[str, str]]) -> str:
    return "\n\n".join(f"--- {item['path']} ---\n{item['text']}" for item in docs)


def _docs_summary(docs: list[dict[str, str]]) -> str:
    return "\n".join(f"- {item['path']}: {item['text'][:500].replace(chr(10), ' ')}" for item in docs)


def _normalize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    steps = plan.get("steps")
    if not isinstance(steps, list):
        legacy_code = str(plan.get("code") or "").strip()
        steps = [{"title": plan.get("message") or "Respond", "goal": plan.get("message") or "", "type": "editor", "legacy_code": legacy_code}]
    normalized_steps = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            step = {"title": str(step), "goal": str(step)}
        normalized_steps.append(
            {
                "title": str(step.get("title") or f"Step {index + 1}"),
                "goal": str(step.get("goal") or step.get("description") or step.get("message") or step.get("title") or ""),
                "type": str(step.get("type") or "editor"),
                "executor_id": str(step.get("executor_id") or ""),
                "requires_confirmation": bool(step.get("requires_confirmation")),
                "needs_visual_check": bool(step.get("needs_visual_check")),
            }
        )
    choices = plan.get("choices") if isinstance(plan.get("choices"), list) else []
    user_prompt = plan.get("user_prompt") if isinstance(plan.get("user_prompt"), dict) else None
    return {
        "summary": str(plan.get("summary") or plan.get("message") or "Plan ready."),
        "question": str(plan.get("question") or ""),
        "requires_user_approval": bool(plan.get("requires_user_approval", False)),
        "user_prompt": _normalize_user_prompt(user_prompt) if user_prompt else None,
        "choices": [_normalize_choice(choice, index) for index, choice in enumerate(choices)],
        "steps": normalized_steps,
        "final": str(plan.get("final") or "Task completed. Review local Git changes manually from the Git workbench."),
    }


def _normalize_user_prompt(prompt: dict[str, Any]) -> dict[str, Any]:
    choices = prompt.get("choices") if isinstance(prompt.get("choices"), list) else []
    return {
        "kind": "user_prompt",
        "title": str(prompt.get("title") or "Confirmation required"),
        "body": str(prompt.get("body") or prompt.get("message") or ""),
        "input_label": str(prompt.get("input_label") or ""),
        "choices": [_normalize_choice(choice, index) for index, choice in enumerate(choices)],
    }


def _normalize_choice(choice: Any, index: int) -> dict[str, str]:
    if isinstance(choice, dict):
        return {
            "id": str(choice.get("id") or f"option_{index + 1}"),
            "label": str(choice.get("label") or choice.get("title") or f"Option {index + 1}"),
            "description": str(choice.get("description") or choice.get("details") or ""),
            "action": str(choice.get("action") or ""),
        }
    return {"id": f"option_{index + 1}", "label": str(choice), "description": "", "action": ""}


def _public_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": plan.get("summary", ""),
        "steps": [_public_step(step, index) for index, step in enumerate(plan.get("steps") or [])],
        "final": plan.get("final", ""),
    }


def _public_step(step: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index + 1,
        "title": step.get("title") or f"Step {index + 1}",
        "goal": step.get("goal") or "",
        "type": step.get("type") or "editor",
        "requires_confirmation": bool(step.get("requires_confirmation")),
        "needs_visual_check": bool(step.get("needs_visual_check")),
    }


def _plan_requires_review(session: HasturTaskSession, plan: dict[str, Any]) -> bool:
    steps = plan.get("steps") or []
    return bool(
        plan.get("requires_user_approval")
        or any(step.get("requires_confirmation") for step in steps)
    )


def _looks_like_complex_request(instruction: str) -> bool:
    text = instruction.lower()
    complex_terms = [
        " and ",
        "then",
        "village",
        "town",
        "post-processing",
        "post processing",
        "lighting",
        "environment",
        "然后",
        "并",
        "村庄",
        "城镇",
        "后期",
        "光照",
        "光线",
        "复杂",
    ]
    return any(term in text for term in complex_terms)


def _needs_visual_check(step: dict[str, Any], title: str) -> bool:
    return bool(step.get("needs_visual_check"))
    if step.get("needs_visual_check"):
        return True
    text = f"{title} {step.get('goal', '')}".lower()
    return any(term in text for term in ["light", "exposure", "glow", "fog", "camera", "post", "tonemap", "visual", "光", "曝光", "后期", "画面"])


def _instruction_has_skill_prefix(instruction: str) -> bool:
    return bool(instruction.strip().startswith("/"))


def _default_skill_name() -> str:
    names = {skill.name for skill in list_hastur_skills()}
    return DEFAULT_SKILL_NAME if DEFAULT_SKILL_NAME in names else (next(iter(names), DEFAULT_SKILL_NAME))


def _needs_skill_confirmation(session: HasturTaskSession) -> bool:
    return not session.skill_explicit and not session.skill_confirmed and session.skill_name != _default_skill_name()


def _resume_skill_confirmation(session: HasturTaskSession) -> None:
    if session.choice_id == "skip_skill":
        session.skill_name = _default_skill_name()
    session.skill_confirmed = True
    session.plan = None


def _resume_visual_checkpoint(session: HasturTaskSession) -> None:
    index = session.pending_step_index
    if index is None:
        return
    session.visual_acknowledged.add(index)
    choices = session.pending_prompt.get("choices") if isinstance(session.pending_prompt, dict) else []
    selected = next((choice for choice in choices or [] if choice.get("id") == session.choice_id), {})
    action = str(selected.get("action") or "")
    if session.answer or (session.choice_id and action != "continue"):
        session.visual_adjustments[index] = {"choice_id": session.choice_id, "answer": session.answer}


def _emit_skill_confirmation(session: HasturTaskSession) -> None:
    message = f"The task appears to match the vendored skill `{session.skill_name}`. Confirm whether to use it."
    session.pending = "skill_confirmation"
    detail = {
        "kind": "skill_confirmation",
        "title": "Skill confirmation",
        "body": message,
        "input_label": "",
        "skill_name": session.skill_name,
        "choices": [
            {"id": "use_skill", "label": f"Use {session.skill_name}", "description": "Apply the vendored skill workflow to this task.", "action": "continue"},
            {"id": "skip_skill", "label": "Skip skill", "description": "Use the default Godot executor workflow instead.", "action": "continue"},
        ],
    }
    _emit_user_prompt(session, message, detail)


def _emit_generic_user_prompt(session: HasturTaskSession, prompt: dict[str, Any], plan: dict[str, Any]) -> None:
    detail = {
        "kind": "user_prompt",
        "title": str(prompt.get("title") or "Confirmation required"),
        "body": str(prompt.get("body") or prompt.get("message") or plan.get("summary") or ""),
        "input_label": str(prompt.get("input_label") or ""),
        "choices": prompt.get("choices") or [],
        "plan": _public_plan(plan),
    }
    session.pending = "user_prompt"
    _emit_user_prompt(session, detail["body"], detail)


def _emit_choice_request(session: HasturTaskSession, message: str, plan: dict[str, Any]) -> None:
    session.pending = "choice_request"
    detail = {
        "kind": "user_prompt",
        "title": "Choose an option",
        "body": message,
        "input_label": "Answer",
        "choices": plan.get("choices") or [],
        "plan": _public_plan(plan),
    }
    _emit_user_prompt(session, message, detail)


def _emit_safety_prompt(session: HasturTaskSession, plan: dict[str, Any]) -> None:
    message = str(plan.get("summary") or "Review and confirm the plan before execution.")
    session.pending = "plan_review"
    detail = {
        "kind": "user_prompt",
        "title": "Confirmation required",
        "body": message,
        "input_label": "Request changes",
        "choices": [
            {"id": "confirm_plan", "label": "Confirm", "description": "Run the listed safety-sensitive steps.", "action": "continue"},
            {"id": "request_changes", "label": "Revise", "description": "Use the feedback below to revise the plan.", "action": "revise"},
        ],
        "plan": _public_plan(plan),
        "confirmation_required": True,
    }
    _emit_user_prompt(session, message, detail)


def _emit_visual_checkpoint(
    session: HasturTaskSession,
    index: int,
    step: dict[str, Any],
    checkpoint: dict[str, Any],
    prompt: dict[str, Any],
) -> None:
    session.pending = "visual_checkpoint"
    session.pending_step_index = index
    message = str(prompt.get("body") or "Review the visual checkpoint before continuing.")
    detail = {
        "kind": "user_prompt",
        "title": str(prompt.get("title") or "Visual review"),
        "body": message,
        "input_label": str(prompt.get("input_label") or "Feedback"),
        "step": _public_step(step, index),
        "visual_checkpoint": checkpoint,
        "choices": prompt.get("choices") or [],
    }
    _emit_user_prompt(session, message, detail, state="visual_review")


def _emit_user_prompt(session: HasturTaskSession, message: str, detail: dict[str, Any], state: str = "awaiting_user") -> None:
    session.pending_prompt = detail
    _emit(session, "user_prompt", state, message, detail)


def _emit(session: HasturTaskSession, event_type: str, state: str, message: str, detail: Any | None = None) -> None:
    session.state = state if state in TASK_STATES else session.state
    event = {
        "type": event_type,
        "state": session.state,
        "message": message,
        "detail": detail or {},
        "created_at": time.time(),
    }
    session.events.append(event)
    session.event_queue.put(event)


def _emit_activity(session: HasturTaskSession, event_type: str, state: str, message: str, detail: Any | None = None) -> None:
    _emit(session, event_type, state, message, detail)
    if event_type != "activity":
        _emit(session, "activity", state, message, {"source": event_type, "detail": detail or {}})


def _emit_assistant_delta(session: HasturTaskSession, text: str) -> None:
    if not text:
        return
    _emit(session, "assistant_delta", session.state, text, {"delta": text})


def _emit_thought_delta(session: HasturTaskSession, text: str) -> None:
    if not text:
        return
    _emit(session, "thought_delta", session.state, text, {"delta": text, "source": "thought"})


def _finish(session: HasturTaskSession) -> None:
    session.completed = True
    session.event_queue.put(None)


def _sse(event: dict[str, Any]) -> str:
    event_type = str(event.get("type") or "message")
    data = json.dumps(event, ensure_ascii=False)
    return f"event: {event_type}\ndata: {data}\n\n"


def _extract_output_value(broker_response: Any, key: str) -> str:
    if isinstance(broker_response, dict):
        outputs = broker_response.get("outputs")
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, list) and len(item) >= 2 and item[0] == key:
                    return str(item[1])
        for value in broker_response.values():
            found = _extract_output_value(value, key)
            if found:
                return found
    if isinstance(broker_response, list):
        for value in broker_response:
            found = _extract_output_value(value, key)
            if found:
                return found
    return ""


def encode_task_upload(filename: str, content_type: str | None, content: bytes) -> dict[str, str]:
    return encode_upload(filename, content_type, content)
