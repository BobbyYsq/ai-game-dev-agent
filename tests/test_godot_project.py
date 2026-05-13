from types import SimpleNamespace

from app.services import godot_project_service, project_service


def test_create_godot_project_installs_and_enables_hastur(tmp_path, monkeypatch):
    root = tmp_path / "generated"
    monkeypatch.setattr(godot_project_service, "GENERATED_PROJECTS_DIR", root)

    result = godot_project_service.create_godot_project(
        project_name="Shadow Garden",
        game_type="2D top-down action",
        project_template="2d",
        broker_host="localhost",
        broker_port=5301,
        enable_git=False,
    )

    project = root / "shadow-garden"
    project_godot = (project / "project.godot").read_text(encoding="utf-8")
    assert result.success is True
    assert (project / "addons/hasturoperationgd/plugin.cfg").exists()
    assert (project / "scenes/Main.tscn").exists()
    assert 'enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")' in project_godot
    assert 'broker_host="localhost"' in project_godot
    assert "broker_port=5301" in project_godot
    assert "[input]" not in project_godot
    assert (project / "THIRD_PARTY_NOTICES.md").exists()
    assert (project / "licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md").exists()
    assert (project / ".gitignore").exists()
    assert (project / ".gitattributes").exists()
    assert (project / "docs/GODOT_PROJECT.md").exists()


def test_create_godot_project_initializes_git_by_default(tmp_path, monkeypatch):
    root = tmp_path / "generated"
    calls = []
    monkeypatch.setattr(godot_project_service, "GENERATED_PROJECTS_DIR", root)
    monkeypatch.setattr(godot_project_service, "init_repo", lambda path: calls.append(("init", path.name)))
    monkeypatch.setattr(godot_project_service, "commit_all", lambda path, message: calls.append(("commit", message)))

    godot_project_service.create_godot_project(
        project_name="Git Garden",
        game_type="2D top-down action",
        project_template="2d",
        broker_host="localhost",
        broker_port=5301,
    )

    assert calls == [("init", "git-garden"), ("commit", "Initial Godot project")]


def test_create_godot_project_handles_existing_clean_project(tmp_path, monkeypatch):
    root = tmp_path / "generated"
    monkeypatch.setattr(godot_project_service, "GENERATED_PROJECTS_DIR", root)
    monkeypatch.setattr(godot_project_service, "init_repo", lambda path: None)
    monkeypatch.setattr(
        godot_project_service,
        "commit_all",
        lambda path, message: {"success": True, "committed": False, "message": "No local changes to commit."},
    )

    result = godot_project_service.create_godot_project(
        project_name="Git Garden",
        game_type="2D top-down action",
        project_template="2d",
        broker_host="localhost",
        broker_port=5301,
    )

    assert result.success is True
    assert result.git["committed"] is False
    assert "no new changes" in result.message.lower()


def test_legacy_project_creation_writes_godot_project_notes(tmp_path, monkeypatch):
    root = tmp_path / "generated"
    monkeypatch.setattr(project_service, "GENERATED_PROJECTS_DIR", root)
    monkeypatch.setattr(project_service, "load_private_settings", lambda: {"hastur_broker_host": "localhost", "hastur_broker_tcp_port": 5301})
    monkeypatch.setattr(project_service, "get_llm_provider", lambda: object())
    monkeypatch.setattr(project_service, "generate_review_report", lambda *_args, **_kwargs: "Review")

    request = SimpleNamespace(
        project_name="Legacy Garden",
        game_idea="A tiny garden prototype",
        game_type="2D top-down action",
        project_template="2d",
        engine="Godot 4",
        prototype_scope="one room",
        generate_docs=False,
        generate_godot_skeleton=True,
        enable_git=False,
    )

    result = project_service.create_ai_game_project(request)
    project = root / "legacy-garden"

    assert result.success is True
    assert (project / "docs/GODOT_PROJECT.md").exists()
    assert "docs/GODOT_PROJECT.md" in result.generated_files
