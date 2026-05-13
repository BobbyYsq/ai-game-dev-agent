import base64
import io
import zipfile

import pytest

from app.services import hastur_skill_service


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def test_skill_registry_lists_scopes_and_frontmatter(tmp_path, monkeypatch):
    vendored = tmp_path / "vendored"
    global_root = tmp_path / "global"
    project = tmp_path / "generated" / "shadow-garden"
    for root, name in [(vendored, "core-skill"), (global_root, "global-skill"), (project / ".claude" / "skills", "project-skill")]:
        skill_dir = root / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            f"name: {name}\n"
            "description: Short description.\n"
            "when_to_use: Use when relevant.\n"
            "argument-hint: ISSUE\n"
            "arguments: [issue]\n"
            "disable-model-invocation: true\n"
            "user-invocable: false\n"
            "allowed-tools: Read Grep\n"
            "model: sonnet\n"
            "effort: low\n"
            "paths: [references/example.md]\n"
            "---\n\nBody",
            encoding="utf-8",
        )

    monkeypatch.setattr("app.services.asset_service.GENERATED_PROJECTS_DIR", tmp_path / "generated")
    monkeypatch.setattr(hastur_skill_service, "HASTUR_SKILLS_DIR", vendored)
    monkeypatch.setattr(hastur_skill_service, "USER_SKILLS_DIR", global_root)

    skills = hastur_skill_service.list_hastur_skills("shadow-garden")
    scopes = {(skill.name, skill.scope, skill.readonly) for skill in skills}

    assert ("core-skill", "vendored", True) in scopes
    assert ("global-skill", "global", False) in scopes
    assert ("project-skill", "project", False) in scopes
    project_skill = next(skill for skill in skills if skill.name == "project-skill")
    assert project_skill.when_to_use == "Use when relevant."
    assert project_skill.argument_hint == "ISSUE"
    assert project_skill.arguments == ["issue"]
    assert project_skill.disable_model_invocation is True
    assert project_skill.user_invocable is False
    assert project_skill.allowed_tools == ["Read", "Grep"]
    assert project_skill.paths == ["references/example.md"]


def test_upload_global_skill_from_markdown_and_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(hastur_skill_service, "USER_SKILLS_DIR", tmp_path / "global")

    result = hastur_skill_service.upload_skill(
        "global",
        [
            {
                "filename": "SKILL.md",
                "data": _b64(b"---\nname: uploaded-skill\ndescription: Uploaded.\n---\n\nBody"),
            }
        ],
    )

    assert result["skill"]["name"] == "uploaded-skill"
    assert (tmp_path / "global" / "uploaded-skill" / "SKILL.md").exists()

    deleted = hastur_skill_service.delete_skill("global", "uploaded-skill")
    assert deleted["success"] is True
    assert not (tmp_path / "global" / "uploaded-skill").exists()


def test_upload_project_skill_from_zip_and_reject_path_traversal(tmp_path, monkeypatch):
    project_root = tmp_path / "generated"
    (project_root / "shadow-garden").mkdir(parents=True)
    monkeypatch.setattr("app.services.asset_service.GENERATED_PROJECTS_DIR", project_root)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("pack/SKILL.md", "---\nname: zipped-skill\ndescription: Zipped.\n---\n\nBody")
        archive.writestr("pack/references/note.md", "reference")

    result = hastur_skill_service.upload_skill(
        "project",
        [{"filename": "skill.zip", "data": _b64(buffer.getvalue())}],
        project_slug="shadow-garden",
    )

    skill_root = project_root / "shadow-garden" / ".claude" / "skills" / "zipped-skill"
    assert result["skill"]["scope"] == "project"
    assert (skill_root / "references" / "note.md").exists()

    with pytest.raises(ValueError):
        hastur_skill_service.upload_skill(
            "project",
            [{"filename": "../SKILL.md", "data": _b64(b"bad")}],
            project_slug="shadow-garden",
        )


def test_vendored_skill_cannot_be_deleted(tmp_path, monkeypatch):
    vendored = tmp_path / "vendored" / "core-skill"
    vendored.mkdir(parents=True)
    (vendored / "SKILL.md").write_text("---\nname: core-skill\ndescription: Core.\n---\n\nBody", encoding="utf-8")
    monkeypatch.setattr(hastur_skill_service, "HASTUR_SKILLS_DIR", tmp_path / "vendored")

    with pytest.raises(ValueError):
        hastur_skill_service.delete_skill("vendored", "core-skill")
