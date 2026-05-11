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

This repository is a local AI game development control plane for Godot prototypes. It creates playable Godot project skeletons, generates planning/reference assets, supports image review, and safely operates Godot through a local Hastur broker and vendored Hastur skills.

## Current Architecture

- `app/main.py` creates the FastAPI app and mounts the dashboard.
- `app/api/` exposes settings, project, Godot project, asset, Hastur, and Git routes.
- `app/services/settings_service.py` stores private local settings, hides secrets from public settings, and infers provider defaults from API keys/saved settings.
- `app/services/project_service.py` coordinates the older combined AI document/project workflow.
- `app/services/godot_project_service.py` creates blank Hastur-enabled Godot projects with local Git initialization.
- `app/tools/godot_templates/` writes Godot 2D/3D scenes, scripts, `project.godot`, and Hastur integration files.
- `app/services/asset_service.py` owns image generation, asset manifests, GDD image attachment, and Blender reference notes.
- `app/services/hastur_service.py` validates structured Godot operations and sends controlled GDScript snippets to Hastur.
- `app/services/broker_service.py` manages the local Hastur broker process from the UI.
- `app/services/hastur_skill_service.py` discovers vendored Hastur skills from `hastur-operation-plugin-main/.claude/skills/`.
- `app/services/hastur_chat_service.py` binds saved LLM settings, uploaded file/image context, vendored Hastur skill instructions, and private broker token state for the single-composer LLM + Hastur chat endpoint.
- `app/services/git_service.py` provides generated-project-scoped Git status, review, diff, log, commit, and confirmation-gated rollback helpers.
- `app/agent/godot_operation_planner.py` validates LLM-created Godot operation plans.
- The dashboard is split into Management, LLM + Hastur Chat, and Image Pipeline views.
- The Management view owns API keys, blank Godot project creation, Hastur broker controls, and the project-local Git workbench.
- The LLM + Hastur view is a ChatGPT/OpenCode-style chat UI with one input, `/` skill detection, file/image attachments, and confirmation buttons for interruptive execution.
- The Image Pipeline view owns image generation, reference uploads, generated asset gallery review, GDD attachment, and Blender reference markers.
- `hastur-operation-plugin-main/` is a vendored MIT-licensed third-party project.
- `godot-docs/` is the local source of truth for Godot implementation details.

## v0.4 Status

Implemented:

- Runtime user-facing placeholder providers have been removed from normal app flows.
- API settings UI only exposes LLM and image API key inputs; provider/model controls are backend-only.
- Provider failures from LLM, image, and Hastur chat endpoints are converted into readable client errors instead of generic `Internal Server Error`.
- Image asset generation through saved OpenAI/OpenAI-compatible settings.
- Per-project image cache and `asset_manifest.json`.
- GDD visual reference attachment.
- Blender reference notes.
- Structured Hastur operations and broker controls.
- Automatic Hastur addon installation and editor-plugin enablement for newly generated Godot projects.
- UI-managed broker start/stop/status/logs.
- LLM-generated Godot operation plan endpoints with schema validation.
- Vendored Hastur skill discovery from `hastur-operation-plugin-main/.claude/skills/`.
- Chat-style LLM + Hastur endpoint with optional uploaded file/image context and private token/base URL binding.
- Generated-project Git status, review, diff, log, commit, and confirmation-gated rollback endpoints.
- Blank Hastur-enabled Godot project creation with a minimal `Main.tscn` and automatic Git initialization.
- Rewritten English and Chinese docs for quickstart, UI reference, architecture, API, and file reference.

Current Codex task:

- The UI/provider/Git redesign has been implemented across backend, UI, docs, and tests.
- Keep the UI free of advanced provider/model controls; provider detection should remain automatic from keys/saved settings.
- Preserve the safety rule that the UI never exposes arbitrary GDScript input.
- Keep broker defaults local-only: host `localhost`, TCP `5301`, HTTP `5302`.
- Use local Godot docs before Godot-related changes.

## Hastur Integration Notes

Hastur Operation Plugin is vendored from `hastur-operation-plugin-main/` under the MIT License. Generated Godot projects must include:

- `addons/hasturoperationgd/`
- `project.godot` with `[editor_plugins] enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")`
- `[hastur_operation] broker_host="localhost"` and `broker_port=5301` unless the UI provides different local settings
- `THIRD_PARTY_NOTICES.md`
- `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`

Do not add the Hastur `GameExecutor` autoload by default; editor-side automation is enough for this version.
