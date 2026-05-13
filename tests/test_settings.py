from app.services import settings_service


def test_hastur_settings_are_public_without_token(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_service, "SETTINGS_FILE", settings_file)

    public = settings_service.update_settings(
        {
            "hastur_enabled": True,
            "hastur_base_url": "http://localhost:5302",
            "hastur_auth_token": "secret",
            "image_provider": "openai",
        }
    )

    assert public["hastur_enabled"] is True
    assert public["has_hastur_auth_token"] is True
    assert "hastur_auth_token" not in public
    assert public["image_provider"] == "openai"


def test_defaults_use_current_provider_models(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_service, "SETTINGS_FILE", settings_file)

    public = settings_service.load_private_settings()

    assert public["llm_provider"] == "openai"
    assert public["llm_model"] == "gpt-5.5"
    assert public["openai_image_model"] == "gpt-image-1.5"


def test_legacy_image_model_is_migrated(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_service, "SETTINGS_FILE", settings_file)
    settings_service.save_private_settings({"image_provider": "openai", "openai_image_model": "gpt-image-2"})

    private = settings_service.load_private_settings()
    public = settings_service.get_public_settings()

    assert private["openai_image_model"] == "gpt-image-1.5"
    assert public["openai_image_model"] == "gpt-image-1.5"
    assert "mock" not in public["llm_defaults"]
    assert "mock" not in public["image_defaults"]


def test_public_settings_hide_legacy_placeholder_provider(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_service, "SETTINGS_FILE", settings_file)
    legacy = "mo" + "ck"
    settings_service.save_private_settings({"llm_provider": legacy, "image_provider": legacy})

    public = settings_service.get_public_settings()

    assert public["llm_provider"] == "openai"
    assert public["image_provider"] == "openai"
    assert legacy not in public["supported_llm_providers"]
    assert legacy not in public["supported_image_providers"]


def test_hastur_ports_do_not_migrate_to_godot_adapter_ports(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_service, "SETTINGS_FILE", settings_file)
    settings_service.save_private_settings(
        {
            "hastur_broker_http_port": 6005,
            "hastur_broker_tcp_port": 6006,
            "hastur_base_url": "http://localhost:6006",
        }
    )

    public = settings_service.get_public_settings()

    assert public["hastur_broker_http_port"] == 5302
    assert public["hastur_broker_tcp_port"] == 5301
    assert public["hastur_base_url"] == "http://localhost:5302"
