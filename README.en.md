# AI Game Development Agent

AI Game Development Agent is an application-layer workflow platform for generating and iterating Godot game prototypes. It is not a one-prompt commercial game generator. It is a local agent dashboard that turns an idea or GDD into documents, Godot prototype files, visual references, review notes, and later editor operations.

## What v0.3 Provides

- Windows and macOS one-click startup through portable Micromamba.
- FastAPI backend with a bilingual local dashboard.
- UI-based API key, text model, image model, and Hastur broker settings.
- 2D and 3D Godot 4 playable prototype templates.
- Image asset generation pipeline with `mock` and OpenAI providers.
- Default OpenAI image model setting: `gpt-image-2`.
- Image cache under each generated project: `assets/generated/cache/images/`.
- `asset_manifest.json` for generated image metadata.
- Attach generated images to `docs/GDD.md`.
- Mark images as Blender/3D references and generate `docs/BLENDER_REFERENCE_NOTES.md`.
- Safe Hastur bridge endpoints for structured Godot operations.
- Standalone Godot Project panel with automatic Hastur addon copy and editor plugin enablement.
- Dashboard-managed Hastur broker start/stop/status/log controls.
- LLM-driven Godot operation planning with schema validation before execution.
- `AGENTS.md` as the AI-facing project context and local `godot-docs/` workflow rule.

## Quick Start

Windows:

```powershell
start_windows.cmd
```

macOS:

```bash
chmod +x start_macos.command
./start_macos.command
```

On first launch, the bootstrap script downloads portable Micromamba, creates `runtime/envs/ai-game-dev-agent` with `conda-forge` only, installs `requirements.txt`, finds an open port from 8000-8003, starts FastAPI, and opens the browser.

## UI Workflow

1. Open the dashboard.
2. Use the language toggle for English or Chinese.
3. Keep `mock` for offline testing, or choose `openai` and save your API key.
4. Create planning docs from the Project panel, or create a standalone Godot project from the Godot Project panel.
5. Use the Assets panel to generate concept art, GDD references, 2D drafts, UI icons, texture references, or Blender references.
6. Use the Hastur panel to start the local broker, list executors, generate LLM operation plans, and execute validated operations.

Generated projects are written to:

```text
workspace/generated_godot_projects/
```

Private settings are written to:

```text
workspace/config/settings.json
```

This file is excluded from Git and should contain local API keys only.

## API Summary

- `GET /api/health`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/settings/test-llm`
- `POST /api/projects/create`
- `POST /api/godot-projects/create`
- `GET /api/projects`
- `GET /api/projects/{project_slug}`
- `POST /api/projects/{project_slug}/assets/images/generate`
- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`
- `GET /api/hastur/status`
- `GET /api/hastur/executors`
- `GET /api/hastur/broker/status`
- `POST /api/hastur/broker/start`
- `POST /api/hastur/broker/stop`
- `GET /api/hastur/broker/logs`
- `POST /api/projects/{project_slug}/hastur/apply-operation`
- `POST /api/projects/{project_slug}/hastur/plan`
- `POST /api/projects/{project_slug}/hastur/execute-plan`
- `POST /api/projects/{project_slug}/hastur/plan-and-execute`

## Third-Party Notices

Hastur Operation Plugin is vendored in `hastur-operation-plugin-main/` under the MIT License. Generated Godot projects include `addons/hasturoperationgd/`, an enabled editor plugin entry in `project.godot`, `THIRD_PARTY_NOTICES.md`, and `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`.

## Documentation

- [Quickstart](docs/en/quickstart.md)
- [Architecture](docs/en/architecture.md)
- [API](docs/en/api.md)
- [UI Design](docs/en/ui-design.md)
- [File and Function Reference](docs/en/file-reference.md)
- [Roadmap](docs/en/roadmap.md)

## Current Boundaries

v0.3 prepares the image and Godot editor operation pipeline, but it does not yet implement the Claude Blender modeling loop, full arbitrary Godot editor automation, multiplayer systems, cloud auth, billing, or hosted user accounts.
