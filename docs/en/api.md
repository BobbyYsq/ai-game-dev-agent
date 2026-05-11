# API

## Health

`GET /api/health`

Returns the app status and version.

## Settings

`GET /api/settings`

Returns public settings only. API keys and Hastur tokens are never returned.

`POST /api/settings`

Saves local settings in `workspace/config/settings.json`.

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-5.4-mini",
  "llm_base_url": "",
  "llm_api_key": "sk-...",
  "image_provider": "openai",
  "openai_image_model": "gpt-image-2",
  "image_base_url": "",
  "image_api_key": "sk-...",
  "image_size": "1024x1024",
  "image_quality": "medium",
  "hastur_enabled": true,
  "hastur_base_url": "http://localhost:5302",
  "hastur_auth_token": "local-token"
}
```

Supported text providers are `mock`, `openai`, `anthropic`, `deepseek`, `openai_compatible`, and `local_openai_compatible`. Image providers are `mock`, `openai`, and `openai_compatible`. Model IDs are stored as editable strings so the UI can follow each provider's current model catalog instead of forcing stale hard-coded choices.

## Projects

`POST /api/projects/create`

```json
{
  "project_name": "Shadow Garden",
  "game_idea": "A haunted garden top-down action prototype.",
  "project_template": "2d",
  "game_type": "2D top-down action",
  "engine": "Godot 4",
  "prototype_scope": "vertical slice",
  "enable_git": true,
  "generate_docs": true,
  "generate_godot_skeleton": true
}
```

`GET /api/projects`

Lists recent generated projects.

`GET /api/projects/{project_slug}`

Returns project path and generated file list.

## Image Assets

`POST /api/projects/{project_slug}/assets/images/generate`

```json
{
  "prompt": "A haunted garden top-down action game concept art, readable silhouettes, dark fantasy.",
  "purpose": "concept_art",
  "model": "gpt-image-2",
  "size": "1024x1024",
  "quality": "medium"
}
```

Supported purposes:

- `concept_art`
- `gdd_reference`
- `2d_sprite_draft`
- `ui_icon`
- `texture_reference`
- `blender_3d_reference`

Generated files are saved under:

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/cache/images/
```

Metadata is saved to:

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/asset_manifest.json
```

Other asset endpoints:

- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`

## Hastur

`GET /api/hastur/broker/status`

Returns the dashboard-managed broker process status.

`POST /api/hastur/broker/start`

Starts `hastur-operation-plugin-main/broker-server` on the configured local host and ports. If no token exists, the backend generates one and stores it in private settings.

`POST /api/hastur/broker/stop`

Stops the dashboard-managed broker process.

`GET /api/hastur/broker/logs`

Returns recent broker stdout/stderr lines.

`GET /api/hastur/status`

Checks the local Hastur broker at the configured base URL.

`GET /api/hastur/executors`

Lists connected Godot editor executors when the broker is available.

`POST /api/projects/{project_slug}/hastur/apply-operation`

```json
{
  "operation": {
    "operation": "create_node",
    "target_scene": "res://scenes/Main.tscn",
    "node_type": "Node2D",
    "node_name": "GeneratedRoot",
    "parent_path": "."
  }
}
```

The backend validates the operation with Pydantic and converts it into a controlled GDScript snippet. The UI does not expose arbitrary GDScript execution.

`POST /api/projects/{project_slug}/hastur/plan`

Uses the configured LLM provider to generate a validated Godot operation plan from a natural-language instruction.

`POST /api/projects/{project_slug}/hastur/execute-plan`

Executes a previously validated list of operations.

`POST /api/projects/{project_slug}/hastur/plan-and-execute`

Plans and executes in one request.

## Godot Projects

`POST /api/godot-projects/create`

Creates a standalone Godot project, copies `addons/hasturoperationgd/`, enables the plugin in `project.godot`, and writes MIT third-party notices.

```json
{
  "project_name": "Shadow Garden",
  "project_template": "2d",
  "game_type": "2D top-down action",
  "engine": "Godot 4",
  "broker_host": "localhost",
  "broker_port": 5301,
  "enable_git": true
}
```
