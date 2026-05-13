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
- `POST /api/projects/{project_slug}/hastur/tasks/{task_id}/cancel`

Task events use server-sent events. Public workflow notes stream through `thought_delta`; user-facing plan/result text streams through `assistant_delta`; prompts use the single generic `user_prompt`; terminal states use `final` and `error`. The frontend should render `thought_delta` and `assistant_delta` in the same assistant bubble and should not expect `plan_review`, `choice_request`, or `visual_checkpoint` event types.

`user_prompt.detail` is a generic modal payload:

```json
{
  "title": "Review result",
  "body": "Choose finish, or describe what to adjust next.",
  "choices": [{"id": "finish", "label": "Finish", "action": "finish"}],
  "input_label": "Modification request",
  "image_url": "/api/projects/demo/visual-checkpoints/checkpoint.png",
  "image_status": "available",
  "requires_input": true
}
```

Confirmed mutating plans generate one complete Hastur editor batch. Compile/runtime failures feed the complete broker payload, failed code excerpt, and current goal back to the LLM for whole-batch repair until success, cancellation, or an unrecoverable provider/broker/executor failure.

`resume` accepts:

```json
{
  "answer": "optional user feedback",
  "confirmed": true,
  "choice_id": "keep",
  "revision_request": "make the plan smaller"
}
```

Visual checkpoints are served from the endpoint below only after the backend has verified that the PNG exists and is non-empty:

- `GET /api/projects/{project_slug}/visual-checkpoints/{filename}`

## Git

- `GET /api/projects/{project_slug}/git/status`
- `GET /api/projects/{project_slug}/git/review`
- `GET /api/projects/{project_slug}/git/diff`
- `GET /api/projects/{project_slug}/git/changes`
- `GET /api/projects/{project_slug}/git/log`
- `GET /api/projects/{project_slug}/git/branches`
- `POST /api/projects/{project_slug}/git/commit`
- `POST /api/projects/{project_slug}/git/save`
- `POST /api/projects/{project_slug}/git/branches`
- `POST /api/projects/{project_slug}/git/branches/switch`
- `DELETE /api/projects/{project_slug}/git/branches/{branch_name}`
- `POST /api/projects/{project_slug}/git/merge-to-main`
- `POST /api/projects/{project_slug}/git/discard`
- `POST /api/projects/{project_slug}/git/revert`
- `POST /api/projects/{project_slug}/git/restore-file`
- `POST /api/projects/{project_slug}/git/rollback`

`status` and `changes` include friendly file metadata: `status_kind`, `display_status`, `directory`, and `filename`. New branch creation preserves local uncommitted changes. Branch switching lets Git proceed only when it can do so without overwriting local work. `commit` accepts an optional `paths` list and only stages/commits those selected files when provided.
