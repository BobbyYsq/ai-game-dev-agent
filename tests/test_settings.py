from app.services import settings_service


def test_hastur_settings_are_public_without_token(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_service, "SETTINGS_FILE", settings_file)

    public = settings_service.update_settings(
        {
            "hastur_enabled": True,
            "hastur_base_url": "http://localhost:5302",
            "hastur_auth_token": "secret",
            "image_provider": "mock",
        }
    )

    assert public["hastur_enabled"] is True
    assert public["has_hastur_auth_token"] is True
    assert "hastur_auth_token" not in public
    assert public["image_provider"] == "mock"
