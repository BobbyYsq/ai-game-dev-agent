# Architecture

The app is a local FastAPI control plane for Godot prototype projects.

```text
Browser dashboard
  -> FastAPI routes in app/api/
  -> services in app/services/
  -> provider adapters in app/models/
  -> generated Godot projects in workspace/generated_godot_projects/
```

## Core Services

- `app/main.py` creates the FastAPI app and serves the dashboard.
- `app/api/routes_settings.py` exposes key saving and LLM connection testing.
- `app/api/routes_godot_projects.py` creates blank Hastur-enabled Godot projects.
- `app/api/routes_hastur.py` manages broker status, skills, executors, and chat-style Hastur interaction.
- `app/api/routes_assets.py` exposes image generation and asset review actions.
- `app/api/routes_git.py` exposes project-local Git review, commit, history, and rollback.
- `app/services/settings_service.py` stores private settings locally and hides secrets from public responses.
- `app/services/hastur_chat_service.py` builds the skill-grounded LLM prompt, includes uploaded context, and executes safe Hastur code when allowed.
- `app/services/asset_service.py` writes image files, manifests, GDD references, and Blender reference notes.
- `app/services/git_service.py` wraps generated-project-scoped Git commands.

## Provider Model

The dashboard only accepts API keys. Provider selection and model defaults are backend concerns. OpenAI is the default provider path; Anthropic, DeepSeek, and OpenAI-compatible settings remain supported through saved configuration for advanced/local deployments.

There is no normal runtime placeholder provider. Missing API keys or provider failures are returned as readable user-facing errors.

## Godot/Hastur Project Shape

Generated projects include:

- `project.godot`
- `scenes/Main.tscn`
- `addons/hasturoperationgd/`
- `docs/GODOT_PROJECT.md`
- third-party notices and Hastur license files

The Hastur editor plugin is enabled in `project.godot`. The app does not add the `GameExecutor` autoload by default.

## Local State

- `workspace/config/settings.json`: private local settings and secrets.
- `workspace/generated_godot_projects/`: generated Godot projects.
- `workspace/cache/`: local caches.
- `runtime/`: local Python runtime created by bootstrap scripts; not committed.
