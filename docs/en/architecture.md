# Architecture

The v0.2.1 app is a local-first FastAPI application with a lightweight HTML/CSS/JavaScript dashboard.

## Flow

```text
User dashboard
  -> FastAPI routes
  -> settings/project services
  -> LLM provider and local generators
  -> workspace/generated_godot_projects/<slug>
```

## Backend

- `app/main.py` creates the FastAPI app, mounts static files, and renders the dashboard.
- `app/api/routes_settings.py` exposes settings and LLM connection testing.
- `app/api/routes_projects.py` exposes project create/list/detail APIs.
- `app/services/settings_service.py` reads and writes local private settings.
- `app/services/project_service.py` coordinates document generation, Godot generation, review output, and optional Git commit.

## Agent Layer

The agent modules are intentionally simple in v0.2.1. They wrap prompts for GDD, technical design, feature tasks, asset list, and review report. The provider can be `mock` for offline testing or `openai` for real text generation.

## Godot Generator

`app/tools/godot_project_tools.py` dispatches to template modules under `app/tools/godot_templates/`. The 2D and 3D templates write Godot scene text files, scripts, project settings, asset directories, and generated-asset cache folders.

## Workspace

- `workspace/config/settings.json` stores private settings and API keys.
- `workspace/generated_godot_projects/` stores generated Godot projects.
- `workspace/cache/` is reserved for future shared cache data.
- `runtime/` stores portable Micromamba and the local Python environment.
