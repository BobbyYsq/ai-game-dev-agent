from __future__ import annotations

import json
import re
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, model_validator

from app.services.asset_service import get_project_dir
from app.services.settings_service import load_private_settings

OperationType = Literal[
    "create_scene",
    "open_scene",
    "create_node",
    "set_property",
    "attach_script",
    "save_scene",
    "import_asset_reference",
]


class GodotOperation(BaseModel):
    operation: OperationType
    target_scene: str | None = None
    node_type: str | None = None
    node_name: str | None = None
    parent_path: str = "."
    node_path: str | None = None
    property_name: str | None = None
    property_value: str | int | float | bool | None = None
    script_path: str | None = None
    asset_path: str | None = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        requirements = {
            "create_scene": ["target_scene"],
            "open_scene": ["target_scene"],
            "create_node": ["node_type", "node_name"],
            "set_property": ["node_path", "property_name"],
            "attach_script": ["node_path", "script_path"],
            "save_scene": [],
            "import_asset_reference": ["asset_path"],
        }
        missing = [field for field in requirements[self.operation] if not getattr(self, field)]
        if missing:
            raise ValueError(f"{self.operation} requires: {', '.join(missing)}")
        return self


class HasturExecuteResult(BaseModel):
    success: bool
    message: str
    broker_response: Any | None = None
    gdscript: str | None = None


class HasturExecutePayload(BaseModel):
    code: str
    project_path: str
    executor_id: str | None = None
    project_name: str | None = None
    type: str | None = None


class EmptyGDScriptError(ValueError):
    pass


GDSCRIPT_IDENTIFIER_REWRITES = {
    "class_name": "node_type_name",
}

GODOT_DAP_PORT = 6006


def get_hastur_settings() -> dict[str, Any]:
    settings = load_private_settings()
    return {
        "enabled": bool(settings.get("hastur_enabled", False)),
        "base_url": str(settings.get("hastur_base_url", "http://localhost:5302")).rstrip("/"),
        "auth_token": settings.get("hastur_auth_token", ""),
        "target_mode": settings.get("hastur_target_mode", "project_path"),
        "hastur_broker_host": settings.get("hastur_broker_host", "localhost"),
        "hastur_broker_tcp_port": settings.get("hastur_broker_tcp_port", 5301),
    }


def build_headers(settings: dict[str, Any]) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if settings.get("auth_token"):
        headers["Authorization"] = f"Bearer {settings['auth_token']}"
    return headers


def hastur_status() -> dict[str, Any]:
    settings = get_hastur_settings()
    if not settings["enabled"]:
        return {"available": False, "enabled": False, "message": "Hastur bridge is disabled."}
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings['base_url']}/api/health", headers=build_headers(settings))
            response.raise_for_status()
            return {"available": True, "enabled": True, "broker": response.json()}
    except httpx.HTTPError as exc:
        return {"available": False, "enabled": True, "message": f"Broker unavailable: {exc}"}


def hastur_executors() -> dict[str, Any]:
    settings = get_hastur_settings()
    if not settings["enabled"]:
        return {"available": False, "executors": [], "message": "Hastur bridge is disabled."}
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings['base_url']}/api/executors", headers=build_headers(settings))
            response.raise_for_status()
            return {"available": True, "executors": response.json()}
    except httpx.HTTPError as exc:
        return {"available": False, "executors": [], "message": f"Broker unavailable: {exc}"}


def godot_string(value: str | None) -> str:
    return json.dumps(value or "")


def godot_value(value: str | int | float | bool | None) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return godot_string("" if value is None else str(value))


def normalize_gdscript_code(code: str) -> str:
    text = _strip_code_fence(code).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not text.strip():
        raise EmptyGDScriptError("GDScript snippet is empty.")

    normalized_lines = []
    for line in text.split("\n"):
        if not line.strip():
            normalized_lines.append("")
            continue
        match = re.match(r"^[\t ]+", line)
        if not match:
            normalized_lines.append(_rewrite_unsafe_identifiers(line.rstrip()))
            continue
        leading = match.group(0)
        columns = 0
        for char in leading:
            columns += 4 if char == "\t" else 1
        tabs = max(1, (columns + 3) // 4)
        normalized_lines.append(("\t" * tabs) + _rewrite_unsafe_identifiers(line[len(leading) :].rstrip()))
    return "\n".join(normalized_lines).strip("\n")


def _strip_code_fence(code: str) -> str:
    text = code.strip()
    fenced = re.fullmatch(r"```(?:gdscript|gd|gds|text)?\s*\n?(.*?)\n?```", text, re.DOTALL | re.IGNORECASE)
    return fenced.group(1) if fenced else text


def _rewrite_unsafe_identifiers(line: str) -> str:
    result = line
    for original, replacement in GDSCRIPT_IDENTIFIER_REWRITES.items():
        result = re.sub(rf"\b{re.escape(original)}\b", replacement, result)
    return result


def _broker_failure_message(broker_response: Any) -> str | None:
    data = _execution_payload(broker_response)
    if not isinstance(data, dict):
        return None
    if data.get("success") is False:
        return str(data.get("message") or data.get("error") or "Hastur broker reported failure.")
    if data.get("compile_success") is False:
        detail = data.get("compile_error") or data.get("error") or "Unknown compile error."
        return f"Hastur compile failed: {detail}"
    if data.get("run_success") is False:
        detail = data.get("run_error") or data.get("error") or "Unknown runtime error."
        return f"Hastur run failed: {detail}"
    return None


def _hastur_project_path(project_dir) -> str:
    return project_dir.resolve().as_posix()


def _ensure_project_hastur_settings(project_dir, settings: dict[str, Any]) -> None:
    project_file = project_dir / "project.godot"
    if not project_file.exists():
        return
    host = str(settings.get("hastur_broker_host") or "localhost")
    try:
        port = int(settings.get("hastur_broker_tcp_port") or 5301)
    except (TypeError, ValueError):
        port = 5301
    original = project_file.read_text(encoding="utf-8", errors="replace")
    desired_lines = [f'broker_host="{host}"', f"broker_port={port}"]
    lines = original.splitlines()
    output: list[str] = []
    found = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip() != "[hastur_operation]":
            output.append(line)
            index += 1
            continue
        found = True
        output.append(line)
        index += 1
        section_lines = []
        while index < len(lines) and not (lines[index].strip().startswith("[") and lines[index].strip().endswith("]")):
            stripped = lines[index].strip()
            if not (stripped.startswith("broker_host=") or stripped.startswith("broker_port=")):
                section_lines.append(lines[index])
            index += 1
        output.extend(desired_lines)
        output.extend(section_lines)

    updated = "\n".join(output).rstrip() + "\n"
    if not found:
        block = "\n[hastur_operation]\n" + "\n".join(desired_lines) + "\n"
        marker = "\n[editor_plugins]"
        if marker in original:
            updated = original.replace(marker, block + marker, 1)
        else:
            updated = original.rstrip() + "\n" + block
    if updated != original:
        project_file.write_text(updated, encoding="utf-8")


def _response_payload(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def _normalize_executor_path(value: str) -> str:
    return re.sub(r"/+", "/", value.replace("\\", "/")).rstrip("/").lower()


def _executor_list(payload: Any) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload, dict) else payload
    if isinstance(data, dict):
        data = data.get("executors") or data.get("data") or []
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def _resolve_executor_id(
    client: httpx.Client,
    settings: dict[str, Any],
    project_dir,
    executor_type: str | None,
) -> str:
    if not hasattr(client, "get"):
        return ""
    try:
        response = client.get(f"{settings['base_url']}/api/executors", headers=build_headers(settings))
        response.raise_for_status()
    except Exception:
        return ""
    target_path = _normalize_executor_path(_hastur_project_path(project_dir))
    target_name = project_dir.name.lower()
    for executor in _executor_list(_response_payload(response)):
        if executor_type and str(executor.get("type") or "") != executor_type:
            continue
        executor_path = _normalize_executor_path(str(executor.get("project_path") or ""))
        executor_name = str(executor.get("project_name") or "").lower()
        if executor_path and (executor_path == target_path or executor_path.endswith(f"/{target_name}")):
            return str(executor.get("id") or "")
        if executor_name == target_name:
            return str(executor.get("id") or "")
    return ""


def _broker_http_error_message(response: httpx.Response, broker_response: Any, project_dir, executor_type: str | None) -> str:
    status_code = getattr(response, "status_code", 0)
    reason = getattr(response, "reason_phrase", "") or "HTTP error"
    error = ""
    hint = ""
    if isinstance(broker_response, dict):
        error = str(broker_response.get("error") or broker_response.get("message") or "")
        hint = str(broker_response.get("hint") or "")
    else:
        error = str(broker_response or "")
    if status_code == 404 and "No connected Hastur Executor" in error:
        target = f" for executor type '{executor_type}'" if executor_type else ""
        return (
            f"No connected Hastur executor matched this project{target}. "
            f"Open the selected Godot project with the Hastur plugin enabled, then check the Management view executor list. "
            f"Expected project path: {_hastur_project_path(project_dir)}. "
            f"Hastur uses TCP localhost:5301; Godot DAP localhost:{GODOT_DAP_PORT} is a different debug port."
        )
    detail = error or reason
    if hint:
        detail = f"{detail} {hint}"
    return f"Hastur execute failed ({status_code} {reason}): {detail}".strip()


def _execution_payload(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    if "compile_success" in value or "run_success" in value:
        return value
    data = value.get("data")
    if isinstance(data, dict):
        return _execution_payload(data)
    return value


def build_gdscript(operation: GodotOperation) -> str:
    if operation.operation == "create_scene":
        return "\n".join(
            [
                "var root := Node2D.new()",
                f"root.name = {godot_string(operation.node_name or 'GeneratedScene')}",
                "var packed := PackedScene.new()",
                "packed.pack(root)",
                f"ResourceSaver.save(packed, {godot_string(operation.target_scene)})",
            ]
        )
    if operation.operation == "open_scene":
        return f"EditorInterface.open_scene_from_path({godot_string(operation.target_scene)})"
    if operation.operation == "create_node":
        return "\n".join(
            [
                "var root := EditorInterface.get_edited_scene_root()",
                "if root == null:",
                '    push_error("No edited scene root is open.")',
                "else:",
                f"    var parent := root if {godot_string(operation.parent_path)} == \".\" else root.get_node_or_null({godot_string(operation.parent_path)})",
                "    if parent == null:",
                f"        push_error(\"Parent node not found: \" + {godot_string(operation.parent_path)})",
                "    else:",
                f"        var node := ClassDB.instantiate({godot_string(operation.node_type)})",
                "        if node == null:",
                f"            push_error(\"Unsupported node type: \" + {godot_string(operation.node_type)})",
                "        else:",
                f"            node.name = {godot_string(operation.node_name)}",
                "            parent.add_child(node)",
                "            node.owner = root",
                "            EditorInterface.mark_scene_as_unsaved()",
            ]
        )
    if operation.operation == "set_property":
        return "\n".join(
            [
                "var root := EditorInterface.get_edited_scene_root()",
                f"var node := root.get_node_or_null({godot_string(operation.node_path)}) if root != null else null",
                "if node == null:",
                f"    push_error(\"Node not found: \" + {godot_string(operation.node_path)})",
                "else:",
                f"    node.set({godot_string(operation.property_name)}, {godot_value(operation.property_value)})",
                "    EditorInterface.mark_scene_as_unsaved()",
            ]
        )
    if operation.operation == "attach_script":
        return "\n".join(
            [
                "var root := EditorInterface.get_edited_scene_root()",
                f"var node := root.get_node_or_null({godot_string(operation.node_path)}) if root != null else null",
                f"var script := load({godot_string(operation.script_path)})",
                "if node == null or script == null:",
                '    push_error("Node or script could not be loaded.")',
                "else:",
                "    node.set_script(script)",
                "    EditorInterface.mark_scene_as_unsaved()",
            ]
        )
    if operation.operation == "save_scene":
        return "EditorInterface.save_scene()"
    if operation.operation == "import_asset_reference":
        return "\n".join(
            [
                "# Asset reference recorded by AI Game Development Agent.",
                f"print({godot_string('Import asset reference: ' + (operation.asset_path or ''))})",
            ]
        )
    raise ValueError(f"Unsupported operation: {operation.operation}")


def apply_hastur_operation(project_slug: str, operation: GodotOperation, executor_id: str | None = None) -> HasturExecuteResult:
    project_dir = get_project_dir(project_slug)
    settings = get_hastur_settings()
    if not settings["enabled"]:
        return HasturExecuteResult(success=False, message="Hastur bridge is disabled.")

    gdscript = normalize_gdscript_code(build_gdscript(operation))
    _ensure_project_hastur_settings(project_dir, settings)
    payload = HasturExecutePayload(code=gdscript, project_path=_hastur_project_path(project_dir), executor_id=executor_id)
    try:
        with httpx.Client(timeout=15.0) as client:
            if not payload.executor_id:
                payload.executor_id = _resolve_executor_id(client, settings, project_dir, None) or None
            response = client.post(
                f"{settings['base_url']}/api/execute",
                headers=build_headers(settings),
                json=payload.model_dump(exclude_none=True),
            )
            if getattr(response, "status_code", 200) >= 400:
                broker_response = _response_payload(response)
                return HasturExecuteResult(
                    success=False,
                    message=_broker_http_error_message(response, broker_response, project_dir, None),
                    broker_response=broker_response,
                    gdscript=gdscript,
                )
            response.raise_for_status()
            broker_response = _response_payload(response)
            failure = _broker_failure_message(broker_response)
            return HasturExecuteResult(
                success=failure is None,
                message=failure or "Hastur operation executed.",
                broker_response=broker_response,
                gdscript=gdscript,
            )
    except httpx.HTTPError as exc:
        return HasturExecuteResult(success=False, message=f"Hastur execute failed: {exc}", gdscript=gdscript)


def apply_hastur_code(
    project_slug: str,
    code: str,
    executor_id: str | None = None,
    executor_type: str | None = None,
) -> HasturExecuteResult:
    project_dir = get_project_dir(project_slug)
    settings = get_hastur_settings()
    if not settings["enabled"]:
        return HasturExecuteResult(success=False, message="Hastur bridge is disabled.")
    try:
        gdscript = normalize_gdscript_code(code)
    except EmptyGDScriptError as exc:
        return HasturExecuteResult(success=False, message=str(exc), gdscript=code)
    _ensure_project_hastur_settings(project_dir, settings)
    payload = HasturExecutePayload(
        code=gdscript,
        project_path=_hastur_project_path(project_dir),
        executor_id=executor_id,
        type=executor_type,
    )
    try:
        with httpx.Client(timeout=30.0) as client:
            if not payload.executor_id:
                payload.executor_id = _resolve_executor_id(client, settings, project_dir, executor_type) or None
            response = client.post(
                f"{settings['base_url']}/api/execute",
                headers=build_headers(settings),
                json=payload.model_dump(exclude_none=True),
            )
            if getattr(response, "status_code", 200) >= 400:
                broker_response = _response_payload(response)
                return HasturExecuteResult(
                    success=False,
                    message=_broker_http_error_message(response, broker_response, project_dir, executor_type),
                    broker_response=broker_response,
                    gdscript=gdscript,
                )
            response.raise_for_status()
            broker_response = _response_payload(response)
            failure = _broker_failure_message(broker_response)
            return HasturExecuteResult(
                success=failure is None,
                message=failure or "Hastur skill code executed.",
                broker_response=broker_response,
                gdscript=gdscript,
            )
    except httpx.HTTPError as exc:
        return HasturExecuteResult(success=False, message=f"Hastur execute failed: {exc}", gdscript=gdscript)
