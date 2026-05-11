from pathlib import Path

from app.services import hastur_chat_service, hastur_skill_service


def test_lists_vendored_hastur_skills(tmp_path, monkeypatch):
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "godot-remote-executor"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: godot-remote-executor
description: Execute Godot remotely.
---

# Godot Remote Executor
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(hastur_skill_service, "HASTUR_SKILLS_DIR", skills_dir)

    skills = hastur_skill_service.list_hastur_skills()

    assert skills[0].name == "godot-remote-executor"
    assert "Execute Godot" in skills[0].description


def test_hastur_chat_loads_skill_and_keeps_token_hidden(tmp_path, monkeypatch):
    project_root = tmp_path / "generated"
    project = project_root / "shadow-garden"
    project.mkdir(parents=True)
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "godot-remote-executor"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Godot Remote Executor", encoding="utf-8")

    class FakeLLM:
        supports_images = True

        def generate_text(self, prompt, system_prompt=None):
            assert "secret-token" not in prompt
            assert "Auth token is available to the app: True" in prompt
            return '{"message": "ready", "requires_confirmation": false, "code": ""}'

    monkeypatch.setattr("app.services.asset_service.GENERATED_PROJECTS_DIR", project_root)
    monkeypatch.setattr(hastur_chat_service, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(hastur_chat_service, "hastur_executors", lambda: {"available": True, "executors": []})
    monkeypatch.setattr(hastur_chat_service, "load_private_settings", lambda: {"hastur_auth_token": "secret-token", "hastur_base_url": "http://localhost:5302"})
    monkeypatch.setattr(hastur_skill_service, "HASTUR_SKILLS_DIR", skills_dir)

    result = hastur_chat_service.chat_with_hastur_skill("shadow-garden", "inspect", "godot-remote-executor")

    assert result["success"] is True
    assert result["message"] == "ready"
