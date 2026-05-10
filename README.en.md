# AI Game Development Agent (MVP v0.2)

## What this project is
An application-layer AI game development workflow platform for Godot prototypes.

## What it can do
- One-click startup on Windows/macOS.
- Configure LLM/API key in the UI.
- Generate Godot project skeleton, docs, starter scripts, and review report.

## What it does NOT guarantee
It does not generate a complete commercial game in one shot.

## Quick start
- Windows: double-click `start_windows.cmd`
- macOS: run/double-click `start_macos.command` (may need `chmod +x start_macos.command`)

See `docs/en/quickstart.md` for details.


## v0.2.1 Update
- Universal bootstrap (Windows/macOS) with portable micromamba and runtime/env reuse.
- Settings panel supports provider dropdown and API key masked state.
- Project creation supports project_template (2d/3d) and recent project list.
- Godot generator now creates playable 2D/3D prototype file sets.
