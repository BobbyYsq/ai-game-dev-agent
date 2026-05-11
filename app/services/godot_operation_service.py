from __future__ import annotations

from typing import Any

from app.agent.godot_operation_planner import GodotOperationPlan, build_operation_planner_prompt, parse_operation_plan
from app.models.llm_provider import get_llm_provider
from app.services.asset_service import get_project_dir
from app.services.hastur_service import GodotOperation, apply_hastur_operation


def _read_project_text(project_slug: str, relative_path: str) -> str:
    path = get_project_dir(project_slug) / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def plan_godot_operations(project_slug: str, instruction: str, executors: Any | None = None) -> GodotOperationPlan:
    project_dir = get_project_dir(project_slug)
    gdd = _read_project_text(project_slug, "docs/GDD.md")
    feature_tasks = _read_project_text(project_slug, "docs/FEATURE_TASKS.md")
    prompt = build_operation_planner_prompt(project_dir.name, gdd, feature_tasks)
    prompt += f"""

User instruction:
{instruction}

Connected executors:
{executors or "unknown"}

Return only the JSON operation plan. Do not include prose.
"""
    raw = get_llm_provider().generate_text(
        prompt,
        system_prompt="You produce safe, minimal Godot editor operation JSON for a validated execution pipeline.",
    )
    return parse_operation_plan(raw)


def execute_godot_operation_plan(
    project_slug: str,
    operations: list[GodotOperation],
    executor_id: str | None = None,
) -> dict[str, Any]:
    results = []
    for operation in operations:
        result = apply_hastur_operation(project_slug, operation, executor_id)
        results.append(result.model_dump())
        if not result.success:
            break
    return {"success": all(item.get("success") for item in results), "results": results}
