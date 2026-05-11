from pathlib import Path

from app.services import git_service


def test_git_status_for_non_repo(tmp_path: Path):
    result = git_service.status(tmp_path)

    assert result["is_repo"] is False
    assert result["dirty"] is False


def test_git_rollback_requires_confirmation(tmp_path: Path):
    git_service.init_repo(tmp_path)
    git_service.run_git(tmp_path, ["config", "user.email", "test@example.com"])
    git_service.run_git(tmp_path, ["config", "user.name", "Test User"])
    (tmp_path / "file.txt").write_text("one", encoding="utf-8")
    git_service.commit_all(tmp_path, "one")
    first = git_service.run_git(tmp_path, ["rev-parse", "HEAD"])
    (tmp_path / "file.txt").write_text("two", encoding="utf-8")
    git_service.commit_all(tmp_path, "two")

    preview = git_service.rollback(tmp_path, first, confirm=False)

    assert preview["requires_confirmation"] is True
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "two"

    done = git_service.rollback(tmp_path, first, confirm=True)

    assert done["requires_confirmation"] is False
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one"
