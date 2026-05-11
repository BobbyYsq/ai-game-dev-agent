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
## v0.3 Pipeline

The app is organized as a local FastAPI control plane:

- `app/api/` exposes settings, project, asset, and Hastur routes.
- `app/services/asset_service.py` owns image asset generation, cache writes, manifest updates, GDD attachment, and Blender reference notes.
- `app/models/image_provider.py` abstracts `mock` and OpenAI image generation. The OpenAI path defaults to `gpt-image-2`.
- `app/services/hastur_service.py` validates structured Godot operations and converts them into controlled GDScript snippets before calling a local Hastur broker.
- `app/services/broker_service.py` starts, stops, checks, and captures logs from the vendored Hastur broker-server.
- `app/services/godot_project_service.py` creates standalone Godot projects with the Hastur addon copied into `addons/hasturoperationgd/`.
- `app/services/godot_operation_service.py` uses the configured LLM provider to plan Godot operations, then validates them before execution.
- `app/agent/godot_operation_planner.py` prepares the future LLM planning step by validating JSON operation plans.
- `app/templates/index.html` and `app/static/js/app.js` provide the bilingual dashboard.

Generated project assets are kept inside each Godot project folder so the project remains portable.

Godot-related implementation must reference local `godot-docs/`. The Hastur addon follows Godot's documented `addons/<plugin_name>/plugin.cfg` convention and is enabled in `project.godot` under `[editor_plugins]`.
