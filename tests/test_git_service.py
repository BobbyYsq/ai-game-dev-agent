from pathlib import Path
import subprocess

from app.services import git_service


def test_git_status_for_non_repo(tmp_path: Path):
    result = git_service.status(tmp_path)

    assert result["is_repo"] is False
    assert result["dirty"] is False


def test_git_rollback_creates_safe_restore_commit(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("one", encoding="utf-8")
    git_service.commit_all(tmp_path, "one")
    first = git_service.run_git(tmp_path, ["rev-parse", "HEAD"])
    (tmp_path / "file.txt").write_text("two", encoding="utf-8")
    git_service.commit_all(tmp_path, "two")

    result = git_service.rollback(tmp_path, first, confirm=True)

    assert result["success"] is True
    assert result["committed"] is True
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one"
    assert git_service.run_git(tmp_path, ["log", "-1", "--pretty=%s"]).startswith("Restore to")


def test_git_rollback_without_confirmation_returns_preview(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("one", encoding="utf-8")
    git_service.commit_all(tmp_path, "one")
    first = git_service.run_git(tmp_path, ["rev-parse", "HEAD"])
    (tmp_path / "file.txt").write_text("two", encoding="utf-8")
    git_service.commit_all(tmp_path, "two")

    result = git_service.rollback(tmp_path, first, confirm=False)

    assert result["success"] is True
    assert result["preview"] is True
    assert result["committed"] is False
    assert result["short_hash"] == first[:7]
    assert result["subject"] == "one"
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "two"
    assert git_service.run_git(tmp_path, ["log", "-1", "--pretty=%s"]) == "two"


def test_init_repo_uses_main_branch(tmp_path: Path):
    git_service.init_repo(tmp_path)

    assert git_service.status(tmp_path)["branch"] == "main"
    assert (tmp_path / ".gitignore").exists()
    assert (tmp_path / ".gitattributes").exists()


def test_godot_generated_cache_is_ignored_on_save(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "project.godot").write_text("config_version=5\n", encoding="utf-8")
    (tmp_path / ".godot/shader_cache/deep").mkdir(parents=True)
    (tmp_path / ".godot/shader_cache/deep/cache.bin").write_text("cache", encoding="utf-8")
    (tmp_path / "strings.translation").write_text("generated", encoding="utf-8")

    result = git_service.save(tmp_path, "initial")
    tracked = set(git_service.run_git(tmp_path, ["ls-files"]).splitlines())

    assert result["success"] is True
    assert ".gitignore" in tracked
    assert ".gitattributes" in tracked
    assert not any(path.startswith(".godot/") for path in tracked)
    assert "strings.translation" not in tracked


def test_existing_tracked_godot_cache_is_untracked_without_deleting_file(tmp_path: Path):
    git_service.init_repo(tmp_path)
    cache_file = tmp_path / ".godot/cache.txt"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text("cache", encoding="utf-8")
    git_service.run_git(tmp_path, ["add", "-f", ".godot/cache.txt"])
    git_service.run_git(tmp_path, ["commit", "-m", "old cache"])

    result = git_service.status(tmp_path)
    tracked_cache = git_service.run_git(tmp_path, ["ls-files", ".godot/cache.txt"])

    assert result["is_repo"] is True
    assert tracked_cache == ""
    assert cache_file.exists()


def test_commit_selected_paths_only(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")

    result = git_service.commit(tmp_path, "commit one", ["one.txt"])

    assert result["success"] is True
    assert git_service.run_git(tmp_path, ["log", "-1", "--pretty=%s"]) == "commit one"
    status = git_service.status(tmp_path)
    assert any(file["path"] == "two.txt" for file in status["files"])


def test_discard_selected_changes(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("one", encoding="utf-8")
    git_service.commit_all(tmp_path, "one")
    (tmp_path / "file.txt").write_text("two", encoding="utf-8")
    (tmp_path / "scratch.txt").write_text("scratch", encoding="utf-8")

    result = git_service.discard(tmp_path, ["file.txt", "scratch.txt"])

    assert result["success"] is True
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one"
    assert not (tmp_path / "scratch.txt").exists()


def test_revert_commit_and_restore_file(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("one", encoding="utf-8")
    git_service.commit_all(tmp_path, "one")
    (tmp_path / "file.txt").write_text("two", encoding="utf-8")
    git_service.commit_all(tmp_path, "two")
    second = git_service.run_git(tmp_path, ["rev-parse", "HEAD"])

    revert = git_service.revert_commit(tmp_path, second)

    assert revert["success"] is True
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one"

    restore = git_service.restore_file(tmp_path, second, ["file.txt"])

    assert restore["success"] is True
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "two"


def test_branch_save_merge_delete_and_graph(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("main", encoding="utf-8")
    git_service.save(tmp_path, "initial")

    created = git_service.create_branch(tmp_path, "feature")
    assert created["success"] is True
    assert git_service.status(tmp_path)["branch"] == "feature"

    (tmp_path / "feature.txt").write_text("feature", encoding="utf-8")
    saved = git_service.save(tmp_path, "feature save")
    assert saved["success"] is True

    merged = git_service.merge_to_main(tmp_path)
    assert merged["success"] is True
    assert git_service.status(tmp_path)["branch"] == "main"
    assert (tmp_path / "feature.txt").exists()

    graph = git_service.graph(tmp_path)
    subjects = [commit["subject"] for commit in graph["commits"]]
    assert any("feature save" in subject for subject in subjects)
    assert graph["ascii"]

    deleted = git_service.delete_branch(tmp_path, "feature")
    assert deleted["success"] is True
    assert "feature" not in {branch["name"] for branch in git_service.branches(tmp_path)["branches"]}


def test_create_branch_allows_dirty_worktree(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("main", encoding="utf-8")
    git_service.save(tmp_path, "initial")
    (tmp_path / "dirty.txt").write_text("dirty", encoding="utf-8")

    created = git_service.create_branch(tmp_path, "feature")

    assert created["success"] is True
    assert git_service.status(tmp_path)["branch"] == "feature"
    assert (tmp_path / "dirty.txt").exists()


def test_switch_allows_non_conflicting_dirty_worktree_and_merge_rejects_dirty(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("main", encoding="utf-8")
    git_service.save(tmp_path, "initial")
    git_service.create_branch(tmp_path, "feature")
    git_service.switch_branch(tmp_path, "main")
    (tmp_path / "dirty.txt").write_text("dirty", encoding="utf-8")

    switch = git_service.switch_branch(tmp_path, "feature")
    merge = git_service.merge_to_main(tmp_path)

    assert switch["success"] is True
    assert merge["success"] is False


def test_git_status_has_friendly_change_fields(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "project.godot").write_text("main", encoding="utf-8")
    git_service.save(tmp_path, "initial")
    (tmp_path / "project.godot").write_text("changed", encoding="utf-8")
    (tmp_path / "materials/town").mkdir(parents=True)
    (tmp_path / "materials/town/roof.tres").write_text("roof", encoding="utf-8")

    files = {item["path"]: item for item in git_service.status(tmp_path)["files"]}

    assert files["project.godot"]["status_kind"] == "modified"
    assert files["project.godot"]["display_status"] == "Modified"
    assert files["materials/town/roof.tres"]["status_kind"] == "added"
    assert files["materials/town/roof.tres"]["directory"] == "materials/town"


def test_delete_current_or_main_branch_is_rejected(tmp_path: Path):
    git_service.init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("main", encoding="utf-8")
    git_service.save(tmp_path, "initial")
    git_service.create_branch(tmp_path, "feature")

    current = git_service.delete_branch(tmp_path, "feature")
    main = git_service.delete_branch(tmp_path, "main")

    assert current["success"] is False
    assert main["success"] is False


def test_commit_all_no_changes_is_success(tmp_path: Path):
    git_service.init_repo(tmp_path)
    git_service.commit_all(tmp_path, "metadata")

    result = git_service.commit_all(tmp_path, "empty")

    assert result["success"] is True
    assert result["committed"] is False


def test_init_repo_sets_local_identity(tmp_path: Path, monkeypatch):
    calls = []

    def fake_run(cmd, cwd=None, check=None, text=None, capture_output=None):
        calls.append(cmd)
        if cmd[-3:-1] == ["config", "--get"]:
            return subprocess.CompletedProcess(cmd, 1, "", "")
        return subprocess.CompletedProcess(cmd, 0, "ok", "")

    monkeypatch.setattr(git_service.subprocess, "run", fake_run)

    git_service.init_repo(tmp_path)

    assert any(cmd[-2:] == ["-b", git_service.DEFAULT_BRANCH] for cmd in calls)
    assert any(cmd[-3:] == ["config", "user.name", git_service.DEFAULT_GIT_USER_NAME] for cmd in calls)
    assert any(cmd[-3:] == ["config", "user.email", git_service.DEFAULT_GIT_USER_EMAIL] for cmd in calls)
