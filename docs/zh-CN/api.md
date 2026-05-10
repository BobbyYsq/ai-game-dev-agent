# API 说明

启动后的基础地址：

```text
http://127.0.0.1:<port>
```

## 健康检查

`GET /api/health`

返回服务状态。

## 设置

`GET /api/settings`

只返回公开设置。完整 API Key 不会返回到前端。

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

使用当前 provider 发送一个小的测试 prompt。

## 项目

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

响应：

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

返回最近生成的项目列表。

`GET /api/projects/{project_slug}`

返回单个项目路径和文件列表。
