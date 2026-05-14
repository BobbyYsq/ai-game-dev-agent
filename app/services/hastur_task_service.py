from __future__ import annotations

from dataclasses import dataclass, field
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
    _attachment_summary,
    _execution_readiness,
    _parse_response,
    _public_attachment_list,
    encode_upload,
)
from app.services.hastur_service import apply_hastur_code, hastur_executors
from app.services.hastur_skill_service import list_hastur_skills, load_hastur_skill, skill_listing_for_prompt
from app.services.settings_service import load_private_settings


TASK_STATES = {
    "intake",
    "context",
    "planning",
    "awaiting_user",
    "executing",
    "repairing",
    "verifying",
    "complete",
    "failed",
    "cancelled",
}

DEFAULT_SKILL_NAME = "godot-remote-executor"
MAX_REPEATED_REPAIR_FAILURES = 3

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
    "godot-docs/classes/class_mesh.rst.txt",
    "godot-docs/classes/class_arraymesh.rst.txt",
    "godot-docs/classes/class_meshdatatool.rst.txt",
    "godot-docs/classes/class_surfacetool.rst.txt",
    "godot-docs/classes/class_basematerial3d.rst.txt",
    "godot-docs/classes/class_environment.rst.txt",
    "godot-docs/classes/class_worldenvironment.rst.txt",
    "godot-docs/classes/class_cameraattributes.rst.txt",
    "godot-docs/classes/class_cameraattributespractical.rst.txt",
    "godot-docs/classes/class_light3d.rst.txt",
    "godot-docs/classes/class_directionallight3d.rst.txt",
    "godot-docs/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.rst.txt",
    "godot-docs/tutorials/3d/environment_and_post_processing.rst.txt",
]


@dataclass
class HasturTaskSession:
    task_id: str
    project_slug: str
    instruction: str
    skill_name: str
    workflow_mode: str = "auto"
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
    needs_resume_thought: bool = False
    context_request_keys: set[str] = field(default_factory=set)
    vision_summary: str = ""
    current_task_id: str = ""
    announced_skills: set[str] = field(default_factory=set)


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
    workflow_mode: str = "auto",
) -> dict[str, Any]:
    project_dir = get_project_dir(project_slug)
    explicit = _instruction_has_skill_prefix(instruction)
    selected_skill = skill_name if explicit and skill_name else detect_skill(instruction, project_slug)
    mode = workflow_mode if workflow_mode in {"auto", "plan"} else "auto"
    session = HasturTaskSession(
        task_id=uuid4().hex,
        project_slug=project_slug,
        instruction=instruction,
        skill_name=selected_skill,
        workflow_mode=mode,
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
        "workflow_mode": mode,
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

    if pending == "pre_execution_prompt":
        selected = _selected_prompt_choice(session)
        session.plan = None
        session.confirmed = False
        session.plan_announced = False
        session.execution_complete = False
        session.final_ready = False
        session.next_step_index = 0
        session.prior_results = []
        session.context_request_keys = set()
        if session.choice_id:
            session.answer = _append_selected_choice_context(session.answer, session.choice_id, selected)
    elif pending == "plan_confirmation":
        selected = _selected_prompt_choice(session)
        action = str(selected.get("action") or "")
        if action == "revise" and not session.revision_request:
            session.revision_request = session.answer or "Revise the plan."
        elif action in {"confirm", "continue", "execute"} or session.choice_id or confirmed:
            session.confirmed = True
            if session.choice_id:
                session.answer = _append_selected_choice_context(session.answer, session.choice_id, selected)
            if isinstance(session.plan, dict):
                session.plan = {**session.plan, "user_prompt": None}
        elif session.answer and not session.revision_request:
            session.revision_request = session.answer
        if session.revision_request:
            session.plan = None
            session.confirmed = False
            session.plan_announced = False
            session.execution_complete = False
            session.final_ready = False
            session.next_step_index = 0
            session.prior_results = []
            session.context_request_keys = set()
            session.answer = "\n".join(filter(None, [session.answer, f"Plan revision request: {session.revision_request}"]))
    session.pending = ""
    session.pending_prompt = {}
    session.started = False
    session.completed = False
    session.cancelled = False
    session.events = []
    session.event_queue = queue.Queue()
    session.state = "context"
    session.needs_resume_thought = True
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


def detect_skill(instruction: str, project_slug: str | None = None) -> str:
    first = instruction.strip().split(maxsplit=1)[0] if instruction.strip() else ""
    skills = list_hastur_skills(project_slug)
    names = {skill.name for skill in skills}
    if first.startswith("/") and first[1:] in names:
        return first[1:]
    lower = instruction.lower()
    for skill in skills:
        if skill.disable_model_invocation:
            continue
        haystack = f"{skill.name} {skill.description}".lower()
        if skill.name == _default_skill_name():
            continue
        if skill.paths and not _skill_paths_match_instruction(skill.paths, lower):
            continue
        if any(word in haystack for word in re.findall(r"[a-zA-Z][a-zA-Z_-]{3,}", lower)):
            return skill.name
    return _default_skill_name()


def _skill_paths_match_instruction(paths: list[str], instruction: str) -> bool:
    for path in paths:
        normalized = path.replace("\\", "/").lower().strip()
        if normalized and normalized in instruction:
            return True
        name = Path(normalized).name
        if name and name in instruction:
            return True
    return False


def _run_task(session: HasturTaskSession) -> None:
    try:
        _raise_if_cancelled(session)
        project_dir = get_project_dir(session.project_slug)
        docs = _load_godot_docs()
        executors = hastur_executors()

        readiness = _execution_readiness(load_private_settings(), executors)
        if readiness:
            _emit(session, "error", "failed", readiness, {"executors": executors})
            return

        skill_text = _skill_body_for_session(session)
        if skill_text and session.skill_explicit:
            _emit_skill_invocation_notice(session, session.skill_name, "explicit")
        _ensure_attachment_observations(session)
        if session.final_ready:
            final = _final_task_response(session, session.plan or {})
            _emit(session, "final", "complete", final, {"results": session.prior_results, "summary": final})
            return

        if session.plan is None:
            _stream_planning_text(session, project_dir, docs, skill_text, executors)
            session.needs_resume_thought = False
            _raise_if_cancelled(session)
            session.plan = _plan_task(session, project_dir, docs, skill_text, executors)
            session.next_step_index = 0
            session.prior_results = []
            session.plan_announced = False
            session.execution_complete = False
            session.final_ready = False
            session.post_execution_feedback = ""
        elif session.needs_resume_thought:
            _stream_resume_text(session, project_dir, docs, skill_text, executors)
            session.needs_resume_thought = False

        plan = _enforce_workflow_mode(session, _normalize_plan(session.plan))
        if _plan_requires_review(session, plan) and not plan.get("user_prompt") and not session.confirmed:
            repaired_plan = _repair_plan_missing_modal(session, project_dir, docs, skill_text, executors, plan)
            if repaired_plan:
                plan = _enforce_workflow_mode(session, _normalize_plan(repaired_plan))
        session.plan = plan
        _emit_task_breakdown(session, plan)
        if _should_announce_plan(plan) and not session.plan_announced:
            _emit_assistant_delta(session, _plan_response_text(plan))
            session.plan_announced = True

        if plan.get("user_prompt"):
            pending = _prompt_pending_state(session, plan)
            _emit_generic_user_prompt(session, plan["user_prompt"], pending=pending)
            return

        if plan.get("question") and not session.answer:
            _emit(session, "error", "failed", "The LLM asked for user input without instantiating the modal tool.")
            return

        choices = plan.get("choices") if isinstance(plan.get("choices"), list) else []
        if choices and not session.choice_id:
            _emit(session, "error", "failed", "The LLM returned choices without instantiating the modal tool.")
            return

        if _plan_requires_review(session, plan) and not session.confirmed:
            _emit(session, "error", "failed", "The LLM did not provide modal content for plan confirmation.")
            return

        completed = _execute_plan(session, project_dir, docs, skill_text, executors, plan)
        if completed:
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


def _stream_resume_text(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> None:
    llm = get_llm_provider()
    prompt = _resume_chat_prompt(session, project_dir, docs, skill_text, executors)
    stream = getattr(llm, "generate_text_stream", None)
    if callable(stream):
        for chunk in stream(prompt, system_prompt=_planning_chat_system_prompt()):
            _raise_if_cancelled(session)
            _emit_thought_delta(session, str(chunk), state="planning", kind="resume")
        return
    text = llm.generate_text(prompt, system_prompt=_planning_chat_system_prompt())
    _emit_thought_delta(session, text, state="planning", kind="resume")


def _plan_task(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> dict[str, Any]:
    context_snippets: list[str] = []
    llm = get_llm_provider()
    for attempt in range(3):
        prompt = _task_prompt(session, project_dir, docs, skill_text, executors, context_snippets)
        raw = llm.generate_text(prompt, system_prompt=_task_system_prompt())
        parsed = _parse_response(raw)
        requests = parsed.get("context_requests") if isinstance(parsed, dict) else []
        if attempt < 2 and isinstance(requests, list) and requests:
            resolved = _resolve_context_requests(session, requests)
            if resolved:
                context_snippets.extend(resolved)
                continue
        return _normalize_plan(parsed)
    return _normalize_plan(parsed)


def _repair_plan_missing_modal(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any] | None:
    invalid_response = ""
    for attempt in range(2):
        prompt = f"""
The previous planner JSON requires user approval but did not instantiate the abstract modal tool.
Return the full corrected planner JSON. Keep the same task intent, but add user_prompt with LLM-authored title, body, choices, input_label, and requires_input.
The UI renders exactly the choices you provide, in the order and count you choose; do not assume there are exactly two choices and do not add fixed generic defaults.
Every visible choice label and description must be authored for this specific task. For plan approval, include at least one approval/continue/execute choice with an action such as "confirm", "continue", or "execute"; add revision/alternative choices only when they are useful.
Do not create a choice whose purpose is "I will type/provide my own answer/path/details"; the custom reply box already handles that.
The custom reply box is always rendered separately for alternate user instructions or revisions. When choices are present, input_label should describe alternate instructions, not repeat the main question. Set requires_input true only when a custom text answer is mandatory.
Do not generate GDScript here.

Project path: {project_dir}
User request: {session.instruction}
Workflow mode: {session.workflow_mode}
Previous plan:
{json.dumps(plan, ensure_ascii=False)}
{f'''
Previous invalid repair response:
{invalid_response}
''' if invalid_response else ''}

Capability registry:
{_capability_registry_text()}

Available skills:
{skill_listing_for_prompt(session.project_slug)}

Godot docs index:
{_docs_summary(docs)}

Loaded skill/context snippets:
{_context_snippets_text(skill_text, [])}

Connected executors:
{json.dumps(executors, ensure_ascii=False)}

Return JSON only with user_prompt populated.
""".strip()
        raw = get_llm_provider().generate_text(prompt, system_prompt=_task_system_prompt())
        parsed = _parse_response(raw)
        repaired = _coerce_repaired_modal_plan(plan, parsed)
        if repaired:
            return repaired
        invalid_response = str(raw)[:2000]
    return None


def _coerce_repaired_modal_plan(plan: dict[str, Any], parsed: Any) -> dict[str, Any] | None:
    if not isinstance(parsed, dict):
        return None

    prompt = parsed.get("user_prompt") if isinstance(parsed.get("user_prompt"), dict) else None
    if not prompt:
        for key in ("modal", "prompt", "confirmation_prompt", "userPrompt"):
            value = parsed.get(key)
            if isinstance(value, dict):
                prompt = value
                break
    if not prompt and _looks_like_user_prompt_object(parsed):
        prompt = parsed
    if not prompt:
        return None

    repaired = dict(plan)
    if prompt is not parsed:
        repaired.update(parsed)
    repaired["user_prompt"] = prompt
    return repaired


def _looks_like_user_prompt_object(value: dict[str, Any]) -> bool:
    prompt_keys = {"title", "body", "message", "input_label", "choices", "requires_input"}
    return bool(prompt_keys.intersection(value)) and bool(value.get("body") or value.get("message") or value.get("title"))


def _execute_plan(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
) -> bool:
    steps = plan.get("steps") or []
    direct_code = _direct_plan_code(plan)
    if not steps and not direct_code:
        _complete_all_tasks(session, "skipped")
        return True

    if session.execution_complete:
        return True

    if _execution_strategy(plan) == "sequential_subtasks" and len(plan.get("task_breakdown") or []) > 1 and not direct_code:
        completed = _execute_sequential_tasks(session, project_dir, docs, skill_text, executors, plan)
        if completed:
            session.execution_complete = True
            session.post_execution_feedback = ""
            session.next_step_index = len(steps)
        return completed

    task_id = _first_task_id(plan)
    completed = _execute_one_batch(session, project_dir, docs, skill_text, executors, plan, task_id)
    if completed:
        session.execution_complete = True
        session.post_execution_feedback = ""
        session.next_step_index = len(steps)
    return completed


def _execute_sequential_tasks(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
) -> bool:
    tasks = plan.get("task_breakdown") or []
    for task in tasks:
        task_id = str(task.get("id") or "")
        subplan = _subtask_plan(plan, task)
        if not _execute_one_batch(session, project_dir, docs, skill_text, executors, subplan, task_id):
            return False
    return True


def _execute_one_batch(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    plan: dict[str, Any],
    task_id: str,
) -> bool:
    _raise_if_cancelled(session)
    _set_task_status(session, task_id, "active", "executing", f"Working on { _task_title(plan, task_id) }.")
    feedback = session.post_execution_feedback
    direct_code = _direct_plan_code(plan)
    if direct_code and not feedback:
        message = "Executing the LLM-selected direct Hastur action."
        code = direct_code
    else:
        message = "Generating one complete adjustment script." if feedback else "Generating one complete Hastur script for the LLM-selected plan."
        code = _generate_batch_code(session, project_dir, docs, skill_text, executors, plan, feedback)
    _emit_activity(session, "execution", "executing", message, {"plan": _public_plan(plan), "adjustment": feedback})
    if not code:
        session.prior_results.append({"success": False, "message": "The LLM did not return executable GDScript for the batch."})
        repaired = _repair_failed_batch(session, project_dir, docs, skill_text, executors, plan, session.prior_results)
        if not repaired:
            _set_task_status(session, task_id, "failed", "failed", "The current task could not produce executable GDScript.")
            _emit(session, "error", "failed", "The LLM did not return executable GDScript for the batch.", {"results": session.prior_results})
            return False
        _set_task_status(session, task_id, "completed", "executing", "The current task completed after repair.")
        return True

    result = apply_hastur_code(session.project_slug, code, executor_type="editor")
    payload = result.model_dump()
    session.prior_results.append(payload)
    _emit_activity(session, "execution_result", "executing", result.message, {"result": payload})
    if result.success:
        output_failure = _missing_output_contract_result(session, plan, payload)
        if output_failure:
            session.prior_results.append(output_failure)
            repaired = _repair_failed_batch(session, project_dir, docs, skill_text, executors, plan, session.prior_results)
            if not repaired:
                _set_task_status(session, task_id, "failed", "failed", output_failure["message"])
                _emit(session, "error", "failed", output_failure["message"], {"results": session.prior_results})
                return False
    else:
        if _is_unrecoverable_hastur_failure(payload):
            _set_task_status(session, task_id, "failed", "failed", result.message)
            _emit(session, "error", "failed", result.message, {"results": session.prior_results})
            return False
        repaired = _repair_failed_batch(session, project_dir, docs, skill_text, executors, plan, session.prior_results)
        if not repaired:
            _set_task_status(session, task_id, "failed", "failed", "Hastur execution failed and could not be repaired.")
            _emit(session, "error", "failed", "Hastur execution failed and could not be repaired.", {"results": session.prior_results})
            return False

    _set_task_status(session, task_id, "completed", "executing", "The current task completed.")
    return True


def _execution_strategy(plan: dict[str, Any]) -> str:
    value = str(plan.get("execution_strategy") or "").strip()
    return value if value in {"single_batch", "sequential_subtasks", "ask_first"} else "single_batch"


def _first_task_id(plan: dict[str, Any]) -> str:
    tasks = plan.get("task_breakdown") if isinstance(plan.get("task_breakdown"), list) else []
    if tasks:
        return str(tasks[0].get("id") or "task_1")
    return "task_1"


def _task_title(plan: dict[str, Any], task_id: str) -> str:
    for task in plan.get("task_breakdown") or []:
        if str(task.get("id") or "") == task_id:
            return str(task.get("title") or task_id)
    return str(plan.get("summary") or task_id)


def _subtask_plan(plan: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    copied = dict(plan)
    step = {
        "title": task.get("title") or "Task",
        "goal": task.get("goal") or task.get("title") or "",
        "type": task.get("kind") or "editor",
        "requires_confirmation": bool(task.get("requires_confirmation")),
    }
    copied["mode"] = "plan"
    copied["summary"] = step["title"]
    copied["steps"] = [step]
    copied["task_breakdown"] = [dict(task)]
    copied["execution_strategy"] = "single_batch"
    copied["code"] = ""
    return copied


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
    repeated_failures: dict[str, int] = {}
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
            if _record_repair_failure(repeated_failures, prior_results[-1]):
                return False
            attempt += 1
            continue
        repair_result = apply_hastur_code(session.project_slug, repair_code, executor_type="editor")
        payload = repair_result.model_dump()
        prior_results.append(payload)
        _emit_activity(session, "repair_result", "repairing", repair_result.message, {"result": payload})
        if repair_result.success:
            output_failure = _missing_output_contract_result(session, plan, payload)
            if output_failure:
                prior_results.append(output_failure)
                if _record_repair_failure(repeated_failures, output_failure):
                    return False
                attempt += 1
                continue
            return True
        if _is_unrecoverable_hastur_failure(payload):
            return False
        if _record_repair_failure(repeated_failures, payload):
            return False
        attempt += 1


def _record_repair_failure(repeated_failures: dict[str, int], result: dict[str, Any]) -> bool:
    signature = _repair_failure_signature(result)
    repeated_failures[signature] = repeated_failures.get(signature, 0) + 1
    return repeated_failures[signature] >= MAX_REPEATED_REPAIR_FAILURES


def _repair_failure_signature(result: dict[str, Any]) -> str:
    contract = result.get("output_contract") if isinstance(result.get("output_contract"), dict) else {}
    reason = str(contract.get("reason") or "")
    message = str(result.get("message") or "")
    broker_error = _broker_error_text(result.get("broker_response"))
    return "|".join([reason, message, broker_error])[:1200]


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
    if first.startswith(
        (
            "extends ",
            "@tool",
            "func ",
            "var ",
            "const ",
            "if ",
            "for ",
            "while ",
            "match ",
            "EditorInterface.",
            "ProjectSettings.",
            "ResourceSaver.",
            "ClassDB.",
            "InputMap.",
            "DisplayServer.",
            "RenderingServer.",
            "executeContext.",
            "execute_context.",
            "print(",
            "push_error(",
        )
    ):
        return True
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\s*\(", first):
        return True
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?\s*(?::=|=)\s*.+", first))


def _capability_registry_text() -> str:
    return f"""
- modal: Abstract user prompt tool. You may instantiate it by returning user_prompt with title, body, optional input_label, requires_input, and choices. The agent renders your modal copy and however many concrete choices you provide. Do not include an "I will type my own answer" choice because the custom reply box is always visible for alternate instructions; requires_input only means that custom reply is mandatory.
- skills: Use the skill listing to decide whether a skill is relevant. Request full skill content with context_requests when needed.
- godot_docs: Use the docs index to request small local snippets by path or keyword. Do not assume the full docs are in context.
- hastur_editor_batch: The agent can execute one complete editor GDScript batch only after your direct code or an approved plan.
- task_breakdown: Classify complexity and list one task for simple work or multiple tasks for phased work. The agent displays the list and current active task.
""".strip()


def _skill_body_for_session(session: HasturTaskSession) -> str:
    bodies: list[str] = []
    if not session.skill_explicit:
        explicit_body = ""
    else:
        try:
            explicit_body = load_hastur_skill(session.skill_name, project_slug=session.project_slug)
            if explicit_body:
                bodies.append(f"--- skill:{session.skill_name} ---\n{explicit_body[:6000]}")
        except FileNotFoundError:
            explicit_body = ""
    for skill in _auto_invoked_skills(session):
        if skill.name == session.skill_name and explicit_body:
            continue
        try:
            body = load_hastur_skill(skill.name, project_slug=session.project_slug)
            bodies.append(f"--- skill:{skill.name} ---\n{body[:6000]}")
            _emit_skill_invocation_notice(session, skill.name, "auto")
        except FileNotFoundError:
            continue
    return "\n\n".join(bodies)


def _auto_invoked_skills(session: HasturTaskSession) -> list[Any]:
    instruction = session.instruction.lower()
    matches: list[Any] = []
    for skill in list_hastur_skills(session.project_slug):
        if skill.disable_model_invocation:
            continue
        if skill.name == _default_skill_name():
            continue
        haystack = f"{skill.name} {skill.description} {skill.when_to_use}".lower()
        if _skill_matches_instruction_text(instruction, haystack):
            matches.append(skill)
    return matches


def _skill_matches_instruction_text(instruction: str, haystack: str) -> bool:
    latin_terms = [term for term in re.findall(r"[a-zA-Z][a-zA-Z_-]{3,}", instruction) if len(term) >= 4]
    if any(term in haystack for term in latin_terms):
        return True
    chinese_terms = [
        "\u5927\u9646",
        "\u5730\u5f62",
        "\u5730\u56fe",
        "\u6b63\u9762",
        "\u53cd\u9762",
        "\u80cc\u9762",
        "\u900f\u660e",
        "\u6750\u8d28",
        "\u4e0a\u4e0b",
        "\u98a0\u5012",
        "\u6cd5\u7ebf",
        "\u5254\u9664",
        "\u7ed5\u5e8f",
        "\u540e\u671f",
        "\u5149\u6e90",
        "\u706f\u5149",
        "\u73af\u5883",
        "\u76f8\u673a",
        "\u6e05\u6670",
        "\u6a21\u7cca",
        "\u9ed1\u6697",
        "\u8fc7\u66dd",
    ]
    return any(term in instruction and term in haystack for term in chinese_terms)


def _context_snippets_text(skill_text: str, snippets: list[str]) -> str:
    sections = []
    if skill_text:
        sections.append(skill_text[:12000])
    sections.extend(snippet[:5000] for snippet in snippets if snippet.strip())
    return "\n\n".join(sections) if sections else "No full skill or Godot doc body is loaded yet. Use context_requests if needed."


def _resolve_context_requests(session: HasturTaskSession, requests: list[Any]) -> list[str]:
    snippets: list[str] = []
    for request in requests:
        if not isinstance(request, dict):
            continue
        key = _context_request_key(request, session)
        if key in session.context_request_keys:
            continue
        request_type = str(request.get("type") or "").strip()
        if request_type == "skill":
            name = str(request.get("name") or session.skill_name).strip()
            try:
                body = load_hastur_skill(name, project_slug=session.project_slug)
                snippets.append(f"--- skill:{name} ---\n{body[:6000]}")
                session.context_request_keys.add(key)
                _emit_skill_invocation_notice(session, name, "context_request")
            except FileNotFoundError:
                continue
        elif request_type == "godot_doc":
            path = str(request.get("path") or "").strip()
            query = str(request.get("query") or "").strip()
            text = _read_godot_doc(path)
            if text:
                snippets.append(f"--- {path} ---\n{_doc_excerpt(text, query)}")
                session.context_request_keys.add(key)
        elif request_type == "godot_doc_search":
            query = str(request.get("query") or "").strip()
            if query:
                found = _search_godot_docs(query)
                if found:
                    snippets.extend(found)
                    session.context_request_keys.add(key)
    return snippets


def _context_request_key(request: dict[str, Any], session: HasturTaskSession) -> str:
    request_type = str(request.get("type") or "").strip()
    name = str(request.get("name") or session.skill_name).strip()
    path = str(request.get("path") or "").replace("\\", "/").strip()
    query = str(request.get("query") or "").strip().lower()
    return "|".join([request_type, name, path, query])


def _ensure_attachment_observations(session: HasturTaskSession) -> None:
    if session.vision_summary:
        return
    images = [item for item in session.attachments if str(item.get("media_type", "")).startswith("image/")]
    if not images:
        return
    llm = get_llm_provider()
    if not getattr(llm, "supports_images", False) or not hasattr(llm, "generate_text_with_images"):
        session.vision_summary = (
            "Image attachments were provided, but the selected LLM provider does not support image input in this app. "
            "Ask the user for a textual description before relying on screenshot content."
        )
        return
    prompt = f"""
Summarize the attached images for a Godot task in concise natural language.
Focus on visible editor/game state, selected nodes, material/mesh/camera issues, and any evidence needed to solve the user's request.
Do not invent hidden state and do not write code.

User request:
{session.instruction}

Uploaded files:
{json.dumps(_public_attachment_list(images), ensure_ascii=False)}
""".strip()
    raw = llm.generate_text_with_images(prompt, images, system_prompt="Describe image evidence for a Godot/Hastur task. Return concise text only.")
    session.vision_summary = _clip_text(str(raw or "").strip(), 2000) or "Image attachments were provided, but no reliable visual observations were returned."


def _attachment_context_text(session: HasturTaskSession) -> str:
    return f"""
Uploaded file summary:
{_attachment_summary(session.attachments)}

Image observations:
{session.vision_summary or "No image observations loaded."}
""".strip()


def _read_godot_doc(rel_path: str) -> str:
    normalized = rel_path.replace("\\", "/").strip("/")
    if not normalized.startswith("godot-docs/") or ".." in Path(normalized).parts:
        return ""
    path = PROJECT_ROOT / normalized
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _doc_excerpt(text: str, query: str = "", limit: int = 2400) -> str:
    if query:
        lower = text.lower()
        index = lower.find(query.lower())
        if index >= 0:
            start = max(0, index - limit // 3)
            return text[start : start + limit]
    return text[:limit]


def _search_godot_docs(query: str) -> list[str]:
    snippets: list[str] = []
    for rel in GODOT_DOCS:
        text = _read_godot_doc(rel)
        if query.lower() in text.lower():
            snippets.append(f"--- {rel} ---\n{_doc_excerpt(text, query)}")
            if len(snippets) >= 3:
                break
    return snippets


def _planning_chat_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> str:
    answer = f"\nUser answer/selection context:\n{session.answer}\n" if session.answer else ""
    return f"""
User request:
{session.instruction}

Project slug: {session.project_slug}
Project path: {project_dir}
Selected Hastur skill: {session.skill_name}
Uploaded files: {json.dumps(_public_attachment_list(session.attachments), ensure_ascii=False)}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
Workflow mode: {session.workflow_mode}
{answer}

{_attachment_context_text(session)}

Capability registry:
{_capability_registry_text()}

Available skills:
{skill_listing_for_prompt(session.project_slug)}

Godot docs index:
{_docs_summary(docs)}

Reply to the user in natural language. Be concise and direct. Do not ask for broker tokens, broker URLs, executor IDs, or default ports; this app checks and binds that private runtime context automatically. Explain only what you are thinking about now. Do not include JSON, GDScript, modal content, or fake execution results.
""".strip()


def _resume_chat_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
) -> str:
    plan = _public_plan(session.plan or {})
    selection = "\n".join(
        part
        for part in [
            f"Selected choice: {session.choice_id}" if session.choice_id else "",
            f"Custom reply: {session.answer}" if session.answer else "",
            f"Revision request: {session.revision_request}" if session.revision_request else "",
        ]
        if part
    )
    return f"""
The user just responded to an abstract modal. Continue the public work stream before any code generation or Hastur execution.

User request:
{session.instruction}

User modal response:
{selection or "No custom text."}

Current plan:
{json.dumps(plan, ensure_ascii=False)}

Project slug: {session.project_slug}
Project path: {project_dir}
Selected Hastur skill: {session.skill_name}
Connected executors: {json.dumps(executors, ensure_ascii=False)}

{_attachment_context_text(session)}

Capability registry:
{_capability_registry_text()}

Available skills:
{skill_listing_for_prompt(session.project_slug)}

Godot docs index:
{_docs_summary(docs)}

Reply in one or two natural-language sentences about what you are doing next. Do not include JSON, GDScript, modal content, tool tags, or fake execution results.
""".strip()


def _planning_chat_system_prompt() -> str:
    return "You are the LLM side of a Godot/Hastur agent. Stream natural user-facing text only."


def _task_prompt(
    session: HasturTaskSession,
    project_dir: Path,
    docs: list[dict[str, str]],
    skill_text: str,
    executors: dict[str, Any],
    context_snippets: list[str] | None = None,
) -> str:
    answer = f"\nUser answer/selection context:\n{session.answer}\n" if session.answer else ""
    mode_rule = (
        'Workflow mode is "plan": design a user-visible plan only. Do not write GDScript. Do not execute through Hastur. '
        'Return mode "plan", steps, assistant-facing summary/final text, and a user_prompt that instantiates the abstract modal tool for plan confirmation.'
        if session.workflow_mode == "plan"
        else 'Workflow mode is "auto": decide whether direct execution, a visible plan, or a modal question is needed.'
    )
    return f"""
You are creating an execution decision for a local Godot project controlled through Hastur.
The agent only provides abstract capabilities. You decide whether and how to use them.
{mode_rule}
For trivial, low-risk, single-action tasks with no missing information, set mode to "direct" and return complete GDScript in code.
For complex, multi-step, risky, destructive, start/stop/play/autoload/rollback, or ambiguous tasks, set mode to "plan" or "ask".
Do not include a visible plan unless you decide the user benefits from seeing or confirming it.
Complex scene-building tasks should be described as coherent implementation phases, not tiny code-generation steps.
For read-only inspection requests, plan the minimum steps needed to return the requested factual result; do not turn the final answer into a repeat of the task.
Any direct GDScript must call executeContext.output("result", text) at least once with non-empty user-displayable text.
For direction, flip, upside-down, continent, map, terrain, or orientation fixes, first identify the exact target node/resource and intended correction. If the meaning or target is unclear, instantiate the modal tool to ask before modifying. When modifying, require before/after evidence in the output.
{_visual_clarity_guidance()}
{_mesh_surface_orientation_guidance()}
{_godot_coordinate_summary()}
Use user_prompt only by instantiating the abstract modal tool. All modal title, body, labels, and choices must come from you.
If you need more context, return context_requests first instead of guessing. The agent will fetch only the requested local snippets and call you again.

Project slug: {session.project_slug}
Project path: {project_dir}
Selected Hastur skill: {session.skill_name}
Uploaded files: {json.dumps(_public_attachment_list(session.attachments), ensure_ascii=False)}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
{answer}

{_attachment_context_text(session)}

Capability registry:
{_capability_registry_text()}

Available skills:
{skill_listing_for_prompt(session.project_slug)}

Godot docs index:
{_docs_summary(docs)}

Loaded skill/context snippets:
{_context_snippets_text(skill_text, context_snippets or [])}

User request:
{session.instruction}

Return JSON only:
{{
  "context_requests": [
    {{"type": "skill", "name": "skill-name"}},
    {{"type": "godot_doc", "path": "godot-docs/path/file.rst.txt", "query": "optional keyword"}},
    {{"type": "godot_doc_search", "query": "optional keyword"}}
  ],
  "mode": "direct",
  "complexity": "simple",
  "execution_strategy": "single_batch",
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
      "requires_confirmation": false
    }}
  ],
  "task_breakdown": [
    {{"id": "task_1", "title": "one user-visible task title", "goal": "what this task will accomplish", "kind": "editor", "status": "pending", "requires_confirmation": false}}
  ],
  "code": "complete GDScript only when mode is direct; otherwise empty",
  "final": "short completion summary"
}}

Always classify task complexity. Use "simple" only for one clear low-risk action or inspection; use "multi_step" for tasks that should be solved in phases; use "ambiguous" when user intent or target is unclear; use "risky" for destructive or interruption-prone changes.
Always return task_breakdown. If simple, return exactly one task. If multi_step, return the smallest useful sequence of user-understandable tasks.
Set execution_strategy to "single_batch" only for simple tasks or genuinely atomic tightly coupled edits. For multi_step tasks with multiple task_breakdown items, prefer "sequential_subtasks" so each subtask is executed through Hastur, observed through its output, and fed back before generating the next subtask script. Use "ask_first" when a modal question is required before execution.
Set mode to "direct" when no visible plan or user prompt is needed. In direct mode, steps must be empty and code must be executable GDScript for one Hastur editor execution.
Set mode to "plan" only when you decide a visible plan is useful or user approval is needed.
Set mode to "ask" when missing information must be collected before code or planning.
Set question only when information is required before planning safely.
Set requires_user_approval or step requires_confirmation for delete/remove/reset/start/stop/play/autoload/rollback operations.
Keep choices empty unless the user needs to decide between materially different approaches.
If user_prompt is not null, it must be a modal object with title, body, optional input_label, requires_input, and optional choices. User-facing choices must come from you, not fixed defaults. Choose however many concrete options the task actually needs; do not pad or truncate the list to two, and do not include a choice for "I will type/provide my own answer/path/details".
The modal custom reply box is always visible to the user for alternate instructions or revisions. When choices are present, input_label should describe alternate instructions, not the main question. Set requires_input true only when custom text is mandatory.
If workflow mode is "plan", code must be empty and user_prompt must ask the user whether to approve or revise your plan.
Set read_only true for inspect/list/read tasks that should not mutate the project.
""".strip()


def _task_system_prompt() -> str:
    return "You are the LLM planner for a Godot/Hastur agent. Output JSON only. Never expose secrets."


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
Every batch must call executeContext.output("result", text) at least once with non-empty user-displayable text. This is required for read-only and mutating tasks.
{_visual_clarity_guidance()}
{_mesh_surface_orientation_guidance()}
Use EditorInterface and scene/node APIs consistent with the local Godot docs.
For inspection/list/read requests, do not mutate the scene; collect the requested facts and return them with executeContext.output("result", text). If the user asks for the scene tree, include the complete open edited scene tree in that output.
For mutating scene tasks, save changed scenes/resources when appropriate and return a concise summary of changed nodes/resources with executeContext.output("result", text).
For direction, flip, upside-down, inverted, continent, map, terrain, or orientation fixes, inspect the target node/resource first and include Before: ... and After: ... evidence in executeContext.output("result", text). If the target or intended correction is unclear, the plan should have asked through the modal before this code generation step.
For front/back, transparent face, material, normal, cull, winding, mesh, or terrain surface fixes, inspect the target MeshInstance3D, mesh surfaces, material cull_mode, normals, and triangle winding first; include Before: ... and After: ... evidence in executeContext.output("result", text).
{_godot_coordinate_summary()}

Project path: {project_dir}
Selected skill: {session.skill_name}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
User request: {session.instruction}
User answer context: {session.answer}
Attachment observations: {session.vision_summary or "None"}
{adjustment}

Confirmed plan:
{json.dumps(_public_plan(plan), ensure_ascii=False)}

Prior execution results:
{json.dumps(_compact_execution_results(session.prior_results[-3:]), ensure_ascii=False)}

Relevant docs:
{_docs_summary(docs)}

Loaded skill context:
{_context_snippets_text(skill_text, [])}

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
The previous run may have compiled and run successfully but failed the output contract. The corrected batch must call executeContext.output("result", text) at least once with non-empty user-displayable text. Scene-tree requests must output the complete scene tree.
If the task is a direction, flip, upside-down, inverted, continent, map, terrain, or orientation fix, the corrected batch must output Before: ... and After: ... evidence for the exact target node/resource.
For front/back, transparent face, material, normal, cull, winding, mesh, or terrain surface fixes, the corrected batch must output Before: ... and After: ... evidence for the target MeshInstance3D, mesh surface/material state, and the applied fix.
{_visual_clarity_guidance()}
{_mesh_surface_orientation_guidance()}

Repair attempt: {attempt}
Project path: {project_dir}
Selected skill: {session.skill_name}
Connected executors: {json.dumps(executors, ensure_ascii=False)}
User request: {session.instruction}
User answer context: {session.answer}
Attachment observations: {session.vision_summary or "None"}
Post-execution feedback if any: {session.post_execution_feedback}

Confirmed plan:
{json.dumps(_public_plan(plan), ensure_ascii=False)}

Latest error:
{json.dumps(_result_error_context(prior_results[-1] if prior_results else {}), ensure_ascii=False)}

Recent execution results:
{json.dumps(_compact_execution_results(prior_results[-3:]), ensure_ascii=False)}

Relevant docs:
{_docs_summary(docs)}

Loaded skill context:
{_context_snippets_text(skill_text, [])}

Return JSON only:
{{"message": "brief internal summary", "code": "corrected complete GDScript snippet or empty string"}}
""".strip()


def _load_godot_docs() -> list[dict[str, str]]:
    docs = []
    for rel in GODOT_DOCS:
        path = PROJECT_ROOT / rel
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        title = next((line.strip() for line in text.splitlines() if line.strip() and not line.startswith("..")), Path(rel).name)
        docs.append({"path": rel, "title": title, "text": text[:700]})
    return docs


def _docs_context(docs: list[dict[str, str]]) -> str:
    return "\n\n".join(f"--- {item['path']} ---\n{item['text']}" for item in docs)


def _docs_summary(docs: list[dict[str, str]]) -> str:
    return "\n".join(f"- {item['path']} ({item.get('title') or Path(item['path']).name}): {item['text'][:220].replace(chr(10), ' ')}" for item in docs)


def _visual_clarity_guidance() -> str:
    return (
        "Visual clarity rule for lighting, camera, material, environment, and post-processing tasks: "
        "prioritize a clear editor/game preview over cinematic mood. Do not make the scene darker, blurrier, foggier, "
        "or more overexposed than before. Avoid enabling DOF blur, fog, volumetric fog, high glow/bloom, heavy SSAO, "
        "high contrast, aggressive color grading, auto exposure, or very dark backgrounds unless the user explicitly asks for that exact effect. "
        "For clear prototype previews, prefer a WorldEnvironment with ambient_light_energy around 0.6-1.2, "
        "background_energy_multiplier around 0.8-1.2, tonemap_exposure around 0.8-1.1, tonemap white/AgX white high enough to prevent blown highlights, "
        "CameraAttributes auto_exposure_enabled=false, dof_blur_near_enabled=false, dof_blur_far_enabled=false, and DirectionalLight3D light_energy around 0.7-1.5. "
        "If the user asks to improve visibility or clarity, first disable/neutralize blur/fog/excessive glow/auto exposure before adding effects. "
        "Output only concise Before/After evidence for key visibility settings such as environment, exposure, glow, fog, DOF, light energy, camera distance, and save status; keep executeContext.output under 700 characters."
    )


def _mesh_surface_orientation_guidance() -> str:
    return (
        "Mesh surface orientation rule for continent, terrain, map, front/back, transparent face, upside-down material, normals, culling, and winding tasks: "
        "Godot ArrayMesh triangle front faces use clockwise winding. If the front/top appears transparent while the back/underside shows material, treat it as a mesh winding/normal/cull/material-alpha problem, not as a lighting or post-processing problem. "
        "First inspect the exact MeshInstance3D, mesh surface count, surface material/material_override, material cull_mode, transparency/alpha, and representative triangle normals or vertex order. "
        "Do not claim the fix from a successful broker run alone. The output must include concise Before/After evidence for the intended target node path, cull_mode, alpha/transparency, normal direction or winding, and explicit top/front visibility after the fix using a field such as top_visible=true, front_visible=true, or visible_from_above=true. "
        "Do not fix an incidental tree, decoration, or child mesh when the user asked about the continent, terrain, map, or landmass; if the intended target is ambiguous, ask first instead of modifying the first invisible mesh found. "
        "Prefer correcting triangle winding/normals so the visible terrain/continent top faces upward/outward, then use opaque material settings such as alpha 1.0 and disabled transparency with normal back-face culling. "
        "Do not use CULL_DISABLED/two-sided material as the only fix unless the user explicitly asks for a two-sided surface or the mesh cannot be rebuilt; if used as a temporary visibility fallback, say so in the output. "
        "For generated flat terrain or continent maps, top surface normals should generally have positive Y; reversing every triangle's index order is the usual repair when the underside is visible and the top is culled."
    )


def _emit_skill_invocation_notice(session: HasturTaskSession, name: str, source: str) -> None:
    if not name or name in session.announced_skills:
        return
    session.announced_skills.add(name)
    message = f"Invoked Claude Code skill: /{name}"
    _emit(
        session,
        "thought_delta",
        session.state,
        message,
        {"delta": message, "kind": "skill", "skill_name": name, "source": source},
    )


def _godot_coordinate_summary() -> str:
    return (
        "Godot 3D coordinates: right-handed; +Y is up; camera forward is -Z; "
        "+X is right; +Z is back. Oriented 3D assets conventionally face +Z, "
        "so use look_at(..., use_model_front=true) or Vector3.MODEL_* constants "
        "when working in an asset's local forward direction. For maps/terrain, "
        "+X east, -X west, +Z south, -Z north."
    )


def _normalize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    mode = str(plan.get("mode") or "").strip().lower()
    steps = plan.get("steps")
    if not isinstance(steps, list):
        legacy_code = str(plan.get("code") or "").strip()
        if legacy_code:
            steps = []
            mode = mode or "direct"
        else:
            steps = [{"title": plan.get("message") or "Respond", "goal": plan.get("message") or "", "type": "editor", "legacy_code": legacy_code}]
    if mode not in {"direct", "plan", "ask"}:
        mode = "direct" if str(plan.get("code") or "").strip() and not steps else "plan"
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
            }
        )
    choices = plan.get("choices") if isinstance(plan.get("choices"), list) else []
    user_prompt = plan.get("user_prompt") if isinstance(plan.get("user_prompt"), dict) else None
    complexity = str(plan.get("complexity") or "").strip()
    if complexity not in {"simple", "multi_step", "ambiguous", "risky"}:
        complexity = _infer_complexity(plan, normalized_steps)
    task_breakdown = _normalize_task_breakdown(plan, normalized_steps, complexity)
    execution_strategy = _normalize_execution_strategy(plan, mode, complexity, task_breakdown)
    return {
        "mode": mode,
        "complexity": complexity,
        "execution_strategy": execution_strategy,
        "summary": str(plan.get("summary") or plan.get("message") or "Plan ready."),
        "question": str(plan.get("question") or ""),
        "read_only": bool(plan.get("read_only", False)),
        "requires_user_approval": bool(plan.get("requires_user_approval", False)),
        "user_prompt": _normalize_user_prompt(user_prompt) if user_prompt else None,
        "choices": [_normalize_choice(choice, index) for index, choice in enumerate(choices)],
        "steps": normalized_steps,
        "task_breakdown": task_breakdown,
        "code": str(plan.get("code") or "").strip(),
        "final": str(plan.get("final") or ""),
    }


def _enforce_workflow_mode(session: HasturTaskSession, plan: dict[str, Any]) -> dict[str, Any]:
    if session.workflow_mode != "plan":
        return plan
    enforced = dict(plan)
    enforced["mode"] = "plan"
    enforced["code"] = ""
    enforced["requires_user_approval"] = True
    if not enforced.get("steps"):
        summary = str(enforced.get("summary") or "Review the requested Godot task.")
        enforced["steps"] = [
            {
                "title": summary,
                "goal": "Review and approve the plan before any Hastur execution.",
                "type": "editor",
                "executor_id": "",
                "requires_confirmation": True,
            }
        ]
    if not enforced.get("task_breakdown"):
        enforced["task_breakdown"] = [
            {
                "id": "task_1",
                "title": str(enforced.get("summary") or "Review plan"),
                "goal": "Confirm or revise the plan before execution.",
                "kind": "editor",
                "status": "pending",
                "requires_confirmation": True,
            }
        ]
    return enforced


def _infer_complexity(plan: dict[str, Any], steps: list[dict[str, Any]]) -> str:
    if str(plan.get("mode") or "") == "ask":
        return "ambiguous"
    if plan.get("requires_user_approval"):
        return "risky"
    if len(steps) > 1:
        return "multi_step"
    return "simple"


def _normalize_execution_strategy(
    plan: dict[str, Any],
    mode: str,
    complexity: str,
    task_breakdown: list[dict[str, Any]],
) -> str:
    value = str(plan.get("execution_strategy") or "").strip()
    if mode == "ask":
        return "ask_first"
    if complexity == "multi_step" and len(task_breakdown) > 1 and not str(plan.get("code") or "").strip():
        return "sequential_subtasks"
    if value in {"single_batch", "sequential_subtasks", "ask_first"}:
        return value
    return "single_batch"


def _normalize_task_breakdown(plan: dict[str, Any], steps: list[dict[str, Any]], complexity: str) -> list[dict[str, Any]]:
    raw_tasks = plan.get("task_breakdown") if isinstance(plan.get("task_breakdown"), list) else []
    source = raw_tasks or steps or [{"title": plan.get("summary") or plan.get("message") or "Run task", "goal": plan.get("summary") or ""}]
    tasks: list[dict[str, Any]] = []
    for index, task in enumerate(source, start=1):
        if not isinstance(task, dict):
            task = {"title": str(task), "goal": str(task)}
        task_id = str(task.get("id") or f"task_{index}").strip() or f"task_{index}"
        status = str(task.get("status") or "pending").strip()
        if status not in {"pending", "active", "completed", "failed", "skipped"}:
            status = "pending"
        tasks.append(
            {
                "id": task_id,
                "title": str(task.get("title") or task.get("summary") or f"Task {index}"),
                "goal": str(task.get("goal") or task.get("description") or ""),
                "kind": str(task.get("kind") or task.get("type") or "editor"),
                "status": status,
                "requires_confirmation": bool(task.get("requires_confirmation")),
            }
        )
    if complexity == "simple" and len(tasks) > 1:
        first = tasks[0]
        first["title"] = str(plan.get("summary") or first["title"])
        first["goal"] = str(plan.get("summary") or first.get("goal") or "")
        return [first]
    return tasks


def _normalize_user_prompt(prompt: dict[str, Any]) -> dict[str, Any]:
    choices = prompt.get("choices") if isinstance(prompt.get("choices"), list) else []
    requires_input = prompt.get("requires_input")
    concrete_choices = [choice for choice in choices if not _is_custom_reply_choice(choice)]
    return {
        "title": str(prompt.get("title") or ""),
        "body": str(prompt.get("body") or prompt.get("message") or ""),
        "input_label": str(prompt.get("input_label") or ""),
        "choices": [_normalize_choice(choice, index) for index, choice in enumerate(concrete_choices)],
        "requires_input": bool(requires_input) if requires_input is not None else False,
    }


def _is_custom_reply_choice(choice: Any) -> bool:
    if isinstance(choice, dict):
        text = " ".join(str(choice.get(key) or "") for key in ("id", "label", "title", "description", "details", "action"))
    else:
        text = str(choice)
    normalized = text.strip().lower()
    if not normalized:
        return False
    custom_terms = [
        "custom option",
        "custom reply",
        "custom plan",
        "custom input",
        "freeform",
        "free-form",
        "manual input",
        "enter details",
        "type details",
        "provide details",
        "provide path",
        "input path",
        "user input",
        "i will input",
        "i will provide",
        "let me type",
        "let me enter",
        "我来输入",
        "我输入",
        "手动输入",
        "自定义方案",
        "自定义意见",
        "自定义输入",
        "其他意见",
        "其他方案",
        "输入路径",
        "提供路径",
        "填写路径",
    ]
    return any(term in normalized for term in custom_terms)


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
        "mode": plan.get("mode", "plan"),
        "complexity": plan.get("complexity", "simple"),
        "execution_strategy": plan.get("execution_strategy", "single_batch"),
        "summary": plan.get("summary", ""),
        "read_only": bool(plan.get("read_only", False)),
        "steps": [_public_step(step, index) for index, step in enumerate(plan.get("steps") or [])],
        "task_breakdown": [_public_task(task) for task in plan.get("task_breakdown") or []],
        "final": plan.get("final", ""),
    }


def _public_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": task.get("id") or "",
        "title": task.get("title") or "",
        "goal": task.get("goal") or "",
        "kind": task.get("kind") or "editor",
        "status": task.get("status") or "pending",
        "requires_confirmation": bool(task.get("requires_confirmation")),
    }


def _public_step(step: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index + 1,
        "title": step.get("title") or f"Step {index + 1}",
        "goal": step.get("goal") or "",
        "type": step.get("type") or "editor",
        "requires_confirmation": bool(step.get("requires_confirmation")),
    }


def _plan_requires_review(session: HasturTaskSession, plan: dict[str, Any]) -> bool:
    if session.workflow_mode == "plan" and (plan.get("steps") or plan.get("requires_user_approval")):
        return True
    if _is_read_only_plan(session, plan):
        return False
    if plan.get("execution_strategy") == "ask_first":
        return True
    if plan.get("complexity") in {"multi_step", "ambiguous", "risky"} and str(plan.get("mode") or "") == "plan":
        return True
    steps = plan.get("steps") or []
    return bool(
        plan.get("requires_user_approval")
        or any(step.get("requires_confirmation") for step in steps)
    )


def _prompt_pending_state(session: HasturTaskSession, plan: dict[str, Any]) -> str:
    mode = str(plan.get("mode") or "").lower()
    has_executable_work = bool(plan.get("steps") or _direct_plan_code(plan))
    if mode == "ask" or (plan.get("execution_strategy") == "ask_first" and not has_executable_work):
        return "pre_execution_prompt"
    return "plan_confirmation" if _plan_requires_review(session, plan) or session.workflow_mode == "plan" else "pre_execution_prompt"


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
    return bool(session.execution_complete and not session.final_ready and _plan_needs_visual_check(plan))


def _instruction_has_skill_prefix(instruction: str) -> bool:
    return bool(instruction.strip().startswith("/"))


def _default_skill_name() -> str:
    names = {skill.name for skill in list_hastur_skills()}
    return DEFAULT_SKILL_NAME if DEFAULT_SKILL_NAME in names else (next(iter(names), DEFAULT_SKILL_NAME))


def _selected_prompt_choice(session: HasturTaskSession) -> dict[str, Any]:
    choices = session.pending_prompt.get("choices") if isinstance(session.pending_prompt, dict) else []
    if not isinstance(choices, list):
        return {}
    return next((choice for choice in choices if isinstance(choice, dict) and choice.get("id") == session.choice_id), {})


def _append_selected_choice_context(answer: str, choice_id: str, choice: dict[str, Any]) -> str:
    lines = [answer.strip()] if answer.strip() else []
    lines.append(f"Selected option: {choice_id}")
    label = str(choice.get("label") or "").strip()
    description = str(choice.get("description") or "").strip()
    action = str(choice.get("action") or "").strip()
    if label:
        lines.append(f"Selected option label: {label}")
    if description:
        lines.append(f"Selected option details: {description}")
    if action:
        lines.append(f"Selected option action: {action}")
    return "\n".join(lines)


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
    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def _should_announce_plan(plan: dict[str, Any]) -> bool:
    return str(plan.get("mode") or "plan") != "direct"


def _direct_plan_code(plan: dict[str, Any]) -> str:
    if str(plan.get("mode") or "").lower() != "direct":
        return ""
    return str(plan.get("code") or "").strip()


def _emit_generic_user_prompt(session: HasturTaskSession, prompt: dict[str, Any], pending: str = "pre_execution_prompt") -> None:
    detail = {
        "title": str(prompt.get("title") or ""),
        "body": str(prompt.get("body") or prompt.get("message") or ""),
        "input_label": str(prompt.get("input_label") or ""),
        "choices": prompt.get("choices") or [],
        "requires_input": bool(prompt.get("requires_input", False)),
    }
    session.pending = pending
    _emit_user_prompt(session, detail["body"], detail)


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
    session.state = state if state in TASK_STATES else session.state
    if event_type in {"execution", "repair", "repair_result", "execution_result"}:
        _emit_task_progress(session, message="Working on the current task.")


def _emit_task_breakdown(session: HasturTaskSession, plan: dict[str, Any]) -> None:
    tasks = plan.get("task_breakdown") if isinstance(plan.get("task_breakdown"), list) else []
    if not tasks:
        return
    detail = _task_progress_detail(plan)
    _emit(session, "task_breakdown", session.state, "Task list ready.", detail)


def _emit_task_progress(session: HasturTaskSession, message: str = "Task progress updated.") -> None:
    if not session.plan:
        return
    detail = _task_progress_detail(session.plan)
    _emit(session, "task_progress", session.state, message, detail)


def _task_progress_detail(plan: dict[str, Any]) -> dict[str, Any]:
    tasks = [_public_task(task) for task in plan.get("task_breakdown") or []]
    current = next((task["id"] for task in tasks if task.get("status") == "active"), "")
    return {
        "complexity": plan.get("complexity", "simple"),
        "execution_strategy": plan.get("execution_strategy", "single_batch"),
        "current_task_id": current,
        "tasks": tasks,
    }


def _set_task_status(session: HasturTaskSession, task_id: str, status: str, state: str, message: str) -> None:
    if not session.plan:
        return
    tasks = session.plan.get("task_breakdown") if isinstance(session.plan.get("task_breakdown"), list) else []
    if not tasks:
        return
    session.current_task_id = task_id if status == "active" else session.current_task_id
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = status
        elif status == "active" and task.get("status") == "active":
            task["status"] = "pending"
    session.state = state if state in TASK_STATES else session.state
    _emit_task_progress(session, message=message)


def _complete_all_tasks(session: HasturTaskSession, status: str = "completed") -> None:
    if not session.plan:
        return
    for task in session.plan.get("task_breakdown") or []:
        if task.get("status") not in {"completed", "failed"}:
            task["status"] = status
    _emit_task_progress(session, message="Task progress updated.")


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
    text = _sanitize_public_thought(text)
    if not text:
        return
    _emit(session, "thought_delta", state or session.state, text, {"delta": text, "kind": kind, "detail": detail or {}})


def _sanitize_public_thought(text: str) -> str:
    if not text:
        return ""
    stripped = text.strip()
    lower = stripped.lower()
    if not stripped:
        return ""
    if "```" in stripped or "<tool" in lower or "</tool" in lower:
        return ""
    if _looks_like_gdscript(stripped):
        return ""
    if re.search(r"(?m)^\s*(extends|@tool|class_name|func|var|const|if|for|while)\b", stripped):
        return ""
    if "executecontext" in lower or "editorinterface" in lower or "projectsettings" in lower:
        return ""
    json_markers = ['"code"', '"steps"', '"context_requests"', '"user_prompt"', '"mode"', '"choices"', '"broker_response"']
    if stripped.startswith(("{", "[")) or any(marker in lower for marker in json_markers):
        return ""
    return text


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
            "no connected hastur executor",
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
        "broker_response": _compact_broker_response(result.get("broker_response")),
        "gdscript_excerpt": str(result.get("gdscript") or "")[:4000],
        "output_contract": result.get("output_contract"),
    }


def _compact_broker_response(value: Any) -> dict[str, Any]:
    outputs = _extract_output_pairs(value)
    return {
        "outputs": [(key, _clip_text(text, 1200)) for key, text in outputs[:6]],
        "errors": _clip_text(_broker_error_text(value), 1600),
    }


def _compact_execution_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for result in results:
        outputs = _extract_output_pairs(result.get("broker_response"))
        compact.append(
            {
                "success": result.get("success"),
                "message": _clip_text(str(result.get("message") or ""), 900),
                "outputs": [(key, _clip_text(value, 1200)) for key, value in outputs[:6]],
                "output_contract": result.get("output_contract"),
                "broker_error": _clip_text(_broker_error_text(result.get("broker_response")), 1200),
                "gdscript_excerpt": _clip_text(str(result.get("gdscript") or ""), 2200),
            }
        )
    return compact


def _broker_error_text(value: Any) -> str:
    if isinstance(value, dict):
        pieces = []
        for key in ("error", "message", "stderr", "exception"):
            if value.get(key):
                pieces.append(str(value.get(key)))
        for nested in value.values():
            nested_text = _broker_error_text(nested)
            if nested_text:
                pieces.append(nested_text)
        return "\n".join(dict.fromkeys(pieces))
    if isinstance(value, list):
        return "\n".join(filter(None, (_broker_error_text(item) for item in value)))
    return ""


def _clip_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n...[clipped]"


def _missing_output_contract_result(
    session: HasturTaskSession,
    plan: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any] | None:
    output_text = _result_displayable_text(result)
    needs_before_after = _requires_before_after_evidence(session, plan)
    needs_mesh_orientation = _requires_mesh_surface_orientation_evidence(session, plan)
    quality_reason = _output_quality_failure_reason(output_text, needs_mesh_orientation)
    if output_text and quality_reason:
        reason = quality_reason
    elif output_text and (
        (not needs_before_after or _has_before_after_evidence(output_text))
        and (not needs_mesh_orientation or _has_mesh_surface_orientation_evidence(output_text))
    ):
        return None
    elif output_text:
        if needs_mesh_orientation and not _has_mesh_surface_orientation_evidence(output_text):
            reason = (
                "The task returned output but did not prove the mesh surface orientation fix on the intended target. "
                "It must include target path, material/cull/alpha state, winding or normal evidence, and explicit top/front visibility after the fix."
            )
        else:
            reason = "The task returned output but did not include required before/after evidence for the target node or resource."
    else:
        reason = "The task completed through Hastur but returned no non-empty executeContext.output entries."
    return {
        "success": False,
        "message": _missing_output_message(session, plan),
        "broker_response": result.get("broker_response"),
        "gdscript": result.get("gdscript"),
        "output_contract": {
            "required": True,
            "before_after_required": needs_before_after,
            "mesh_surface_orientation_required": needs_mesh_orientation,
            "reason": reason,
            "original_success": bool(result.get("success")),
            "original_message": str(result.get("message") or ""),
        },
    }


def _output_quality_failure_reason(output_text: str, needs_mesh_orientation: bool) -> str:
    if not output_text:
        return ""
    lower = output_text.lower()
    if "[truncated:" in lower or "output exceeded" in lower:
        return "The task output was truncated. It must return concise evidence under the Hastur output limit."
    if len(output_text) > 800:
        return "The task output is too long. It must return concise evidence under 800 characters."
    if needs_mesh_orientation and "@editornode" in lower:
        return "The task output used an editor-internal path. Mesh orientation evidence must use a scene-relative target path."
    if needs_mesh_orientation and _mesh_before_claims_already_visible(output_text):
        return (
            "The mesh evidence says the target was already top/front visible before the fix. "
            "It did not reproduce the user's front-transparent/back-material problem and must inspect the real cause."
        )
    return ""


def _mesh_before_claims_already_visible(output_text: str) -> bool:
    lower = output_text.lower()
    match = re.search(r"before:(.*?)(?:\nafter:|after:|$)", lower, re.DOTALL)
    before = match.group(1) if match else lower
    claims_visible = any(term in before for term in ["top_visible=true", "front_visible=true", "visible_from_above=true"])
    if not claims_visible:
        return False
    bad_terms = [
        "top_visible=false",
        "front_visible=false",
        "visible_from_above=false",
        "cull=front",
        "cull_mode=front",
        "normal_y=-",
        "normy=-",
        "alpha=0",
        "transp=alpha",
        "transparency=alpha",
        "instance_transparency=1",
    ]
    return not any(term in before for term in bad_terms)


def _result_has_displayable_output(result: dict[str, Any]) -> bool:
    return bool(_result_displayable_text(result))


def _result_displayable_text(result: dict[str, Any]) -> str:
    return "\n".join(value.strip() for _, value in _extract_output_pairs(result.get("broker_response")) if value and value.strip())


def _missing_output_message(session: HasturTaskSession, plan: dict[str, Any]) -> str:
    if _requires_before_after_evidence(session, plan):
        label = "before/after evidence"
    else:
        label = "scene tree" if _is_scene_tree_request(session, plan) else "task result"
    return (
        f"Hastur ran the batch, but it did not return a displayable {label}. "
        'The batch must call executeContext.output("result", text) with the real result, so I did not fabricate an answer.'
    )


def _is_scene_tree_request(session: HasturTaskSession, plan: dict[str, Any]) -> bool:
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
    return any(term in text for term in ["scene tree", "node tree", "\u573a\u666f\u6811", "\u8282\u70b9\u6811"])


def _requires_before_after_evidence(session: HasturTaskSession, plan: dict[str, Any]) -> bool:
    if _is_read_only_plan(session, plan):
        return False
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
    direct_issue_terms = [
        "flip",
        "flipped",
        "upside down",
        "upside-down",
        "inverted",
        "reverse",
        "reversed",
        "orientation",
        "direction",
        "rotate",
        "rotated",
        "vertical",
        "front",
        "back",
        "backface",
        "transparent",
        "normal",
        "normals",
        "cull",
        "culling",
        "winding",
        "\u4e0a\u4e0b",
        "\u98a0\u5012",
        "\u7ffb\u8f6c",
        "\u65b9\u5411",
        "\u6b63\u9762",
        "\u53cd\u9762",
        "\u80cc\u9762",
        "\u900f\u660e",
        "\u6cd5\u7ebf",
    ]
    resource_terms = [
        "material",
        "mesh",
        "surface",
        "terrain",
        "continent",
        "landmass",
        "map",
        "\u5927\u9646",
        "\u5730\u56fe",
        "\u8d34\u56fe",
        "\u6750\u8d28",
        "\u7f51\u683c",
    ]
    problem_terms = [
        "fix",
        "repair",
        "correct",
        "issue",
        "problem",
        "wrong",
        "not visible",
        "missing",
        "transparent",
        "front",
        "back",
        "\u4fee\u6b63",
        "\u4fee\u590d",
        "\u95ee\u9898",
        "\u4e0d\u5bf9",
        "\u9519",
        "\u900f\u660e",
        "\u6b63\u9762",
        "\u80cc\u9762",
    ]
    return any(term in text for term in direct_issue_terms) or (
        any(term in text for term in resource_terms) and any(term in text for term in problem_terms)
    )


def _has_before_after_evidence(text: str) -> bool:
    lower = text.lower()
    before_terms = ["before:", "before =", "before=", "old:", "previous:", "\u4fee\u6539\u524d", "\u4fee\u590d\u524d", "\u539f\u59cb", "\u4e4b\u524d", "\u5f53\u524d"]
    after_terms = ["after:", "after =", "after=", "new:", "updated:", "\u4fee\u6539\u540e", "\u4fee\u590d\u540e", "\u4e4b\u540e", "\u5b8c\u6210\u540e"]
    return any(term in lower for term in before_terms) and any(term in lower for term in after_terms)


def _requires_mesh_surface_orientation_evidence(session: HasturTaskSession, plan: dict[str, Any]) -> bool:
    if _is_read_only_plan(session, plan):
        return False
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
    surface_terms = [
        "front",
        "back",
        "backface",
        "transparent",
        "normal",
        "normals",
        "cull",
        "culling",
        "winding",
        "surface",
        "mesh",
        "material",
        "top",
        "above",
        "underside",
        "\u6b63\u9762",
        "\u53cd\u9762",
        "\u80cc\u9762",
        "\u900f\u660e",
        "\u6cd5\u7ebf",
        "\u7f51\u683c",
        "\u8868\u9762",
        "\u6750\u8d28",
        "\u4e0a\u65b9",
        "\u4e0a\u9762",
        "\u4e0b\u65b9",
        "\u4e0b\u9762",
        "\u4e0a\u4e0b",
        "\u98a0\u5012",
    ]
    fix_terms = [
        "fix",
        "repair",
        "correct",
        "issue",
        "problem",
        "wrong",
        "\u4fee\u6b63",
        "\u4fee\u590d",
        "\u95ee\u9898",
        "\u4e0d\u5bf9",
        "\u9519",
    ]
    return any(term in text for term in surface_terms) and any(term in text for term in fix_terms)


def _has_mesh_surface_orientation_evidence(text: str) -> bool:
    lower = text.lower()
    target_terms = [
        "path=",
        "target=",
        "node=",
        "meshinstance3d",
        "terrain",
        "continent",
        "landmass",
        "map",
        "\u8def\u5f84",
        "\u76ee\u6807",
        "\u8282\u70b9",
        "\u5730\u5f62",
        "\u5927\u9646",
        "\u5730\u56fe",
    ]
    material_terms = [
        "cull",
        "cull_mode",
        "alpha",
        "transparency",
        "opaque",
        "material",
        "\u6750\u8d28",
        "\u900f\u660e",
        "\u4e0d\u900f\u660e",
    ]
    orientation_terms = [
        "normal",
        "normy",
        "normal_y",
        "winding",
        "clockwise",
        "rewind",
        "reverse",
        "indices",
        "\u6cd5\u7ebf",
        "\u7ed5\u5e8f",
        "\u987a\u65f6\u9488",
        "\u53cd\u8f6c",
    ]
    visibility_terms = [
        "top_visible=true",
        "front_visible=true",
        "visible_from_above=true",
        "above_visible=true",
        "top visible",
        "front visible",
        "from above visible",
        "\u4e0a\u65b9\u53ef\u89c1",
        "\u4e0a\u9762\u53ef\u89c1",
        "\u6b63\u9762\u53ef\u89c1",
    ]
    return (
        any(term in lower for term in target_terms)
        and any(term in lower for term in material_terms)
        and any(term in lower for term in orientation_terms)
        and any(term in lower for term in visibility_terms)
    )


def _final_task_response(session: HasturTaskSession, plan: dict[str, Any]) -> str:
    outputs: list[tuple[str, str]] = []
    for result in session.prior_results:
        outputs.extend(_extract_output_pairs(result.get("broker_response")))
    cleaned_outputs = [(key, value.strip()) for key, value in outputs if value and value.strip()]
    if cleaned_outputs:
        if len(cleaned_outputs) == 1:
            return cleaned_outputs[0][1][:12000]
        return "\n\n".join(f"{key}:\n{value[:12000]}" for key, value in cleaned_outputs)

    final = str(plan.get("final") or "").strip()
    if final:
        return final[:12000]
    return _missing_output_message(session, plan)


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
