from pathlib import Path
import subprocess
from typing import Any


def init_repo(project_dir: Path) -> None:
    if (project_dir / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=project_dir, check=True)


def commit_all(project_dir: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=project_dir, check=True)


def is_git_repo(project_dir: Path) -> bool:
    return (project_dir / ".git").exists()


def run_git(project_dir: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=project_dir,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def status(project_dir: Path) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "short": "", "branch": "", "dirty": False, "files": []}
    short = run_git(project_dir, ["status", "--short"])
    branch = run_git(project_dir, ["branch", "--show-current"])
    files = _parse_status_files(short)
    return {"is_repo": True, "short": short, "branch": branch, "dirty": bool(short), "files": files}


def diff_summary(project_dir: Path) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "stat": "", "diff": ""}
    stat = run_git(project_dir, ["diff", "--stat"])
    diff = run_git(project_dir, ["diff", "--", "."])
    return {"is_repo": True, "stat": stat, "diff": diff[:12000]}


def review(project_dir: Path) -> dict[str, Any]:
    current_status = status(project_dir)
    current_diff = diff_summary(project_dir)
    return {
        "success": True,
        "status": current_status,
        "diff": current_diff,
        "log": log(project_dir, limit=5),
    }


def log(project_dir: Path, limit: int = 12) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "commits": []}
    output = run_git(project_dir, ["log", f"--max-count={limit}", "--pretty=format:%H%x1f%h%x1f%an%x1f%ad%x1f%s", "--date=short"])
    commits = []
    for line in output.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 5:
            commits.append(
                {
                    "hash": parts[0],
                    "short_hash": parts[1],
                    "author": parts[2],
                    "date": parts[3],
                    "subject": parts[4],
                }
            )
    return {"is_repo": True, "commits": commits}


def commit(project_dir: Path, message: str) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        init_repo(project_dir)
    current_status = status(project_dir)
    if current_status["is_repo"] and not current_status["dirty"]:
        return {"success": False, "message": "No local changes to commit.", "status": current_status, "log": log(project_dir)}
    commit_all(project_dir, message)
    return {"success": True, "status": status(project_dir), "log": log(project_dir)}


def rollback(project_dir: Path, commit_hash: str, confirm: bool = False) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    target = run_git(project_dir, ["rev-parse", "--verify", commit_hash])
    preview = run_git(project_dir, ["diff", "--stat", f"HEAD..{target}"])
    if not confirm:
        return {"success": True, "requires_confirmation": True, "target": target, "preview": preview}
    run_git(project_dir, ["reset", "--hard", target])
    return {"success": True, "requires_confirmation": False, "target": target, "status": status(project_dir)}


def _parse_status_files(short_status: str) -> list[dict[str, str]]:
    files = []
    for line in short_status.splitlines():
        if not line:
            continue
        status_code = line[:2].strip() or line[:2]
        path = line[3:] if len(line) > 3 else line[2:].strip()
        files.append({"status": status_code, "path": path})
    return files
