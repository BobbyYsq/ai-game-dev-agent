## v0.3.0
- Added image asset generation pipeline with mock/OpenAI providers and `gpt-image-2` as the default image model.
- Added per-project image cache and `assets/generated/asset_manifest.json`.
- Added APIs to generate image assets, list assets, serve image files, attach images to GDD, and mark Blender references.
- Added `BLENDER_REFERENCE_NOTES.md` generation for future Claude Blender workflows.
- Added Hastur settings, status/executor APIs, and safe structured Godot operation execution endpoints.
- Added `godot_operation_planner.py` for validated JSON operation plans.
- Added Assets and Hastur panels to the bilingual dashboard.
- Added pytest smoke tests for assets, settings, and Hastur operation validation.
- Added `AGENTS.md` as the AI-facing project context and Godot-docs workflow rule.
- Added standalone Godot project API/UI with automatic Hastur addon copy and editor plugin enablement.
- Added third-party notices for the vendored MIT-licensed Hastur Operation Plugin.
- Added UI-managed Hastur broker start/stop/status/log endpoints.
- Added LLM Godot operation planning, execute-plan, and plan-and-execute endpoints.

## v0.2.0
- Added cross-platform bootstrap scripts (Windows/macOS/unix).
- Added UI settings with local API key storage.
- Added project generation/list/detail APIs.
- Added bilingual documentation structure.

## v0.2.1
- Implemented real universal bootstrap for Windows/macOS using portable Micromamba.
- Added Godot Project Template selection in the UI.
- Added 2D playable Godot prototype template.
- Added 3D playable Godot prototype template.
- Improved project creation form and recent project list.
- Expanded bilingual documentation.
