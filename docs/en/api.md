# API

Base URL after startup:

```text
http://127.0.0.1:<port>
```

## Health

`GET /api/health`

Returns service status.

## Settings

`GET /api/settings`

Returns public settings only. The API key is never returned in plaintext.

```json
{
  "llm_provider": "mock",
  "openai_model": "gpt-4.1-mini",
  "has_openai_api_key": false
}
```

`POST /api/settings`

```json
{
  "llm_provider": "openai",
  "openai_model": "gpt-4.1-mini",
  "openai_api_key": "sk-..."
}
```

`POST /api/settings/test-llm`

Calls the active provider with a small ping prompt.

## Projects

`POST /api/projects/create`

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

Response:

```json
{
  "success": true,
  "project_slug": "shadow-garden",
  "project_path": "workspace/generated_godot_projects/shadow-garden",
  "generated_files": ["project.godot", "scenes/Main.tscn"],
  "review_summary": "Created a playable Godot prototype.",
  "next_steps": ["Open project in Godot 4."],
  "project_template": "2d"
}
```

`GET /api/projects`

Lists recent generated projects.

`GET /api/projects/{project_slug}`

Returns the project path and generated file list.
