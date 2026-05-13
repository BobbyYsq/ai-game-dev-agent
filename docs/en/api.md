# API Reference

## Settings

`GET /api/settings`

Returns public settings only. API keys and Hastur tokens are never returned.

`POST /api/settings`

Saves local settings in `workspace/config/settings.json`. Common dashboard payload:

```json
{
  "llm_api_key": "sk-...",
  "openai_api_key": "sk-...",
  "image_api_key": "sk-...",
  "image_size": "1024x1024",
  "image_quality": "medium"
}
```

The backend infers providers and model defaults. Public provider lists do not include offline placeholder providers.

`POST /api/settings/test-llm`

Runs a small LLM request and returns a readable provider error on failure.

`POST /api/settings/test-image-config`

Runs local image configuration validation without spending image generation credits.

## Projects

`POST /api/godot-projects/create`

Creates a blank Hastur-enabled Godot project and initializes local Git.

```json
{
  "project_name": "Shadow Garden",
  "enable_git": true
}
```

`GET /api/projects`

Lists generated projects.

`GET /api/projects/{project_slug}`

Returns generated project details and files.

## Image Assets

`POST /api/projects/{project_slug}/assets/images/generate`

Generates an image asset using saved image settings.

```json
{
  "prompt": "Readable top-down concept art for a dark fantasy prototype.",
  "purpose": "concept_art",
  "size": "1024x1024",
  "quality": "medium"
}
```

The backend chooses the image model default. The resulting file is stored under:

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/cache/images/
```

The manifest is stored at:

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/asset_manifest.json
```

Other asset endpoints:

- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`

## Hastur

- `POST /api/hastur/broker/start`
- `POST /api/hastur/broker/stop`
- `GET /api/hastur/broker/status`
- `GET /api/hastur/broker/logs`
- `GET /api/hastur/executors`
- `GET /api/hastur/skills`

`POST /api/projects/{project_slug}/hastur/chat`

Sends a chat-style instruction through a vendored Hastur skill. The app injects broker URL and token privately.

```json
{
  "instruction": "/godot-remote-executor Add a Label node and save the scene.",
  "skill_name": "godot-remote-executor",
  "execute": true,
  "confirmed": false,
  "attachments": [
    {
      "filename": "reference.png",
      "media_type": "image/png",
      "data": "base64..."
    }
  ]
}
```

If the operation is interruptive, the response sets `requires_confirmation` and the UI must resend with `confirmed: true`.

Codex-like task streaming:

- `POST /api/projects/{project_slug}/hastur/tasks`
- `GET /api/projects/{project_slug}/hastur/tasks/{task_id}/events`
- `POST /api/projects/{project_slug}/hastur/tasks/{task_id}/resume`

Task events use server-sent events. Event types include `assistant_delta`, `activity`, `context`, `plan_review`, `choice_request`, `skill_confirmation`, `visual_checkpoint`, `step_result`, `question`, `verification`, `final`, and `error`. `question` is kept for compatibility; new clients should render the more specific modal events.

`resume` accepts:

```json
{
  "answer": "optional user feedback",
  "confirmed": true,
  "choice_id": "keep",
  "revision_request": "make the plan smaller"
}
```

Visual checkpoints are served from:

- `GET /api/projects/{project_slug}/visual-checkpoints/{filename}`

## Git

- `GET /api/projects/{project_slug}/git/status`
- `GET /api/projects/{project_slug}/git/review`
- `GET /api/projects/{project_slug}/git/diff`
- `GET /api/projects/{project_slug}/git/changes`
- `GET /api/projects/{project_slug}/git/log`
- `POST /api/projects/{project_slug}/git/commit`
- `POST /api/projects/{project_slug}/git/discard`
- `POST /api/projects/{project_slug}/git/revert`
- `POST /api/projects/{project_slug}/git/restore-file`
- `POST /api/projects/{project_slug}/git/rollback`

`commit` accepts an optional `paths` list and only stages/commits those selected files when provided. `rollback` is deprecated and returns a safe error instead of running `git reset --hard`; use discard selected files, revert commit, or restore selected files from a commit.
