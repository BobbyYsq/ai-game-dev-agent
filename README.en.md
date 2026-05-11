# AI Game Development Agent

A local control plane for Godot prototypes. It creates Hastur-enabled Godot projects, runs a ChatGPT/OpenCode-style Hastur chat workflow, generates image references, and manages local Git review/commit/restore loops for generated projects.

## Features

- Simple API setup with LLM and image key fields. Provider and model defaults are inferred by the backend.
- Blank Godot project creation with `addons/hasturoperationgd/`, enabled editor plugin settings, `Main.tscn`, notices, and local Git initialization.
- Managed local Hastur broker controls for start, stop, status, logs, and executor discovery.
- Chat UI with one composer, `/` skill detection, file/image attachments, safe execution, and confirmation for interruptive operations.
- Image generation and review gallery with GDD attachment and Blender reference notes.
- Project-local Git workbench for details, review changes, commit, history, and confirmation-gated restore.

## Quick Start

Run `start_windows.cmd`, `start_macos.command`, or `start_unix.sh`, then follow [docs/en/quickstart.md](docs/en/quickstart.md).

## Documentation

- [Quickstart](docs/en/quickstart.md)
- [UI Reference](docs/en/ui-design.md)
- [Architecture](docs/en/architecture.md)
- [API Reference](docs/en/api.md)
- [File Reference](docs/en/file-reference.md)

## Local Data

- Settings and secrets: `workspace/config/settings.json`
- Generated Godot projects: `workspace/generated_godot_projects/`
- Local runtime: `runtime/`

Secrets remain local and are not returned by public settings endpoints.
