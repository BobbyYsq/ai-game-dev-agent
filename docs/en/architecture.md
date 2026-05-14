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
- `app/api/routes_hastur.py` manages broker status, executors, chat-style Hastur interaction, and task streaming.
- `app/api/routes_skills.py` manages Claude Code-style skills across vendored, global, and project scopes.
- `app/api/routes_assets.py` exposes image generation and asset review actions.
- `app/api/routes_git.py` exposes project-local Git status, changed files, project save, branch, merge-to-main, history, safe restore-to-commit, revert, and selected-file compatibility actions.
- `app/services/settings_service.py` stores private settings locally and hides secrets from public responses.
- `app/services/hastur_chat_service.py` builds the skill-grounded LLM prompt, includes uploaded context, and executes safe Hastur code when allowed.
- `app/services/hastur_skill_service.py` discovers Claude Code-style `SKILL.md` packages from vendored, global, and project locations; parses frontmatter; supports safe user uploads/deletes; and returns lightweight metadata for prompt injection.
- `app/services/hastur_task_service.py` runs the Codex-like Hastur task loop: stream LLM-authored public thoughts, structured task breakdown/progress, and assistant body text into one chat bubble, inject an abstract capability registry plus lightweight skill/Godot-doc indexes, summarize image attachments once, resolve LLM `context_requests` on demand, build hidden plans, pause only through LLM-instantiated modal prompts, generate one complete Hastur editor batch per approved plan/direct action or per LLM-selected sequential subtask, repair failed batches with compact Hastur error context until success/cancel/unrecoverable or repeated-stall failure, and return final answers from execution outputs.
- `app/services/asset_service.py` writes image files, manifests, GDD references, and Blender reference notes.
- `app/services/git_service.py` wraps generated-project-scoped safe Git commands with Godot VCS metadata, friendly changed-file status fields, local-change-preserving branch creation, guarded branch switching, project-level saves, and safe restore-to-commit commits. Hard reset rollback is disabled.

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
- `workspace/skills/`: user-uploaded global skills.
- `workspace/generated_godot_projects/`: generated Godot projects.
- `workspace/cache/`: local caches.
- `runtime/`: local Python runtime created by bootstrap scripts; not committed.
