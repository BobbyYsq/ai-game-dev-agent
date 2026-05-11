# File and Function Reference

## Root

- `start_windows.cmd`: Windows double-click entrypoint.
- `start_macos.command`: macOS entrypoint.
- `environment.yml`: Micromamba environment definition.
- `requirements.txt`: Python package list used by the environment.

## Bootstrap

- `bootstrap/bootstrap_windows.ps1`: downloads Micromamba, creates runtime env, finds a port, starts FastAPI on Windows.
- `bootstrap/bootstrap_macos.sh`: same workflow for macOS with architecture detection.
- `bootstrap/README_BOOTSTRAP.md`: explains the local runtime layout.

## App Entry

- `app/main.py`
  - `create_app()`: creates FastAPI, mounts `/static`, registers routers, and renders `/`.
- `app/config.py`
  - `ensure_workspace_dirs()`: creates workspace directories.

## API Routes

- `app/api/routes_settings.py`
  - `get_settings()`: returns public settings.
  - `save_settings()`: saves provider/model/key values.
  - `test_llm_connection()`: calls the active provider.
- `app/api/routes_projects.py`
  - `create_project()`: validates template and creates a project.
  - `list_projects()`: lists recent generated project folders.
  - `get_project()`: returns files for one generated project.

## Services

- `app/services/settings_service.py`
  - `load_private_settings()`: reads local settings.
  - `save_private_settings()`: writes local settings.
  - `get_public_settings()`: hides API key value.
  - `update_settings()`: merges UI updates.
- `app/services/project_service.py`
  - `slugify()`: converts names to folder-safe slugs.
  - `create_ai_game_project()`: orchestrates docs, Godot files, review, and Git.
- `app/services/git_service.py`
  - `init_repo()`: runs `git init`.
  - `commit_all()`: stages and commits generated files.

## Generators

- `app/tools/godot_project_tools.py`
  - `generate_godot_template_project()`: dispatches `2d` or `3d` generation.
- `app/tools/godot_templates/base.py`: shared folder, project file, and script helpers.
- `app/tools/godot_templates/template_2d.py`: writes the playable 2D template.
- `app/tools/godot_templates/template_3d.py`: writes the playable 3D template.
## v0.3 Added Files

- `app/models/image_provider.py`: `MockImageProvider`, `OpenAIImageProvider`, and `get_image_provider()` for image generation.
- `app/services/asset_service.py`: creates image assets, writes `asset_manifest.json`, appends images to `GDD.md`, and writes Blender reference notes.
- `app/api/routes_assets.py`: exposes image generation, asset listing, asset file serving, GDD attachment, and Blender reference endpoints.
- `app/services/hastur_service.py`: defines `GodotOperation`, validates required fields, builds safe GDScript snippets, checks Hastur status, lists executors, and applies operations.
- `app/services/broker_service.py`: manages the local Hastur broker process and captures logs.
- `app/services/godot_project_service.py`: creates standalone Godot projects with automatic Hastur addon integration.
- `app/services/godot_operation_service.py`: asks the configured LLM for operation plans, validates them, and executes validated plans.
- `app/api/routes_hastur.py`: exposes Hastur status, executor, and structured operation endpoints.
- `app/api/routes_godot_projects.py`: exposes standalone Godot project creation.
- `app/agent/godot_operation_planner.py`: validates future LLM-produced Godot operation plans.
- `AGENTS.md`: AI-facing project context and required workflow rules.
- `THIRD_PARTY_NOTICES.md`: root third-party license notice for the vendored Hastur Operation Plugin.
- `tests/test_assets.py`, `tests/test_hastur.py`, `tests/test_settings.py`: smoke coverage for v0.3 services.
