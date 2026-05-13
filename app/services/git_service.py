from pathlib import Path
from datetime import datetime
import os
import subprocess
from typing import Any

DEFAULT_GIT_USER_NAME = os.environ.get("AI_GAME_DEV_AGENT_GIT_NAME", "AI Game Development Agent")
DEFAULT_GIT_USER_EMAIL = os.environ.get("AI_GAME_DEV_AGENT_GIT_EMAIL", "agent@localhost")
DEFAULT_BRANCH = "main"
GODOT_GITIGNORE_ENTRIES = [
    ".godot/",
    "*.translation",
]
GODOT_GITATTRIBUTES_ENTRIES = [
    "* text=auto eol=lf",
]


class GitCommandError(RuntimeError):
    def __init__(self, command: list[str], stderr: str = "", stdout: str = ""):
        message = stderr.strip() or stdout.strip() or f"Git command failed: {' '.join(command)}"
        super().__init__(message)
        self.command = command
        self.stderr = stderr
        self.stdout = stdout


def _run_git_raw(project_dir: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git", "-c", f"safe.directory={project_dir.resolve().as_posix()}", *args]
    completed = subprocess.run(
        command,
        cwd=project_dir,
        check=False,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        raise GitCommandError(command, completed.stderr, completed.stdout)
    return completed


def init_repo(project_dir: Path) -> None:
    if (project_dir / ".git").exists():
        _ensure_identity(project_dir)
        _ensure_main_branch(project_dir)
        ensure_godot_vcs_metadata(project_dir)
        return
    ensure_godot_vcs_metadata(project_dir)
    _run_git_raw(project_dir, ["init", "-b", DEFAULT_BRANCH])
    _ensure_identity(project_dir)
    _untrack_ignored_godot_files(project_dir)


def commit_all(project_dir: Path, message: str) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        init_repo(project_dir)
    _ensure_repository_ready(project_dir)
    _ensure_identity(project_dir)
    _run_git_raw(project_dir, ["add", "."])
    pending = _run_git_raw(project_dir, ["status", "--porcelain"]).stdout.strip()
    if not pending:
        return {"success": True, "committed": False, "message": "No local changes to commit."}
    commit_result = _run_git_raw(project_dir, ["commit", "-m", message])
    return {
        "success": True,
        "committed": True,
        "message": commit_result.stdout.strip() or "Committed local changes.",
    }


def is_git_repo(project_dir: Path) -> bool:
    return (project_dir / ".git").exists()


def run_git(project_dir: Path, args: list[str]) -> str:
    completed = _run_git_raw(project_dir, args)
    return completed.stdout.strip()


def friendly_git_error(error: Exception | str) -> str:
    if isinstance(error, GitCommandError):
        return _friendly_git_error(error.stderr or error.stdout or str(error))
    return _friendly_git_error(str(error))


def status(project_dir: Path) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {
            "is_repo": False,
            "short": "",
            "branch": "",
            "default_branch": DEFAULT_BRANCH,
            "branches": [],
            "dirty": False,
            "files": [],
            "dirty_count": 0,
            "can_save": False,
            "can_merge_to_main": False,
            "can_delete_current": False,
        }
    _ensure_repository_ready(project_dir)
    short = _run_git_raw(project_dir, ["status", "--porcelain=v1", "-uall"]).stdout.rstrip()
    branch = _current_branch(project_dir)
    files = _parse_status_files(short)
    branch_list = branches(project_dir)["branches"]
    dirty = bool(short)
    return {
        "is_repo": True,
        "short": short,
        "branch": branch,
        "default_branch": DEFAULT_BRANCH,
        "branches": branch_list,
        "dirty": dirty,
        "dirty_count": len(files),
        "files": files,
        "can_save": dirty,
        "can_merge_to_main": branch != DEFAULT_BRANCH and not dirty and _has_commits(project_dir),
        "can_delete_current": False,
    }


def changes(project_dir: Path) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "status": status(project_dir), "files": [], "log": {"is_repo": False, "commits": []}}
    _ensure_repository_ready(project_dir)
    short = _run_git_raw(project_dir, ["status", "--porcelain=v1", "-uall"]).stdout.rstrip()
    files = [_change_entry(line) for line in short.splitlines() if line]
    return {
        "success": True,
        "is_repo": True,
        "status": status(project_dir),
        "files": files,
        "log": log(project_dir, limit=8),
    }


def diff_summary(project_dir: Path, path: str | None = None) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "stat": "", "diff": ""}
    _ensure_repository_ready(project_dir)
    args = ["diff", "--stat"]
    diff_args = ["diff", "--"]
    if path:
        safe_paths = _validate_paths(project_dir, [path])
        args.extend(["--", *safe_paths])
        diff_args.extend(safe_paths)
    else:
        diff_args.append(".")
    stat = run_git(project_dir, args)
    diff = run_git(project_dir, diff_args)
    cached_stat = run_git(project_dir, ["diff", "--cached", "--stat", "--", *(safe_paths if path else ["."])])
    cached_diff = run_git(project_dir, ["diff", "--cached", "--", *(safe_paths if path else ["."])])
    return {
        "is_repo": True,
        "stat": stat,
        "diff": diff[:12000],
        "cached_stat": cached_stat,
        "cached_diff": cached_diff[:12000],
    }


def review(project_dir: Path) -> dict[str, Any]:
    current_status = status(project_dir)
    current_diff = diff_summary(project_dir)
    return {
        "success": True,
        "status": current_status,
        "diff": current_diff,
        "changes": changes(project_dir),
        "log": log(project_dir, limit=5),
    }


def log(project_dir: Path, limit: int = 12) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "commits": []}
    _ensure_repository_ready(project_dir)
    output = _run_git_raw(
        project_dir,
        ["log", f"--max-count={limit}", "--pretty=format:%H%x1f%h%x1f%an%x1f%ad%x1f%s", "--date=short"],
        check=False,
    ).stdout.strip()
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


def commit(project_dir: Path, message: str, paths: list[str] | None = None) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        init_repo(project_dir)
    _ensure_repository_ready(project_dir)
    safe_paths = _validate_paths(project_dir, paths or [])
    _ensure_identity(project_dir)
    if safe_paths:
        _run_git_raw(project_dir, ["add", "--", *safe_paths])
    else:
        _run_git_raw(project_dir, ["add", "."])
    staged = _run_git_raw(project_dir, ["diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        return {"success": False, "message": "No staged changes to commit.", "status": status(project_dir), "log": log(project_dir)}
    commit_result = _run_git_raw(project_dir, ["commit", "-m", message])
    return {
        "success": True,
        "message": commit_result.stdout.strip() or "Committed local changes.",
        "status": status(project_dir),
        "changes": changes(project_dir),
        "log": log(project_dir),
    }


def branches(project_dir: Path) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "branches": [], "current": "", "default_branch": DEFAULT_BRANCH}
    _ensure_repository_ready(project_dir)
    output = _run_git_raw(
        project_dir,
        ["branch", "--format=%(refname:short)\t%(HEAD)\t%(objectname:short)\t%(subject)"],
        check=False,
    ).stdout.strip()
    current = _current_branch(project_dir)
    items = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) != 4:
            continue
        name, head, short_hash, subject = parts
        items.append(
            {
                "name": name,
                "current": head == "*" or name == current,
                "default": name == DEFAULT_BRANCH,
                "short_hash": short_hash,
                "subject": subject,
                "can_delete": name not in {current, DEFAULT_BRANCH},
            }
        )
    return {"is_repo": True, "branches": items, "current": current, "default_branch": DEFAULT_BRANCH}


def create_branch(project_dir: Path, name: str, checkout: bool = True) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        init_repo(project_dir)
    _ensure_repository_ready(project_dir)
    branch_name = _validate_branch_name(project_dir, name)
    existing = {branch["name"] for branch in branches(project_dir)["branches"]}
    if branch_name in existing:
        return {"success": False, "message": f"Branch already exists: {branch_name}", "status": status(project_dir)}
    args = ["checkout", "-b", branch_name] if checkout else ["branch", branch_name]
    result = _run_git_raw(project_dir, args, check=False)
    if result.returncode != 0:
        return {
            "success": False,
            "message": _friendly_git_error(result.stderr or result.stdout),
            "status": status(project_dir),
            "graph": graph(project_dir),
        }
    return {
        "success": True,
        "message": result.stdout.strip() or f"Created branch {branch_name}.",
        "status": status(project_dir),
        "graph": graph(project_dir),
    }


def switch_branch(project_dir: Path, name: str) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    branch_name = _validate_branch_name(project_dir, name)
    existing = {branch["name"] for branch in branches(project_dir)["branches"]}
    if branch_name not in existing:
        return {"success": False, "message": f"Branch not found: {branch_name}", "status": status(project_dir)}
    result = _run_git_raw(project_dir, ["checkout", branch_name], check=False)
    if result.returncode != 0:
        return {
            "success": False,
            "message": _friendly_git_error(result.stderr or result.stdout),
            "status": status(project_dir),
            "graph": graph(project_dir),
        }
    return {
        "success": True,
        "message": result.stdout.strip() or f"Switched to {branch_name}.",
        "status": status(project_dir),
        "graph": graph(project_dir),
    }


def delete_branch(project_dir: Path, name: str) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    branch_name = _validate_branch_name(project_dir, name)
    current = _current_branch(project_dir)
    if branch_name == DEFAULT_BRANCH:
        return {"success": False, "message": f"Cannot delete the {DEFAULT_BRANCH} branch.", "status": status(project_dir)}
    if branch_name == current:
        return {"success": False, "message": "Switch to another branch before deleting this branch.", "status": status(project_dir)}
    result = _run_git_raw(project_dir, ["branch", "-d", branch_name], check=False)
    if result.returncode != 0:
        return {
            "success": False,
            "message": _friendly_git_error(result.stderr or result.stdout),
            "status": status(project_dir),
            "graph": graph(project_dir),
        }
    return {
        "success": True,
        "message": result.stdout.strip() or f"Deleted branch {branch_name}.",
        "status": status(project_dir),
        "graph": graph(project_dir),
    }


def save(project_dir: Path, message: str | None = None) -> dict[str, Any]:
    default_message = f"Save {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    result = commit(project_dir, (message or "").strip() or default_message)
    result["graph"] = graph(project_dir)
    return result


def merge_to_main(project_dir: Path) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    source = _current_branch(project_dir)
    if source == DEFAULT_BRANCH:
        return {"success": False, "message": f"You are already on {DEFAULT_BRANCH}.", "status": status(project_dir)}
    if _is_dirty(project_dir):
        return {"success": False, "message": "Save or discard local changes before merging.", "status": status(project_dir)}
    if not _has_commits(project_dir):
        return {"success": False, "message": "There are no commits to merge yet.", "status": status(project_dir)}

    _run_git_raw(project_dir, ["checkout", DEFAULT_BRANCH])
    result = _run_git_raw(project_dir, ["merge", "--no-ff", source, "-m", f"Merge {source} into {DEFAULT_BRANCH}"], check=False)
    if result.returncode != 0:
        _run_git_raw(project_dir, ["merge", "--abort"], check=False)
        _run_git_raw(project_dir, ["checkout", source], check=False)
        return {
            "success": False,
            "message": _friendly_git_error(result.stderr or result.stdout),
            "status": status(project_dir),
            "graph": graph(project_dir),
        }
    return {
        "success": True,
        "message": result.stdout.strip() or f"Merged {source} into {DEFAULT_BRANCH}.",
        "merged_branch": source,
        "status": status(project_dir),
        "graph": graph(project_dir),
    }


def graph(project_dir: Path, limit: int = 80) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"is_repo": False, "commits": [], "ascii": "", "branches": []}
    _ensure_repository_ready(project_dir)
    if not _has_commits(project_dir):
        return {"is_repo": True, "commits": [], "ascii": "", "branches": branches(project_dir)["branches"]}
    output = _run_git_raw(
        project_dir,
        [
            "log",
            "--all",
            "--date-order",
            f"--max-count={limit}",
            "--pretty=format:%H%x1f%h%x1f%P%x1f%D%x1f%an%x1f%ad%x1f%s",
            "--date=short",
        ],
        check=False,
    ).stdout.strip()
    commits = []
    for line in output.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 7:
            refs = _parse_refs(parts[3])
            commits.append(
                {
                    "hash": parts[0],
                    "short_hash": parts[1],
                    "parents": [parent for parent in parts[2].split() if parent],
                    "refs": refs,
                    "author": parts[4],
                    "date": parts[5],
                    "subject": parts[6],
                    "current": "HEAD" in refs,
                    "main": DEFAULT_BRANCH in refs,
                }
            )
    ascii_graph = _run_git_raw(
        project_dir,
        ["log", "--graph", "--decorate", "--all", "--date-order", f"--max-count={limit}", "--oneline"],
        check=False,
    ).stdout.strip()
    return {"is_repo": True, "commits": commits, "ascii": ascii_graph, "branches": branches(project_dir)["branches"]}


def discard(project_dir: Path, paths: list[str]) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    safe_paths = _validate_paths(project_dir, paths)
    if not safe_paths:
        return {"success": False, "message": "Select at least one file to discard."}
    current = {file["path"]: file for file in changes(project_dir).get("files", [])}
    tracked_paths = [path for path in safe_paths if not current.get(path, {}).get("untracked")]
    untracked_paths = [path for path in safe_paths if current.get(path, {}).get("untracked")]
    if tracked_paths:
        _run_git_raw(project_dir, ["restore", "--staged", "--worktree", "--", *tracked_paths], check=False)
    if untracked_paths:
        _run_git_raw(project_dir, ["clean", "-f", "-d", "--", *untracked_paths], check=False)
    return {"success": True, "message": "Selected changes were discarded.", "changes": changes(project_dir)}


def revert_commit(project_dir: Path, commit_hash: str) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    target = run_git(project_dir, ["rev-parse", "--verify", commit_hash])
    result = _run_git_raw(project_dir, ["revert", "--no-edit", target], check=False)
    if result.returncode != 0:
        raise GitCommandError(["git", "revert", "--no-edit", target], result.stderr, result.stdout)
    return {"success": True, "message": result.stdout.strip() or "Commit reverted.", "target": target, "changes": changes(project_dir)}


def restore_file(project_dir: Path, commit_hash: str, paths: list[str]) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    safe_paths = _validate_paths(project_dir, paths)
    if not safe_paths:
        return {"success": False, "message": "Select at least one file to restore."}
    target = run_git(project_dir, ["rev-parse", "--verify", commit_hash])
    _run_git_raw(project_dir, ["restore", f"--source={target}", "--worktree", "--", *safe_paths])
    return {"success": True, "message": "Selected files were restored from the chosen commit.", "target": target, "changes": changes(project_dir)}


def rollback(project_dir: Path, commit_hash: str, confirm: bool = False) -> dict[str, Any]:
    if not is_git_repo(project_dir):
        return {"success": False, "message": "Project is not a Git repository."}
    _ensure_repository_ready(project_dir)
    if _is_dirty(project_dir):
        return {"success": False, "message": "Save or discard local changes before restoring to a previous save point.", "status": status(project_dir)}
    target = run_git(project_dir, ["rev-parse", "--verify", commit_hash])
    short = run_git(project_dir, ["rev-parse", "--short", target])
    _ensure_identity(project_dir)
    _run_git_raw(project_dir, ["restore", f"--source={target}", "--staged", "--worktree", "--", "."])
    _run_git_raw(project_dir, ["add", "-A"])
    staged = _run_git_raw(project_dir, ["diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        return {
            "success": True,
            "committed": False,
            "message": f"Project already matches save point {short}.",
            "target": target,
            "status": status(project_dir),
            "graph": graph(project_dir),
        }
    commit_result = _run_git_raw(project_dir, ["commit", "-m", f"Restore to {short}"])
    return {
        "success": True,
        "committed": True,
        "message": commit_result.stdout.strip() or f"Restored project to {short}.",
        "target": target,
        "status": status(project_dir),
        "graph": graph(project_dir),
    }


def _parse_status_files(short_status: str) -> list[dict[str, str]]:
    return [_change_entry(line) for line in short_status.splitlines() if line]


def _change_entry(line: str) -> dict[str, str]:
    xy = line[:2]
    raw_path = line[3:] if len(line) > 3 else line[2:].strip()
    if " -> " in raw_path:
        raw_path = raw_path.split(" -> ", 1)[1]
    status_code = xy.strip() or xy
    staged = xy[0] not in {" ", "?"}
    unstaged = xy[1] not in {" "}
    untracked = xy == "??"
    path = raw_path.strip('"')
    status_kind = _status_kind(xy)
    directory = str(Path(path).parent).replace("\\", "/")
    if directory == ".":
        directory = ""
    return {
        "status": status_code,
        "index_status": xy[0],
        "worktree_status": xy[1],
        "path": path,
        "directory": directory,
        "filename": Path(path).name,
        "status_kind": status_kind,
        "display_status": _display_status(status_kind),
        "staged": staged and not untracked,
        "unstaged": unstaged and not untracked,
        "untracked": untracked,
    }


def _status_kind(xy: str) -> str:
    if xy == "??":
        return "added"
    if "U" in xy or xy in {"AA", "DD"}:
        return "conflict"
    if "R" in xy:
        return "renamed"
    if "C" in xy:
        return "copied"
    if "D" in xy:
        return "deleted"
    if "T" in xy:
        return "type_changed"
    if "A" in xy:
        return "added"
    if "M" in xy:
        return "modified"
    return "changed"


def _display_status(status_kind: str) -> str:
    return {
        "added": "Added",
        "modified": "Modified",
        "deleted": "Deleted",
        "renamed": "Renamed",
        "copied": "Copied",
        "type_changed": "Type changed",
        "conflict": "Conflict",
        "changed": "Changed",
    }.get(status_kind, "Changed")


def _current_branch(project_dir: Path) -> str:
    branch = _run_git_raw(project_dir, ["branch", "--show-current"], check=False).stdout.strip()
    if branch:
        return branch
    return _run_git_raw(project_dir, ["rev-parse", "--short", "HEAD"], check=False).stdout.strip()


def ensure_godot_vcs_metadata(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    _ensure_lines(project_dir / ".gitignore", GODOT_GITIGNORE_ENTRIES)
    _ensure_lines(project_dir / ".gitattributes", GODOT_GITATTRIBUTES_ENTRIES)


def _ensure_repository_ready(project_dir: Path) -> None:
    _ensure_main_branch(project_dir)
    ensure_godot_vcs_metadata(project_dir)
    _untrack_ignored_godot_files(project_dir)


def _ensure_lines(path: Path, required_lines: list[str]) -> None:
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    normalized = {line.strip() for line in existing}
    additions = [line for line in required_lines if line not in normalized]
    if not additions:
        return
    content = "\n".join(existing + additions).strip() + "\n"
    path.write_text(content, encoding="utf-8", newline="\n")


def _untrack_ignored_godot_files(project_dir: Path) -> None:
    if not is_git_repo(project_dir):
        return
    _run_git_raw(project_dir, ["rm", "-r", "--cached", "--ignore-unmatch", "--", ".godot", "*.translation"], check=False)


def _ensure_main_branch(project_dir: Path) -> None:
    if not is_git_repo(project_dir):
        return
    has_main = _ref_exists(project_dir, f"refs/heads/{DEFAULT_BRANCH}")
    has_master = _ref_exists(project_dir, "refs/heads/master")
    if has_main:
        return
    if has_master:
        _run_git_raw(project_dir, ["branch", "-m", "master", DEFAULT_BRANCH])
        return
    if not _has_commits(project_dir):
        _run_git_raw(project_dir, ["symbolic-ref", "HEAD", f"refs/heads/{DEFAULT_BRANCH}"], check=False)


def _ref_exists(project_dir: Path, ref: str) -> bool:
    return _run_git_raw(project_dir, ["show-ref", "--verify", "--quiet", ref], check=False).returncode == 0


def _has_commits(project_dir: Path) -> bool:
    return _run_git_raw(project_dir, ["rev-parse", "--verify", "HEAD"], check=False).returncode == 0


def _is_dirty(project_dir: Path) -> bool:
    return bool(_run_git_raw(project_dir, ["status", "--porcelain=v1", "-uall"], check=False).stdout.strip())


def _validate_branch_name(project_dir: Path, name: str) -> str:
    branch_name = name.strip()
    if not branch_name:
        raise ValueError("Branch name is required.")
    result = _run_git_raw(project_dir, ["check-ref-format", "--branch", branch_name], check=False)
    if result.returncode != 0 or branch_name.upper() == "HEAD":
        raise ValueError(f"Invalid branch name: {name}")
    return branch_name


def _parse_refs(decorations: str) -> list[str]:
    if not decorations:
        return []
    refs = []
    for item in decorations.split(", "):
        item = item.strip()
        if item.startswith("HEAD -> "):
            refs.extend(["HEAD", item.replace("HEAD -> ", "", 1)])
        elif item.startswith("tag: "):
            refs.append(item.replace("tag: ", "", 1))
        else:
            refs.append(item.replace("origin/", "", 1))
    return refs


def _friendly_git_error(text: str) -> str:
    cleaned = (text or "").strip()
    lowered = cleaned.lower()
    if "not fully merged" in cleaned:
        return "This branch has not been merged yet. Merge it to main before deleting it."
    if "CONFLICT" in cleaned or "Automatic merge failed" in cleaned:
        return "Merge conflict. Resolve or discard conflicting changes manually, then try again."
    if "would be overwritten by checkout" in lowered or "would be overwritten by merge" in lowered or "please commit your changes" in lowered:
        return "This branch operation would overwrite local changes. Save or discard the affected files, then try again."
    if "untracked working tree files would be overwritten" in lowered:
        return "This branch operation would overwrite new local files. Save or discard the affected files, then try again."
    if "Filename too long" in cleaned or "unable to index file" in cleaned:
        return "Git could not index a generated Godot cache file. The project Git ignore metadata has been refreshed; try saving again."
    if "LF will be replaced by CRLF" in cleaned:
        return "Git reported line-ending warnings. The project Git attributes have been refreshed to keep text files consistent."
    return cleaned or "Git operation failed."


def _validate_paths(project_dir: Path, paths: list[str]) -> list[str]:
    safe = []
    for path in paths:
        normalized = str(path).replace("\\", "/").strip()
        if not normalized or normalized.startswith("/") or re_contains_parent(normalized):
            raise ValueError(f"Unsafe Git path: {path}")
        resolved = (project_dir / normalized).resolve()
        root = project_dir.resolve()
        if resolved != root and root not in resolved.parents:
            raise ValueError(f"Git path escapes project: {path}")
        safe.append(normalized)
    return safe


def re_contains_parent(path: str) -> bool:
    return any(part == ".." for part in Path(path).parts)


def _ensure_identity(project_dir: Path) -> None:
    if not _read_git_config(project_dir, "user.name"):
        _run_git_raw(project_dir, ["config", "user.name", DEFAULT_GIT_USER_NAME])
    if not _read_git_config(project_dir, "user.email"):
        _run_git_raw(project_dir, ["config", "user.email", DEFAULT_GIT_USER_EMAIL])


def _read_git_config(project_dir: Path, key: str) -> str:
    completed = _run_git_raw(project_dir, ["config", "--get", key], check=False)
    return completed.stdout.strip()
