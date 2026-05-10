# Roadmap

## v0.3 Image Generation Pipeline

- Add an image-2 provider.
- Generate concept art into `assets/generated/cache/images/`.
- Allow images to be linked from `docs/GDD.md`.
- Promote images to 2D sprite, icon, UI, or texture references.
- Prepare selected images as Blender or 3D asset references.

## v0.4 Claude Blender 3D Pipeline

- Generate Blender Python scripts from project goals.
- Run Blender headless when available.
- Export `.glb` or `.fbx` files into `assets/models/`.
- Add review notes for generated 3D assets.

## v0.5 Hastur / Godot Editor Bridge

- Add a real bridge layer in `hastur_bridge.py`.
- Send structured Godot operations to the editor plugin.
- Create scenes, nodes, signals, imports, and editor-side checks.
- Read back operation results for review reports.

## v0.6 Playtest / Fix / Commit Loop

- Collect user playtest feedback.
- Inspect generated project files.
- Produce a fix plan.
- Modify scripts, scenes, and docs.
- Generate a new review report.
- Commit changes with a generated Git message.
