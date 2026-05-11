# ROADMAP

## v0.3 Image Generation + Hastur Bridge

Implemented in this branch:

- Image asset generation through `mock` and OpenAI providers.
- Default image model setting: `gpt-image-2`.
- Generated image cache under `assets/generated/cache/images/`.
- `asset_manifest.json` metadata for image assets.
- Attach generated images to `docs/GDD.md`.
- Mark images as Blender references and write `docs/BLENDER_REFERENCE_NOTES.md`.
- Hastur status, executor, and safe structured operation APIs.
- UI panels for Assets, standalone Godot Project creation, and Hastur.
- Automatic Hastur addon installation and editor-plugin enablement for generated Godot projects.
- Local broker-server lifecycle controls from the dashboard.
- LLM operation planning that validates JSON before broker execution.
- AI-facing `AGENTS.md` plus local `godot-docs/` as the required source for Godot changes.

Remaining hardening:

- Verify real OpenAI image generation across account tiers.
- Match Hastur broker payload details against live plugin behavior.
- Add richer operation types after live Godot editor testing.

## v0.4 Claude Blender 3D Pipeline

- Generate Blender Python scripts from selected reference images.
- Run Blender headless.
- Export `.glb` or `.fbx` into `assets/models/`.
- Write Godot import notes for generated 3D assets.

## v0.5 Hastur / Godot Editor Bridge Expansion

- Use LLM-generated operation plans to edit Godot scenes.
- Create nodes, signals, imports, and scene saves through Hastur.
- Read editor state and feed it back into review reports.
- Keep arbitrary GDScript execution behind an admin/debug gate only.

## v0.6 Playtest / Fix / Commit Loop

- Collect user playtest feedback.
- Analyze generated project files and review reports.
- Modify scripts, scenes, docs, and asset manifests.
- Generate a new review report.
- Commit the iteration to Git.
