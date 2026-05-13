from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Any

from app.services.broker_service import broker_logs, broker_status, start_broker, stop_broker
from app.services.hastur_chat_service import chat_with_hastur_skill
from app.services.hastur_task_service import create_task, resume_task, stream_task_events
from app.services.hastur_service import GodotOperation, apply_hastur_operation, hastur_executors, hastur_status
from app.services.hastur_skill_service import list_hastur_skills
from app.services.godot_operation_service import execute_godot_operation_plan, plan_godot_operations

router = APIRouter()


class ApplyOperationRequest(BaseModel):
    operation: GodotOperation
    executor_id: str | None = None


class PlanOperationRequest(BaseModel):
    instruction: str
    executor_id: str | None = None
    executors: Any | None = None


class ExecutePlanRequest(BaseModel):
    operations: list[GodotOperation]
    executor_id: str | None = None


class BrokerStartRequest(BaseModel):
    host: str | None = None
    http_port: int | None = None
    tcp_port: int | None = None


class UploadedImage(BaseModel):
    filename: str
    media_type: str
    data: str


class HasturChatRequest(BaseModel):
    instruction: str
    skill_name: str = "godot-remote-executor"
    execute: bool = True
    confirmed: bool = False
    images: list[UploadedImage] = []
    attachments: list[UploadedImage] = []


class HasturTaskRequest(BaseModel):
    instruction: str
    skill_name: str | None = None
    confirmed: bool = False
    attachments: list[UploadedImage] = []


class HasturTaskResumeRequest(BaseModel):
    answer: str = ""
    confirmed: bool = False
    choice_id: str = ""
    revision_request: str = ""


@router.get("/api/hastur/broker/status")
def get_broker_status():
    return broker_status()


@router.post("/api/hastur/broker/start")
def start_hastur_broker(payload: BrokerStartRequest):
    try:
        return start_broker(payload.host, payload.http_port, payload.tcp_port)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/api/hastur/broker/stop")
def stop_hastur_broker():
    return stop_broker()


@router.get("/api/hastur/broker/logs")
def get_broker_logs():
    return broker_logs()


@router.get("/api/hastur/status")
def get_hastur_status():
    return hastur_status()


@router.get("/api/hastur/executors")
def get_hastur_executors():
    return hastur_executors()


@router.get("/api/hastur/skills")
def get_hastur_skills():
    return {"skills": [skill.__dict__ for skill in list_hastur_skills()]}


@router.post("/api/projects/{project_slug}/hastur/chat")
def chat_with_hastur(project_slug: str, payload: HasturChatRequest):
    if not payload.instruction.strip():
        raise HTTPException(status_code=422, detail="instruction is required")
    try:
        return chat_with_hastur_skill(
            project_slug=project_slug,
            instruction=payload.instruction.strip(),
            skill_name=payload.skill_name,
            images=[image.model_dump() for image in payload.images],
            attachments=[attachment.model_dump() for attachment in payload.attachments],
            execute=payload.execute,
            confirmed=payload.confirmed,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Hastur chat failed: {exc}") from exc


@router.post("/api/projects/{project_slug}/hastur/tasks")
def create_hastur_task(project_slug: str, payload: HasturTaskRequest):
    if not payload.instruction.strip():
        raise HTTPException(status_code=422, detail="instruction is required")
    try:
        return create_task(
            project_slug=project_slug,
            instruction=payload.instruction.strip(),
            skill_name=payload.skill_name,
            attachments=[attachment.model_dump() for attachment in payload.attachments],
            confirmed=payload.confirmed,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/projects/{project_slug}/hastur/tasks/{task_id}/events")
def stream_hastur_task(project_slug: str, task_id: str):
    try:
        return StreamingResponse(stream_task_events(task_id), media_type="text/event-stream")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/hastur/tasks/{task_id}/resume")
def resume_hastur_task(project_slug: str, task_id: str, payload: HasturTaskResumeRequest):
    try:
        return resume_task(task_id, payload.answer, payload.confirmed, payload.choice_id, payload.revision_request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/projects/{project_slug}/visual-checkpoints/{filename}")
def get_visual_checkpoint(project_slug: str, filename: str):
    if "/" in filename or "\\" in filename or filename.startswith("."):
        raise HTTPException(status_code=400, detail="invalid checkpoint filename")
    try:
        from app.services.asset_service import get_project_dir

        path = get_project_dir(project_slug) / "assets" / "generated" / "visual_checkpoints" / filename
        if not path.exists():
            raise FileNotFoundError(f"Visual checkpoint not found: {filename}")
        return FileResponse(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/hastur/apply-operation")
def apply_operation(project_slug: str, payload: ApplyOperationRequest):
    try:
        return apply_hastur_operation(project_slug, payload.operation, payload.executor_id).model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/hastur/execute")
def execute_structured_operation(project_slug: str, payload: ApplyOperationRequest):
    try:
        return apply_hastur_operation(project_slug, payload.operation, payload.executor_id).model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/hastur/plan")
def plan_operations(project_slug: str, payload: PlanOperationRequest):
    if not payload.instruction.strip():
        raise HTTPException(status_code=422, detail="instruction is required")
    try:
        plan = plan_godot_operations(project_slug, payload.instruction.strip(), payload.executors)
        return {"success": True, "plan": plan.model_dump()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/hastur/execute-plan")
def execute_plan(project_slug: str, payload: ExecutePlanRequest):
    try:
        return execute_godot_operation_plan(project_slug, payload.operations, payload.executor_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/projects/{project_slug}/hastur/plan-and-execute")
def plan_and_execute(project_slug: str, payload: PlanOperationRequest):
    if not payload.instruction.strip():
        raise HTTPException(status_code=422, detail="instruction is required")
    try:
        plan = plan_godot_operations(project_slug, payload.instruction.strip(), payload.executors)
        execution = execute_godot_operation_plan(project_slug, plan.operations, payload.executor_id)
        return {"success": execution["success"], "plan": plan.model_dump(), "execution": execution}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
