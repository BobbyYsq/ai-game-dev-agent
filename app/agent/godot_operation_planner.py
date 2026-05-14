from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.services.hastur_service import GodotOperation


class GodotOperationPlan(BaseModel):
    operations: list[GodotOperation] = Field(default_factory=list)


def parse_operation_plan(raw_json: str | dict[str, Any]) -> GodotOperationPlan:
    if isinstance(raw_json, str):
        text = raw_json.strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1)
        elif not text.startswith("{"):
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                text = text[start : end + 1]
        data = json.loads(text)
    else:
        data = raw_json
    try:
        return GodotOperationPlan.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid Godot operation plan: {exc}") from exc


def build_operation_planner_prompt(project_name: str, gdd: str, feature_tasks: str = "") -> str:
    return f"""
You are planning safe Godot editor operations for the AI Game Development Agent.
Return only JSON in this shape:
{{"operations": [{{"operation": "open_scene", "target_scene": "res://scenes/Main.tscn"}}]}}

Allowed operation values:
- create_scene
- open_scene
- create_node
- set_property
- attach_script
- save_scene
- import_asset_reference

Project: {project_name}

GDD:
{gdd}

Feature tasks:
{feature_tasks}
""".strip()

