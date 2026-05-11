from app.services import godot_project_service


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
    assert 'enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")' in project_godot
    assert 'broker_host="localhost"' in project_godot
    assert "broker_port=5301" in project_godot
    assert (project / "THIRD_PARTY_NOTICES.md").exists()
    assert (project / "licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md").exists()


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
