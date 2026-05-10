from pathlib import Path

APP_VERSION = "0.2.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
SETTINGS_DIR = WORKSPACE_DIR / "config"
GENERATED_PROJECTS_DIR = WORKSPACE_DIR / "generated_godot_projects"
CACHE_DIR = WORKSPACE_DIR / "cache"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


def ensure_workspace_dirs() -> None:
    for p in [WORKSPACE_DIR, SETTINGS_DIR, GENERATED_PROJECTS_DIR, CACHE_DIR]:
        p.mkdir(parents=True, exist_ok=True)
