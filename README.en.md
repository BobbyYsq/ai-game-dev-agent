# AI Game Development Agent

AI Game Development Agent is an application-layer workflow platform for generating and iterating Godot game prototypes. The goal is not to create a complete commercial game in one prompt. The goal is to turn a short idea or GDD into a playable prototype folder with documents, Godot scenes, scripts, review notes, and a path for later AI-assisted iteration.

## What v0.2.1 Provides

- Windows and macOS one-click startup scripts.
- First-run portable Micromamba runtime setup under `runtime/`.
- FastAPI backend with a small local dashboard.
- UI-based LLM provider, OpenAI model, and API key configuration.
- API key storage in `workspace/config/settings.json`, excluded from Git.
- Project creation API and UI.
- 2D and 3D Godot 4 playable prototype templates.
- Generated GDD, technical design, feature task list, asset list, and review report.
- Git initialization and initial commit for generated projects when enabled.

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

On first launch, the bootstrap script downloads portable Micromamba, creates `runtime/envs/ai-game-dev-agent` with `conda-forge` only, installs Python packages from `requirements.txt`, finds an open port from 8000-8003, starts FastAPI, and opens the browser. It does not use Anaconda `defaults`.

## UI Workflow

1. Open the dashboard.
2. Keep `mock` provider for offline testing, or choose `openai` and enter an API key.
3. Save settings and optionally test the connection.
4. Enter a project name and game idea.
5. Choose `2D Game Prototype` or `3D Game Prototype`.
6. Create the project.
7. Open the generated folder in Godot 4 and run `scenes/Main.tscn`.

Generated projects are written to:

```text
workspace/generated_godot_projects/
```

## API Summary

- `GET /api/health`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/settings/test-llm`
- `POST /api/projects/create`
- `GET /api/projects`
- `GET /api/projects/{project_slug}`

Example project request:

```json
{
  "project_name": "Shadow Garden",
  "game_idea": "A 2D top-down action prototype in a haunted garden.",
  "project_template": "2d",
  "game_type": "2D top-down action",
  "engine": "Godot 4",
  "prototype_scope": "vertical slice",
  "enable_git": true,
  "generate_docs": true,
  "generate_godot_skeleton": true
}
```

## Documentation

- [Quickstart](docs/en/quickstart.md)
- [Architecture](docs/en/architecture.md)
- [API](docs/en/api.md)
- [UI Design](docs/en/ui-design.md)
- [File and Function Reference](docs/en/file-reference.md)
- [Roadmap](docs/en/roadmap.md)

## Roadmap

v0.3 will focus on image generation with image-2 and cached concept art. v0.4 will add a Claude/Blender 3D asset pipeline. v0.5 will connect to Hastur or another Godot editor bridge. v0.6 will add a playtest, fix, review, and Git commit loop.
