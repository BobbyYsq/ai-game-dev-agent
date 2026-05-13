from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import git_service
from app.services.git_service import GitCommandError
from app.services.asset_service import get_project_dir

router = APIRouter()


class CommitRequest(BaseModel):
    message: str
    paths: list[str] = []


class SaveRequest(BaseModel):
    message: str = ""


class RollbackRequest(BaseModel):
    commit_hash: str
    confirm: bool = False


class BranchRequest(BaseModel):
    name: str


class PathsRequest(BaseModel):
    paths: list[str] = []


class RevertRequest(BaseModel):
    commit_hash: str


class RestoreFileRequest(BaseModel):
    commit_hash: str
    paths: list[str] = []


def _project_dir(project_slug: str):
    try:
        return get_project_dir(project_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _raise_bad_request(exc: Exception) -> None:
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, GitCommandError):
        raise HTTPException(status_code=400, detail=git_service.friendly_git_error(exc)) from exc
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
def get_git_diff(project_slug: str, path: str | None = None):
    try:
        return git_service.diff_summary(_project_dir(project_slug), path)
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/changes")
def get_git_changes(project_slug: str):
    try:
        return git_service.changes(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/log")
def get_git_log(project_slug: str):
    try:
        return git_service.log(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/graph")
def get_git_graph(project_slug: str):
    try:
        return git_service.graph(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.get("/api/projects/{project_slug}/git/branches")
def get_git_branches(project_slug: str):
    try:
        return git_service.branches(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/commit")
def commit_project(project_slug: str, payload: CommitRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="commit message is required")
    try:
        return git_service.commit(_project_dir(project_slug), payload.message.strip(), payload.paths)
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/save")
def save_project(project_slug: str, payload: SaveRequest):
    try:
        return git_service.save(_project_dir(project_slug), payload.message.strip())
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/branches")
def create_project_branch(project_slug: str, payload: BranchRequest):
    if not payload.name.strip():
        raise HTTPException(status_code=422, detail="branch name is required")
    try:
        return git_service.create_branch(_project_dir(project_slug), payload.name.strip())
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/branches/switch")
def switch_project_branch(project_slug: str, payload: BranchRequest):
    if not payload.name.strip():
        raise HTTPException(status_code=422, detail="branch name is required")
    try:
        return git_service.switch_branch(_project_dir(project_slug), payload.name.strip())
    except Exception as exc:
        _raise_bad_request(exc)


@router.delete("/api/projects/{project_slug}/git/branches/{branch_name:path}")
def delete_project_branch(project_slug: str, branch_name: str):
    if not branch_name.strip():
        raise HTTPException(status_code=422, detail="branch name is required")
    try:
        return git_service.delete_branch(_project_dir(project_slug), branch_name.strip())
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/merge-to-main")
def merge_project_to_main(project_slug: str):
    try:
        return git_service.merge_to_main(_project_dir(project_slug))
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/discard")
def discard_project_changes(project_slug: str, payload: PathsRequest):
    try:
        return git_service.discard(_project_dir(project_slug), payload.paths)
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/revert")
def revert_project_commit(project_slug: str, payload: RevertRequest):
    if not payload.commit_hash.strip():
        raise HTTPException(status_code=422, detail="commit_hash is required")
    try:
        return git_service.revert_commit(_project_dir(project_slug), payload.commit_hash.strip())
    except Exception as exc:
        _raise_bad_request(exc)


@router.post("/api/projects/{project_slug}/git/restore-file")
def restore_project_file(project_slug: str, payload: RestoreFileRequest):
    if not payload.commit_hash.strip():
        raise HTTPException(status_code=422, detail="commit_hash is required")
    try:
        return git_service.restore_file(_project_dir(project_slug), payload.commit_hash.strip(), payload.paths)
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
