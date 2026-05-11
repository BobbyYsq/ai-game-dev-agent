from app.services import broker_service


class FakeProcess:
    pid = 4242
    stdout = []

    def __init__(self):
        self.returncode = None

    def poll(self):
        return self.returncode

    def terminate(self):
        self.returncode = 0

    def wait(self, timeout=None):
        self.returncode = 0

    def kill(self):
        self.returncode = -9


class FakeCompleted:
    returncode = 0
    stdout = "installed"
    stderr = ""


def test_broker_start_and_stop_with_fake_process(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(broker_service, "_process", None)
    monkeypatch.setattr(broker_service, "_command", lambda name: name)
    monkeypatch.setattr(broker_service, "HASTUR_BROKER_DIR", tmp_path)
    monkeypatch.setattr("app.services.settings_service.SETTINGS_FILE", settings_file)
    monkeypatch.setattr("app.services.broker_service.subprocess.run", lambda *args, **kwargs: FakeCompleted())
    monkeypatch.setattr("app.services.broker_service.subprocess.Popen", lambda *args, **kwargs: FakeProcess())
    (tmp_path / "src").mkdir()

    started = broker_service.start_broker("localhost", 5302, 5301)

    assert started["success"] is True
    assert started["status"]["running"] is True
    assert started["status"]["has_auth_token"] is True

    stopped = broker_service.stop_broker()

    assert stopped["success"] is True
    assert stopped["status"]["running"] is False


def test_broker_captures_printed_auth_token(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("app.services.settings_service.SETTINGS_FILE", settings_file)
    monkeypatch.setattr("app.services.broker_service.SETTINGS_FILE", settings_file, raising=False)

    broker_service._append_log("Auto-generated auth token: abcdef1234567890abcdef1234567890")

    status = broker_service.broker_status()
    assert status["has_auth_token"] is True
