from pathlib import Path

from app.services import asset_service
from app.models.image_provider import GeneratedImage


def make_project(tmp_path: Path, monkeypatch):
    root = tmp_path / "generated"
    project = root / "shadow-garden"
    (project / "docs").mkdir(parents=True)
    (project / "assets/generated/cache/images").mkdir(parents=True)
    (project / "docs/GDD.md").write_text("# Shadow Garden\n", encoding="utf-8")
    monkeypatch.setattr(asset_service, "GENERATED_PROJECTS_DIR", root)
    class FakeImageProvider:
        def generate_image(self, prompt: str, model: str, size: str, quality: str):
            return GeneratedImage(content=b"image-bytes", provider="fake", model=model)

    monkeypatch.setattr(asset_service, "get_image_provider", lambda: FakeImageProvider())
    monkeypatch.setattr(asset_service, "load_private_settings", lambda: {"openai_image_model": "gpt-image-1.5", "image_api_key": "sk-test", "image_provider": "openai"})
    monkeypatch.setattr("app.models.image_provider.load_private_settings", lambda: {"openai_image_model": "gpt-image-1.5", "image_api_key": "sk-test", "image_provider": "openai"})
    return project


def test_fake_image_generation_creates_manifest(tmp_path, monkeypatch):
    make_project(tmp_path, monkeypatch)

    asset = asset_service.generate_image_asset(
        project_slug="shadow-garden",
        prompt="A haunted garden concept.",
        purpose="concept_art",
        model="gpt-image-1",
    )

    project = tmp_path / "generated" / "shadow-garden"
    assert asset.id == "img_001"
    assert (project / asset.path).exists()
    manifest = asset_service.load_asset_manifest(project)
    assert manifest[0]["purpose"] == "concept_art"


def test_attach_asset_to_gdd(tmp_path, monkeypatch):
    make_project(tmp_path, monkeypatch)
    asset = asset_service.generate_image_asset(
        project_slug="shadow-garden",
        prompt="A haunted garden concept.",
        purpose="gdd_reference",
        model="gpt-image-1",
    )

    updated = asset_service.attach_asset_to_gdd("shadow-garden", asset.id)

    gdd = (tmp_path / "generated" / "shadow-garden" / "docs/GDD.md").read_text(encoding="utf-8")
    assert updated["linked_to_gdd"] is True
    assert "Generated Visual References" in gdd
    assert asset.path in gdd


def test_mark_blender_reference_writes_notes(tmp_path, monkeypatch):
    make_project(tmp_path, monkeypatch)
    asset = asset_service.generate_image_asset(
        project_slug="shadow-garden",
        prompt="A 3D reference statue.",
        purpose="concept_art",
        model="gpt-image-1",
    )

    updated = asset_service.mark_blender_reference("shadow-garden", asset.id)

    notes = tmp_path / "generated" / "shadow-garden" / "docs/BLENDER_REFERENCE_NOTES.md"
    assert updated["use_as_blender_reference"] is True
    assert notes.exists()
    assert asset.id in notes.read_text(encoding="utf-8")


def test_image_generation_preflight_rejects_invalid_quality(tmp_path, monkeypatch):
    make_project(tmp_path, monkeypatch)

    try:
        asset_service.generate_image_asset(
            project_slug="shadow-garden",
            prompt="A haunted garden concept.",
            purpose="concept_art",
            quality="ultra",
        )
    except ValueError as exc:
        assert "Unsupported image quality" in str(exc)
    else:
        raise AssertionError("expected invalid quality to fail")
