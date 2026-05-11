from __future__ import annotations

import json
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


def get_hastur_settings() -> dict[str, Any]:
    settings = load_private_settings()
    return {
        "enabled": bool(settings.get("hastur_enabled", False)),
        "base_url": str(settings.get("hastur_base_url", "http://localhost:5302")).rstrip("/"),
        "auth_token": settings.get("hastur_auth_token", ""),
        "target_mode": settings.get("hastur_target_mode", "project_path"),
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

    gdscript = build_gdscript(operation)
    payload = HasturExecutePayload(code=gdscript, project_path=str(project_dir), executor_id=executor_id)
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                f"{settings['base_url']}/api/execute",
                headers=build_headers(settings),
                json=payload.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            try:
                broker_response = response.json()
            except ValueError:
                broker_response = response.text
            return HasturExecuteResult(
                success=True,
                message="Hastur operation executed.",
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
    payload = HasturExecutePayload(
        code=code,
        project_path=str(project_dir),
        executor_id=executor_id,
        type=executor_type,
    )
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{settings['base_url']}/api/execute",
                headers=build_headers(settings),
                json=payload.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            try:
                broker_response = response.json()
            except ValueError:
                broker_response = response.text
            return HasturExecuteResult(
                success=True,
                message="Hastur skill code executed.",
                broker_response=broker_response,
                gdscript=code,
            )
    except httpx.HTTPError as exc:
        return HasturExecuteResult(success=False, message=f"Hastur execute failed: {exc}", gdscript=code)
