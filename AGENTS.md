# AI Game Development Agent Context

## Required Workflow

- Before any repository modification, read this file first.
- After any repository modification, update this file when the project state, task list, architecture, or workflow rules change.
- Before any Godot-related modification, read the relevant local files under `godot-docs/` instead of relying on memory. Relevant sources include:
  - `godot-docs/tutorials/plugins/editor/installing_plugins.rst.txt`
  - `godot-docs/tutorials/plugins/editor/making_plugins.rst.txt`
  - `godot-docs/tutorials/best_practices/project_organization.rst.txt`
  - `godot-docs/getting_started/step_by_step/nodes_and_scenes.rst.txt`

## Project Goal

This repository is a local AI game development control plane for Godot prototypes. It generates planning documents, playable Godot project skeletons, image assets, Blender reference notes, and safe Godot editor operations through a local Hastur broker.

## Current Architecture

- `app/main.py` creates the FastAPI app and mounts the dashboard.
- `app/api/` exposes settings, project, Godot project, asset, and Hastur routes.
- `app/services/project_service.py` coordinates AI document generation and the original combined project workflow.
- `app/tools/godot_templates/` writes Godot 2D/3D scenes, scripts, `project.godot`, and Hastur integration files.
- `app/services/asset_service.py` owns image generation, asset manifests, GDD image attachment, and Blender reference notes.
- `app/services/hastur_service.py` validates structured Godot operations and sends controlled GDScript snippets to Hastur.
- `app/services/broker_service.py` manages the local Hastur broker process from the UI.
- `app/agent/godot_operation_planner.py` validates LLM-created Godot operation plans.
- `hastur-operation-plugin-main/` is a vendored MIT-licensed third-party project.
- `godot-docs/` is the local source of truth for Godot implementation details.

## v0.3 Status

Implemented:

- Image asset generation through mock/OpenAI providers.
- Per-project image cache and `asset_manifest.json`.
- GDD visual reference attachment.
- Blender reference notes.
- Structured Hastur operations and basic UI controls.
- Automatic Hastur addon installation and editor-plugin enablement for newly generated Godot projects.
- UI-managed broker start/stop/status/logs.
- LLM-generated Godot operation plan endpoints with schema validation.

Current Codex task:

- v0.3 completion implementation is in place across backend, UI, docs, tests, and licensing.
- Preserve the safety rule that the UI never exposes arbitrary GDScript input.
- Keep broker defaults local-only: host `localhost`, TCP `5301`, HTTP `5302`.
- Latest verification: `node --check app/static/js/app.js`, `runtime/envs/ai-game-dev-agent/python.exe -m compileall app`, and `runtime/envs/ai-game-dev-agent/python.exe -m pytest` passed.

## Hastur Integration Notes

Hastur Operation Plugin is vendored from `hastur-operation-plugin-main/` under the MIT License. Generated Godot projects must include:

- `addons/hasturoperationgd/`
- `project.godot` with `[editor_plugins] enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")`
- `[hastur_operation] broker_host="localhost"` and `broker_port=5301` unless the UI provides different local settings
- `THIRD_PARTY_NOTICES.md`
- `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`

Do not add the Hastur `GameExecutor` autoload by default in v0.3; editor-side automation is enough for this version.
