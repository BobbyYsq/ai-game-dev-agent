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
    "cancelled",
}

DEFAULT_SKILL_NAME = "godot-remote-executor"

GODOT_DOCS = [
    "godot-docs/tutorials/plugins/editor/installing_plugins.rst.txt",
    "godot-docs/tutorials/plugins/editor/making_plugins.rst.txt",
    "godot-docs/tutorials/best_practices/version_control_systems.rst.txt",
    "godot-docs/tutorials/best_practices/project_organization.rst.txt",
    "godot-docs/getting_started/step_by_step/nodes_and_scenes.rst.txt",
    "godot-docs/tutorials/rendering/viewports.rst.txt",
    "godot-docs/classes/class_editorinterface.rst.txt",
    "godot-docs/classes/class_basis.rst.txt",
    "godot-docs/classes/class_node3d.rst.txt",
    "godot-docs/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.rst.txt",
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
    plan: dict[str, Any] | None = None
    next_step_index: int = 0
    prior_results: list[dict[str, Any]] = field(default_factory=list)
    pending_prompt: dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False
    plan_announced: bool = False
    execution_complete: bool = False
    final_ready: bool = False
    post_execution_feedback: str = ""


_SESSIONS: dict[str, HasturTaskSession] = {}
_LOCK = threading.Lock()


class TaskCancelled(RuntimeError):
    pass


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


def cancel_task(task_id: str) -> dict[str, Any]:
    session = get_task(task_id)
    session.cancelled = True
    session.pending = ""
    session.pending_prompt = {}
    if not session.completed:
        _emit(session, "error", "cancelled", "Task cancelled.")
        _finish(session)
    return {"success": True, "task_id": task_id, "state": session.state, "message": "Task cancelled."}


def resume_task(
    task_id: str,
    answer: str = "",
    confirmed: bool = False,
    choice_id: str = "",
    revision_request: str = "",
) -> dict[str, Any]:
    session = get_task(task_id)
    pending = session.pending
    session.answer = answer.strip()
    session.choice_id = choice_id.strip()
    session.revision_request = revision_request.strip()
    if confirmed:
        session.confirmed = True

    if pending == "skill_confirmation":
        _resume_skill_confirmation(session)
    elif pending == "pre_execution_prompt":
        session.plan = None
        session.confirmed = False
        session.plan_announced = False
        session.execution_complete = False
        session.final_ready = False
        session.next_step_index = 0
        session.prior_results = []
        if session.choice_id:
            session.answer = "\n".join(filter(None, [session.answer, f"Selected option: {session.choice_id}"]))
    elif pending == "plan_confirmation":
        selected = _selected_prompt_choice(session)
        action = str(selected.get("action") or "")
        if action in {"confirm", "continue", "execute"} or session.choice_id in {"confirm_plan", "confirm", "continue", "execute"} or confirmed:
            session.confirmed = True
        elif action == "revise" and not session.revision_request:
            session.revision_request = session.answer or "Revise the plan."
        elif session.answer and not session.revision_request:
            session.revision_request = session.answer
        elif session.choice_id:
            session.revision_request = f"Selected option: {session.choice_id}"
        if session.revision_request:
            session.plan = None
            session.confirmed = False
            session.plan_announced = False
            session.execution_complete = False
            session.final_ready = False
            session.next_step_index = 0
            session.prior_results = []
            session.answer = "\n".join(filter(None, [session.answer, f"Plan revision request: {session.revision_request}"]))
    elif pending == "post_execution_review":
        selected = _selected_prompt_choice(session)
        action = str(selected.get("action") or "")
        if action == "finish" and not session.answer:
            session.final_ready = True
        else:
            feedback_parts = []
            if session.choice_id:
                feedback_parts.append(f"Selected option: {session.choice_id}")
            if session.answer:
                feedback_parts.append(session.answer)
            if selected.get("description"):
                feedback_parts.append(f"Option detail: {selected.get('description')}")
            session.post_execution_feedback = "\n".join(feedback_parts).strip() or "Adjust the result based on the selected option."
            session.execution_complete = False
            session.final_ready = False
            session.confirmed = True

    session.pending = ""
    session.pending_prompt = {}
    session.started = False
    session.completed = False
    session.cancelled = False
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
        _raise_if_cancelled(session)
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
        if session.final_ready:
            final = _final_task_response(session, session.plan or {})
            _emit(session, "final", "complete", final, {"results": session.prior_results, "summary": final})
            return

        if session.plan is None:
            _stream_planning_text(session, project_dir, docs, skill_text, executors)
            _raise_if_cancelled(session)
            session.plan = _plan_task(session, project_dir, docs, skill_text, executors)
            session.next_step_index = 0
            session.prior_results = []
            session.plan_announced = False
            session.execution_complete = False
            session.final_ready = False
            session.post_execution_feedback = ""

        plan = _normalize_plan(session.plan)
        session.plan = plan
        if not session.plan_announced:
            _emit_assistant_delta(session, _plan_response_text(plan))
            session.plan_announced = True

        if plan.get("user_prompt") and not (session.answer or session.choice_id):
            _emit_generic_user_prompt(session, plan["user_prompt"])
            return

        if plan.get("question") and not session.answer:
            _emit_choice_request(session, str(plan["question"]), plan)
            return

        choices = plan.get("choices") if isinstance(plan.get("choices"), list) else []
        if choices and not session.choice_id:
            _emit_choice_request(session, str(plan.get("summary") or "Choose how to proceed."), plan)
            return

        if _plan_requires_review(session, plan) and not session.confirmed:
            _emit_plan_confirmation_prompt(session, plan)
            return

        completed = _execute_plan(session, project_dir, docs, skill_text, executors, plan)
        if completed:
            _emit_activity(session, "verification", "verifying", "Checked broker/executor state after execution.", {"executors": hastur_executors()})
            if _should_prompt_after_execution(plan, session):
                checkpoint = _capture_visual_checkpoint(session, project_dir, "Task result") if _plan_needs_visual_check(plan) else _empty_visual_checkpoint()
                checkpoint["analysis"] = _analyze_visual_checkpoint(checkpoint, project_dir)
                prompt = _build_post_execution_user_prompt(session, project_dir, docs, skill_text, executors, plan, checkpoint)
                _emit_post_execution_prompt(session, prompt, checkpoint)
                return
            final = _final_task_response(session, plan)
            _emit(session, "final", "complete", final, {"results": session.prior_results, "summary": final})
    except TaskCancelled:
        _emit(session, "error", "cancelled", "Task cancelled.")
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
            _raise_if_cancelled(session)
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

    if session.execution_complete:
        return True

    _raise_if_cancelled(session)
    feedback = session.post_execution_feedback
    message = "Generating one complete adjustment script." if feedback else "Generating one complete Hastur script for the confirmed plan."
    _emit_activity(session, "execution", "executing", message, {"plan": _public_plan(plan), "adjustment": feedback})
    code = _generate_batch_code(session, project_dir, docs, skill_text, executors, plan, feedback)
    if not code:
        session.prior_results.append({"success": False, "message": "The LLM did not return executable GDScript for the batch."})
        repaired = _repair_failed_batch(session, project_dir, docs, skill_text, executors, plan, session.prior_results)
        if not repaired:
            _emit(session, "error", "failed", "The LLM did not return executable GDScript for the batch.", {"results": session.prior_results})
            return False
        session.execution_complete = True
        session.post_execution_feedback = ""
        session.next_step_index = len(steps)
        return True

    result = apply_hastur_code(session.project_slug, code, executor_type="editor")
    payload = result.model_dump()
    session.prior_results.append(payload)
    _emit_activity(session, "execution_result", "executing", result.message, {"result": payload})
    if not result.success:
        if _is_unrecoverable_hastur_failure(payload):
            _emit(session, "error", "failed", result.message, {"results": session.prior_results})
            return False
        repaired = _repair_failed_batch(session, project_dir, docs, skill_text, executors, plan, session.prior_results)
        if not repaired:
            _emit(session, "error", "failed", "Hastur execution failed and could not be repaired.", {"results": session.prior_results})
            return False

    session.execution_complete = True
    session.post_execution_feedback = ""
    session.next_step_index = len(steps)
    return True


def _generate_batch_code(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    feedback: str = "",
) -> str:
    prompt = _batch_code_prompt(session, project_dir, docs, skill_text, executors, plan, feedback)
    raw = get_llm_provider().generate_text(prompt, system_prompt=_step_code_system_prompt())
    parsed = _parse_response(raw)
    return _extract_executable_code(parsed, raw)


def _repair_failed_batch(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    prior_results: list[dict[str, Any]],
) -> bool:
    attempt = 1
    while True:
        _raise_if_cancelled(session)
        _emit_activity(
            session,
            "repair",
            "repairing",
            f"Repairing complete Hastur script, attempt {attempt}.",
            {"last_result": prior_results[-1] if prior_results else {}},
        )
        prompt = _batch_repair_prompt(session, project_dir, docs, skill_text, executors, plan, prior_results, attempt)
        raw = get_llm_provider().generate_text(prompt, system_prompt=_step_code_system_prompt())
        parsed = _parse_response(raw)
        repair_code = _extract_executable_code(parsed, raw)
        if not repair_code:
            prior_results.append({"success": False, "message": "Repair response did not include executable GDScript."})
            attempt += 1
            continue
        repair_result = apply_hastur_code(session.project_slug, repair_code, executor_type="editor")
        payload = repair_result.model_dump()
        prior_results.append(payload)
        _emit_activity(session, "repair_result", "repairing", repair_result.message, {"result": payload})
        if repair_result.success:
            return True
        if _is_unrecoverable_hastur_failure(payload):
            return False
        attempt += 1


def _capture_visual_checkpoint(session: HasturTaskSession, project_dir: Path, title: str) -> dict[str, Any]:
    filename = f"checkpoint_{int(time.time())}_{uuid4().hex[:8]}.png"
    rel_path = f"assets/generated/visual_checkpoints/{filename}"
    res_path = f"res://{rel_path}"
    code = "\n".join(
        [
            "await RenderingServer.frame_post_draw",
            "var image: Image = null",
            "for viewport in [EditorInterface.get_editor_viewport_3d(0), EditorInterface.get_editor_viewport_2d()]:",
            "\tif viewport == null:",
            "\t\tcontinue",
            "\tvar texture := viewport.get_texture()",
            "\tif texture == null:",
            "\t\tcontinue",
            "\tvar candidate := texture.get_image()",
            "\tif candidate != null and not candidate.is_empty():",
            "\t\timage = candidate",
            "\t\tbreak",
            "if image == null or image.is_empty():",
            "\timage = DisplayServer.screen_get_image(DisplayServer.SCREEN_OF_MAIN_WINDOW)",
            "if image == null or image.is_empty():",
            "\tvar screen_rect := Rect2i(Vector2i.ZERO, DisplayServer.window_get_size())",
            "\timage = DisplayServer.screen_get_image_rect(screen_rect)",
            "if image == null or image.is_empty():",
            "\texecuteContext.output(\"image_status\", \"missing\")",
            "\texecuteContext.output(\"image_error\", \"Editor and screen screenshot capture returned an empty image.\")",
            "else:",
            "\tvar dir_path := ProjectSettings.globalize_path(\"res://assets/generated/visual_checkpoints\")",
            "\tDirAccess.make_dir_recursive_absolute(dir_path)",
            f"\tvar image_path := {json.dumps(res_path)}",
            "\tvar absolute_path := ProjectSettings.globalize_path(image_path)",
            "\tvar save_error := image.save_png(absolute_path)",
            "\tif save_error != OK:",
            "\t\texecuteContext.output(\"image_status\", \"missing\")",
            "\t\texecuteContext.output(\"image_error\", \"Could not save visual checkpoint: \" + error_string(save_error))",
            "\telse:",
            "\t\texecuteContext.output(\"image_status\", \"available\")",
            "\t\texecuteContext.output(\"image_path\", image_path)",
        ]
    )
    result = apply_hastur_code(session.project_slug, code, executor_type="editor")
    payload = result.model_dump()
    output_path = _extract_output_value(payload.get("broker_response"), "image_path") or res_path
    image_status = _extract_output_value(payload.get("broker_response"), "image_status") or ""
    image_error = _extract_output_value(payload.get("broker_response"), "image_error") or ""
    filename_from_output = Path(str(output_path).replace("res://", "")).name
    absolute = project_dir / "assets" / "generated" / "visual_checkpoints" / filename_from_output
    file_available = absolute.exists() and absolute.is_file() and absolute.stat().st_size > 0
    if not file_available:
        image_status = "missing"
        image_error = image_error or "No non-empty PNG file was created for this checkpoint."
    else:
        image_status = "available"
    return {
        "success": result.success and file_available,
        "title": title,
        "image_path": str(output_path),
        "image_url": f"/api/projects/{session.project_slug}/visual-checkpoints/{filename_from_output}" if file_available else "",
        "image_status": image_status,
        "image_error": image_error,
        "absolute_path": str(absolute),
        "result": payload,
    }


def _analyze_visual_checkpoint(checkpoint: dict[str, Any], project_dir: Path) -> str:
    path = Path(checkpoint.get("absolute_path") or "")
    if checkpoint.get("image_status") != "available" or not path.exists() or not path.is_file() or path.stat().st_size <= 0:
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

Reply to the user in natural language. Be concise and direct. Do not ask for broker tokens, broker URLs, executor IDs, or default ports; this app checks and binds that private runtime context automatically. Explain only what you are doing now. Do not include JSON, GDScript, or fake execution results.
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
Do not write GDScript in this planning response. Plan clear user-visible goals; the implementation will be generated later as one complete Hastur script.
Complex scene-building tasks should be described as coherent implementation phases, not tiny code-generation steps.
For read-only inspection requests, plan the minimum steps needed to return the requested factual result; do not turn the final answer into a repeat of the task.
Prefer conservative lighting/post-processing defaults: avoid overexposure, avoid high glow, prefer ACES/AgX/Filmic style tonemapping with controlled exposure/white values when applicable.
{_godot_coordinate_summary()}
Only include user_prompt when choices materially change the result or when you need missing user intent before planning.
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
  "read_only": false,
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
Set read_only true for inspect/list/read tasks that should not mutate the project.
""".strip()


def _task_system_prompt() -> str:
    return "You are a Godot task planner. Output operational JSON only. Never expose secrets. Do not include GDScript."


def _step_code_system_prompt() -> str:
    return "You write complete, repairable Godot editor GDScript batches for Hastur. Return JSON only."


def _batch_code_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    feedback: str = "",
) -> str:
    adjustment = f"\nUser requested adjustment after a successful run:\n{feedback}\n" if feedback else ""
    return f"""
Generate ONE complete GDScript snippet for a single Hastur editor execution.
The snippet must implement the entire confirmed plan in one run. Do not split the work into per-step snippets.
The snippet must be idempotent where practical, tab-indented, and must not use Markdown fences.
Do not ask the user to paste code. Do not expose secrets or broker tokens.
Do not use reserved identifiers such as class_name as variable names.
For visual lighting/post-processing, use conservative values and avoid overexposure.
Use EditorInterface and scene/node APIs consistent with the local Godot docs.
For inspection/list/read requests, do not mutate the scene; collect the requested facts and return them with executeContext.output("result", text). If the user asks for the scene tree, include the complete open edited scene tree in that output.
For mutating scene tasks, save changed scenes/resources when appropriate and emit concise outputs with executeContext.output.
{_godot_coordinate_summary()}

Project path: {project_dir}
Selected skill: {session.skill_name}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
User request: {session.instruction}
User answer context: {session.answer}
{adjustment}

Confirmed plan:
{json.dumps(_public_plan(plan), ensure_ascii=False)}

Prior execution results:
{json.dumps(session.prior_results[-8:], ensure_ascii=False)}

Relevant docs:
{_docs_context(docs)}

Vendored skill excerpt:
{skill_text[:16000]}

Return JSON only:
{{"message": "brief internal summary", "code": "complete GDScript snippet or empty string"}}
""".strip()


def _batch_repair_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    prior_results: list[dict[str, Any]],
    attempt: int,
) -> str:
    return f"""
The previous complete Hastur GDScript batch failed. Generate ONE corrected complete batch script for the same confirmed plan.
Inspect the exact Hastur error, broker payload, and failed code excerpt below. Do not repeat the same rejected code.
The repair must remain a complete one-run script, tab-indented, idempotent where practical, and without Markdown fences.

Repair attempt: {attempt}
Project path: {project_dir}
Selected skill: {session.skill_name}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
User request: {session.instruction}
User answer context: {session.answer}
Post-execution feedback if any: {session.post_execution_feedback}

Confirmed plan:
{json.dumps(_public_plan(plan), ensure_ascii=False)}

Latest error:
{json.dumps(_result_error_context(prior_results[-1] if prior_results else {}), ensure_ascii=False)}

Recent execution results:
{json.dumps(prior_results[-8:], ensure_ascii=False)}

Relevant docs:
{_docs_context(docs)}

Vendored skill excerpt:
{skill_text[:12000]}

Return JSON only:
{{"message": "brief internal summary", "code": "corrected complete GDScript snippet or empty string"}}
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


def _godot_coordinate_summary() -> str:
    return (
        "Godot 3D coordinates: right-handed; +Y is up; camera forward is -Z; "
        "+X is right; +Z is back. Oriented 3D assets conventionally face +Z, "
        "so use look_at(..., use_model_front=true) or Vector3.MODEL_* constants "
        "when working in an asset's local forward direction. For maps/terrain, "
        "+X east, -X west, +Z south, -Z north."
    )


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
        "read_only": bool(plan.get("read_only", False)),
        "requires_user_approval": bool(plan.get("requires_user_approval", False)),
        "user_prompt": _normalize_user_prompt(user_prompt) if user_prompt else None,
        "choices": [_normalize_choice(choice, index) for index, choice in enumerate(choices)],
        "steps": normalized_steps,
        "final": str(plan.get("final") or "Task completed. Review local Git changes manually from the Git workbench."),
    }


def _normalize_user_prompt(prompt: dict[str, Any]) -> dict[str, Any]:
    choices = prompt.get("choices") if isinstance(prompt.get("choices"), list) else []
    image_url = str(prompt.get("image_url") or "")
    image_status = str(prompt.get("image_status") or ("available" if image_url else "none"))
    requires_input = prompt.get("requires_input")
    return {
        "title": str(prompt.get("title") or "Confirmation required"),
        "body": str(prompt.get("body") or prompt.get("message") or ""),
        "input_label": str(prompt.get("input_label") or ""),
        "choices": [_normalize_choice(choice, index) for index, choice in enumerate(choices)],
        "image_url": image_url,
        "image_status": image_status,
        "requires_input": bool(requires_input) if requires_input is not None else bool(choices or prompt.get("input_label")),
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
        "read_only": bool(plan.get("read_only", False)),
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
    if _is_read_only_plan(session, plan):
        return False
    steps = plan.get("steps") or []
    return bool(
        plan.get("requires_user_approval")
        or steps
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
    if step.get("needs_visual_check"):
        return True
    text = f"{title} {step.get('goal', '')}".lower()
    return any(term in text for term in ["light", "exposure", "glow", "fog", "camera", "post", "tonemap", "visual", "光", "曝光", "后期", "画面"])


def _plan_needs_visual_check(plan: dict[str, Any]) -> bool:
    title = str(plan.get("summary") or "")
    return any(_needs_visual_check(step, title) for step in plan.get("steps") or [])


def _is_read_only_plan(session: HasturTaskSession, plan: dict[str, Any]) -> bool:
    if plan.get("read_only"):
        return True
    text = " ".join(
        [
            session.instruction,
            str(plan.get("summary") or ""),
            " ".join(
                f"{step.get('title') or ''} {step.get('goal') or ''}"
                for step in plan.get("steps") or []
            ),
        ]
    ).lower()
    read_terms = [
        "inspect",
        "list",
        "read",
        "show",
        "tell me",
        "scene tree",
        "what is",
        "查看",
        "读取",
        "列出",
        "告诉我",
        "场景树",
    ]
    mutate_terms = [
        "create",
        "add",
        "build",
        "make",
        "remove",
        "delete",
        "change",
        "save",
        "generate",
        "生成",
        "创建",
        "添加",
        "删除",
        "修改",
        "保存",
        "搭建",
    ]
    return any(term in text for term in read_terms) and not any(term in text for term in mutate_terms)


def _should_prompt_after_execution(plan: dict[str, Any], session: HasturTaskSession) -> bool:
    return bool(session.execution_complete and not session.final_ready and not _is_read_only_plan(session, plan))


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


def _selected_prompt_choice(session: HasturTaskSession) -> dict[str, Any]:
    choices = session.pending_prompt.get("choices") if isinstance(session.pending_prompt, dict) else []
    if not isinstance(choices, list):
        return {}
    return next((choice for choice in choices if isinstance(choice, dict) and choice.get("id") == session.choice_id), {})


def _plan_response_text(plan: dict[str, Any]) -> str:
    lines = [str(plan.get("summary") or "Plan ready.").strip()]
    choices = plan.get("choices") if isinstance(plan.get("choices"), list) else []
    if choices:
        lines.append("")
        lines.append("Options:")
        for choice in choices:
            description = f" - {choice.get('description')}" if choice.get("description") else ""
            lines.append(f"- {choice.get('label') or choice.get('id')}{description}")
    steps = plan.get("steps") if isinstance(plan.get("steps"), list) else []
    if steps:
        lines.append("")
        lines.append("Plan:")
        for index, step in enumerate(steps, start=1):
            title = str(step.get("title") or f"Step {index}").strip()
            goal = str(step.get("goal") or "").strip()
            lines.append(f"{index}. {title}" + (f" - {goal}" if goal and goal != title else ""))
    if plan.get("read_only"):
        lines.append("")
        lines.append("I will run this as one read-only Hastur batch and return the requested output in the chat.")
    elif steps:
        lines.append("")
        lines.append("After you confirm, I will generate one complete Hastur batch script for the whole plan and repair that full script until it runs.")
    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def _empty_visual_checkpoint() -> dict[str, Any]:
    return {
        "success": False,
        "title": "Task result",
        "image_path": "",
        "image_url": "",
        "image_status": "not_requested",
        "image_error": "",
        "absolute_path": "",
        "result": {},
    }


def _build_post_execution_user_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    analysis = str(checkpoint.get("analysis") or "")
    status = str(checkpoint.get("image_status") or "none")
    body_parts = ["The batch ran successfully."]
    if analysis:
        body_parts.append(analysis)
    if status not in {"available", "not_requested", "none"}:
        body_parts.append(str(checkpoint.get("image_error") or "No screenshot was available."))
    body_parts.append("Choose finish, or describe what to adjust next.")
    return {
        "title": "Review result",
        "body": "\n".join(part for part in body_parts if part),
        "input_label": "Modification request",
        "choices": [
            {"id": "finish", "label": "Finish", "description": "Keep this result and end the task.", "action": "finish"},
            {"id": "adjust", "label": "Modify", "description": "Use the text below to generate one complete adjustment batch.", "action": "adjust"},
        ],
        "image_url": checkpoint.get("image_url") if status == "available" else "",
        "image_status": status,
        "image_error": checkpoint.get("image_error") or "",
        "requires_input": True,
    }


def _emit_skill_confirmation(session: HasturTaskSession) -> None:
    message = f"The task appears to match the vendored skill `{session.skill_name}`. Confirm whether to use it."
    session.pending = "skill_confirmation"
    detail = {
        "title": "Skill confirmation",
        "body": message,
        "input_label": "",
        "choices": [
            {"id": "use_skill", "label": f"Use {session.skill_name}", "description": "Apply the vendored skill workflow to this task.", "action": "continue"},
            {"id": "skip_skill", "label": "Skip skill", "description": "Use the default Godot executor workflow instead.", "action": "continue"},
        ],
        "image_url": "",
        "image_status": "none",
        "requires_input": True,
    }
    _emit_user_prompt(session, message, detail)


def _emit_generic_user_prompt(session: HasturTaskSession, prompt: dict[str, Any]) -> None:
    detail = {
        "title": str(prompt.get("title") or "Confirmation required"),
        "body": str(prompt.get("body") or prompt.get("message") or ""),
        "input_label": str(prompt.get("input_label") or ""),
        "choices": prompt.get("choices") or [],
        "image_url": str(prompt.get("image_url") or ""),
        "image_status": str(prompt.get("image_status") or "none"),
        "requires_input": bool(prompt.get("requires_input", True)),
    }
    session.pending = "pre_execution_prompt"
    _emit_user_prompt(session, detail["body"], detail)


def _emit_choice_request(session: HasturTaskSession, message: str, plan: dict[str, Any]) -> None:
    session.pending = "pre_execution_prompt"
    detail = {
        "title": "Choose an option",
        "body": message,
        "input_label": "Answer",
        "choices": plan.get("choices") or [],
        "image_url": "",
        "image_status": "none",
        "requires_input": True,
    }
    _emit_user_prompt(session, message, detail)


def _emit_plan_confirmation_prompt(session: HasturTaskSession, plan: dict[str, Any]) -> None:
    message = "Review the plan in the chat. Confirm to generate and run one complete Hastur script, or send changes."
    session.pending = "plan_confirmation"
    detail = {
        "title": "Confirmation required",
        "body": message,
        "input_label": "Request changes",
        "choices": [
            {"id": "confirm_plan", "label": "Confirm", "description": "Generate and run one complete Hastur script.", "action": "confirm"},
            {"id": "request_changes", "label": "Revise", "description": "Use the feedback below to revise the plan.", "action": "revise"},
        ],
        "image_url": "",
        "image_status": "none",
        "requires_input": True,
    }
    _emit_user_prompt(session, message, detail)


def _emit_post_execution_prompt(session: HasturTaskSession, prompt: dict[str, Any], checkpoint: dict[str, Any]) -> None:
    session.pending = "post_execution_review"
    image_status = str(checkpoint.get("image_status") or prompt.get("image_status") or "none")
    image_url = str(checkpoint.get("image_url") or prompt.get("image_url") or "") if image_status == "available" else ""
    message = str(prompt.get("body") or "Review the result and choose whether to continue modifying it.")
    detail = {
        "title": str(prompt.get("title") or "Review result"),
        "body": message,
        "input_label": str(prompt.get("input_label") or "Modification request"),
        "choices": prompt.get("choices") or [],
        "image_url": image_url,
        "image_status": image_status,
        "image_error": str(checkpoint.get("image_error") or prompt.get("image_error") or ""),
        "requires_input": True,
    }
    _emit_user_prompt(session, message, detail, state="awaiting_user")


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
    suffix = "" if str(message).endswith(("\n", "\r")) else "\n"
    _emit_thought_delta(session, f"{message}{suffix}", state=state, kind=event_type, detail=detail)


def _emit_assistant_delta(session: HasturTaskSession, text: str) -> None:
    if not text:
        return
    _emit(session, "assistant_delta", session.state, text, {"delta": text})


def _emit_thought_delta(
    session: HasturTaskSession,
    text: str,
    state: str | None = None,
    kind: str = "work",
    detail: Any | None = None,
) -> None:
    if not text:
        return
    _emit(session, "thought_delta", state or session.state, text, {"delta": text, "kind": kind, "detail": detail or {}})


def _raise_if_cancelled(session: HasturTaskSession) -> None:
    if session.cancelled:
        raise TaskCancelled()


def _is_unrecoverable_hastur_failure(result: dict[str, Any]) -> bool:
    message = str(result.get("message") or "").lower()
    return any(
        phrase in message
        for phrase in [
            "bridge is disabled",
            "broker unavailable",
            "broker is not reachable",
            "no godot executor",
            "executor is connected",
            "connection refused",
            "connecterror",
            "read timed out",
            "timed out",
            "401",
            "403",
        ]
    )


def _result_error_context(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": result.get("success"),
        "message": result.get("message"),
        "broker_response": result.get("broker_response"),
        "gdscript_excerpt": str(result.get("gdscript") or "")[:4000],
    }


def _final_task_response(session: HasturTaskSession, plan: dict[str, Any]) -> str:
    outputs: list[tuple[str, str]] = []
    for result in session.prior_results:
        outputs.extend(_extract_output_pairs(result.get("broker_response")))
    cleaned_outputs = [(key, value.strip()) for key, value in outputs if value and value.strip()]
    if cleaned_outputs:
        if len(cleaned_outputs) == 1:
            return cleaned_outputs[0][1][:12000]
        return "\n\n".join(f"{key}:\n{value[:12000]}" for key, value in cleaned_outputs)

    successful_messages = [
        str(result.get("message") or "").strip()
        for result in session.prior_results
        if result.get("success") and str(result.get("message") or "").strip()
    ]
    if successful_messages:
        return "Task completed.\n" + "\n".join(f"- {message}" for message in successful_messages[-5:])
    return str(plan.get("final") or "Task completed. Review local Git changes manually from the Git workbench.")


def _finish(session: HasturTaskSession) -> None:
    if session.completed:
        return
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


def _extract_output_pairs(broker_response: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(broker_response, dict):
        outputs = broker_response.get("outputs")
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, list) and len(item) >= 2:
                    pairs.append((str(item[0]), str(item[1])))
                elif isinstance(item, dict):
                    output_key = item.get("key") or item.get("name") or item.get("label") or "result"
                    output_value = item.get("value") or item.get("text") or item.get("data")
                    if output_value is not None:
                        pairs.append((str(output_key), str(output_value)))
        for key, value in broker_response.items():
            if key == "outputs":
                continue
            pairs.extend(_extract_output_pairs(value))
    elif isinstance(broker_response, list):
        if len(broker_response) >= 2 and not isinstance(broker_response[0], (dict, list)):
            return [(str(broker_response[0]), str(broker_response[1]))]
        for value in broker_response:
            pairs.extend(_extract_output_pairs(value))
    return pairs


def encode_task_upload(filename: str, content_type: str | None, content: bytes) -> dict[str, str]:
    return encode_upload(filename, content_type, content)
