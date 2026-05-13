from __future__ import annotations

import base64
import json
import re
from binascii import Error as Base64Error
from typing import Any

from app.models.llm_provider import get_llm_provider
from app.services.asset_service import get_project_dir
from app.services.hastur_service import apply_hastur_code, hastur_executors
from app.services.hastur_skill_service import get_skill_metadata, skill_listing_for_prompt
from app.services.settings_service import load_private_settings


CONFIRMATION_TERMS = [
    "autoload",
    "start game",
    "stop game",
    "play_main_scene",
    "stop_playing_scene",
    "remove",
    "delete",
    "reset",
    "rollback",
]


def chat_with_hastur_skill(
    project_slug: str,
    instruction: str,
    skill_name: str,
    images: list[dict[str, str]] | None = None,
    attachments: list[dict[str, str]] | None = None,
    execute: bool = False,
    confirmed: bool = False,
) -> dict[str, Any]:
    project_dir = get_project_dir(project_slug)
    settings = load_private_settings()
    skill_summary = _selected_skill_summary(skill_name, project_slug)
    executors = hastur_executors()
    uploaded = [*(images or []), *(attachments or [])]
    llm_images = [item for item in uploaded if str(item.get("media_type", "")).startswith("image/")]
    prompt = _build_prompt(
        project_slug=project_slug,
        project_dir=str(project_dir),
        instruction=instruction,
        skill_name=skill_name,
        skill_listing=skill_listing_for_prompt(project_slug),
        skill_summary=skill_summary,
        base_url=str(settings.get("hastur_base_url", "http://localhost:5302")),
        has_token=bool(settings.get("hastur_auth_token")),
        executors=executors,
        attachments=uploaded,
    )
    if execute:
        readiness = _execution_readiness(settings, executors)
        if readiness:
            return {
                "success": False,
                "skill": skill_name,
                "message": readiness,
                "requires_confirmation": False,
                "executors": executors,
                "llm_response": {},
            }
    llm = get_llm_provider()
    if llm_images:
        if not getattr(llm, "supports_images", False) or not hasattr(llm, "generate_text_with_images"):
            raise ValueError("The selected LLM provider does not support image input in this app.")
        raw = llm.generate_text_with_images(prompt, llm_images, system_prompt=_system_prompt())
    else:
        raw = llm.generate_text(prompt, system_prompt=_system_prompt())
    parsed = _parse_response(raw)
    requires_confirmation = parsed.get("requires_confirmation")
    if requires_confirmation is None:
        requires_confirmation = _requires_confirmation(instruction, parsed.get("code", ""))
    result: dict[str, Any] = {
        "success": True,
        "skill": skill_name,
        "message": parsed.get("message") or raw,
        "requires_confirmation": bool(requires_confirmation),
        "executors": executors,
        "attachments": _public_attachment_list(uploaded),
        "llm_response": parsed,
    }
    code = str(parsed.get("code") or "").strip()
    if execute and code:
        if result["requires_confirmation"] and not confirmed:
            result["success"] = False
            result["message"] = "This Hastur action needs confirmation before execution."
            return result
        execution = apply_hastur_code(
            project_slug,
            code,
            executor_id=parsed.get("executor_id") or None,
            executor_type=parsed.get("type") or None,
        )
        result["execution"] = execution.model_dump()
        result["success"] = execution.success
        result["message"] = execution.message
    return result


def encode_upload(filename: str, content_type: str | None, content: bytes) -> dict[str, str]:
    return {
        "filename": filename,
        "media_type": content_type or "application/octet-stream",
        "data": base64.b64encode(content).decode("ascii"),
    }


def _system_prompt() -> str:
    return (
        "You are the AI Game Development Agent. Use vendored Hastur skills exactly as workflow guidance. "
        "Never reveal auth tokens. Return concise JSON only."
    )


def _build_prompt(
    project_slug: str,
    project_dir: str,
    instruction: str,
    skill_name: str,
    skill_listing: str,
    skill_summary: str,
    base_url: str,
    has_token: bool,
    executors: dict[str, Any],
    attachments: list[dict[str, str]],
) -> str:
    return f"""
Use the lightweight capability and skill index below. Do not assume full skill bodies are loaded in this legacy endpoint.

Selected skill:
{skill_summary}

Available skills:
{skill_listing}

App-bound runtime context:
- Project slug: {project_slug}
- Project path: {project_dir}
- Broker base URL: {base_url}
- Auth token is available to the app: {has_token}
- Uploaded files in this request: {len(attachments)}
- Connected executors JSON: {json.dumps(executors, ensure_ascii=False)}

Uploaded file summary:
{_attachment_summary(attachments)}

User request:
{instruction}

Return JSON only in this shape:
{{
  "message": "short user-facing summary",
  "requires_confirmation": false,
  "executor_id": "optional executor id",
  "type": "editor or game if needed",
  "code": "optional GDScript snippet to execute through the Hastur broker"
}}

If the task can be answered without executing code, leave "code" empty.
If the task would start/stop a game, add/remove autoloads, delete data, reset state, or otherwise interrupt the user, set "requires_confirmation": true.
If executing code, call executeContext.output("result", text) with a non-empty user-displayable result.
Do not include auth tokens in the JSON.
""".strip()


def _selected_skill_summary(skill_name: str, project_slug: str) -> str:
    try:
        skill = get_skill_metadata(skill_name, project_slug=project_slug)
    except FileNotFoundError:
        return f"- /{skill_name}: metadata unavailable."
    parts = [
        f"- /{skill.name} ({skill.scope})",
        f"description={skill.description!r}" if skill.description else "",
        f"when_to_use={skill.when_to_use!r}" if skill.when_to_use else "",
        f"path={skill.path_label or skill.path}",
    ]
    return " ".join(part for part in parts if part)


def _parse_response(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    elif not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {"message": raw, "code": ""}
    except json.JSONDecodeError:
        return {"message": raw, "code": ""}


def _requires_confirmation(instruction: str, code: str) -> bool:
    haystack = f"{instruction}\n{code}".lower()
    return any(term in haystack for term in CONFIRMATION_TERMS)


def _execution_readiness(settings: dict[str, Any], executors: dict[str, Any]) -> str | None:
    if not settings.get("hastur_auth_token"):
        return "Hastur broker token is missing. Start the broker from the Management view first."
    if not executors.get("available"):
        return str(executors.get("message") or "Hastur broker is not reachable. Start the broker and open the Godot project.")
    data = executors.get("executors")
    if isinstance(data, dict):
        connected = data.get("data") or data.get("executors") or []
    else:
        connected = data or []
    if not connected:
        return "No Godot executor is connected. Open the generated project in Godot with the Hastur plugin enabled. Hastur uses broker TCP localhost:5301; Godot DAP localhost:6006 is only the debug adapter."
    return None


def _attachment_summary(attachments: list[dict[str, str]]) -> str:
    if not attachments:
        return "None"
    lines = []
    for item in attachments[:12]:
        filename = item.get("filename", "upload")
        media_type = item.get("media_type", "application/octet-stream")
        line = f"- {filename} ({media_type})"
        preview = _text_preview(item)
        if preview:
            line += f"\n  Preview: {preview}"
        lines.append(line)
    return "\n".join(lines)


def _text_preview(item: dict[str, str]) -> str:
    media_type = item.get("media_type", "")
    filename = item.get("filename", "")
    if not (media_type.startswith("text/") or filename.lower().endswith((".txt", ".md", ".json", ".csv", ".gd", ".tscn"))):
        return ""
    try:
        raw = base64.b64decode(item.get("data", ""), validate=True)
    except (Base64Error, ValueError):
        return ""
    text = raw.decode("utf-8", errors="replace").strip()
    return text[:1200]


def _public_attachment_list(attachments: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "filename": item.get("filename", "upload"),
            "media_type": item.get("media_type", "application/octet-stream"),
        }
        for item in attachments
    ]
