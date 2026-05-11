from pathlib import Path

APP_VERSION = "0.3.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
SETTINGS_DIR = WORKSPACE_DIR / "config"
GENERATED_PROJECTS_DIR = WORKSPACE_DIR / "generated_godot_projects"
CACHE_DIR = WORKSPACE_DIR / "cache"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"
HASTUR_PROJECT_DIR = PROJECT_ROOT / "hastur-operation-plugin-main"
HASTUR_ADDON_DIR = HASTUR_PROJECT_DIR / "addons" / "hasturoperationgd"
HASTUR_BROKER_DIR = HASTUR_PROJECT_DIR / "broker-server"
HASTUR_LICENSE_FILE = HASTUR_PROJECT_DIR / "LICENSE"


def ensure_workspace_dirs() -> None:
    for p in [WORKSPACE_DIR, SETTINGS_DIR, GENERATED_PROJECTS_DIR, CACHE_DIR]:
        p.mkdir(parents=True, exist_ok=True)
