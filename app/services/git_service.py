from pathlib import Path
import subprocess


def init_repo(project_dir: Path) -> None:
    if (project_dir / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=project_dir, check=True)


def commit_all(project_dir: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=project_dir, check=True)
