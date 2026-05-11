from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import git_service
from app.services.asset_service import get_project_dir

router = APIRouter()


class CommitRequest(BaseModel):
    message: str


class RollbackRequest(BaseModel):
    commit_hash: str
    confirm: bool = False


def _project_dir(project_slug: str):
    try:
        return get_project_dir(project_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _raise_bad_request(exc: Exception) -> None:
    if isinstance(exc, HTTPException):
        raise exc
    raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/projects/{project_slug}/git/status")
def get_git_status(project_slug: str):
    try:
        return git_service.status(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/review")
def review_git_changes(project_slug: str):
    try:
        return git_service.review(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/diff")
def get_git_diff(project_slug: str):
    try:
        return git_service.diff_summary(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/log")
def get_git_log(project_slug: str):
    try:
        return git_service.log(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/commit")
def commit_project(project_slug: str, payload: CommitRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="commit message is required")
    try:
        return git_service.commit(_project_dir(project_slug), payload.message.strip())
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/rollback")
def rollback_project(project_slug: str, payload: RollbackRequest):
    if not payload.commit_hash.strip():
        raise HTTPException(status_code=422, detail="commit_hash is required")
    try:
        return git_service.rollback(_project_dir(project_slug), payload.commit_hash.strip(), payload.confirm)
    except Exception as exc:
        _raise_bad_request(exc)
