# API

## 健康检查

`GET /api/health`

返回应用状态和版本。

## 设置

`GET /api/settings`

只返回公开设置，不返回 API Key 或 Hastur token 明文。

`POST /api/settings`

保存本地设置到 `workspace/config/settings.json`。

```json
{
  "llm_provider": "openai",
  "openai_model": "gpt-4.1-mini",
  "openai_api_key": "sk-...",
  "image_provider": "openai",
  "openai_image_model": "gpt-image-2",
  "image_size": "1024x1024",
  "image_quality": "medium",
  "hastur_enabled": true,
  "hastur_base_url": "http://localhost:5302",
  "hastur_auth_token": "local-token"
}
```

## 项目

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

列出最近生成的项目。

`GET /api/projects/{project_slug}`

返回项目路径和生成文件列表。

## 图像资产

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

支持的用途：

- `concept_art`
- `gdd_reference`
- `2d_sprite_draft`
- `ui_icon`
- `texture_reference`
- `blender_3d_reference`

生成图片保存到：

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/cache/images/
```

资产元数据保存到：

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/asset_manifest.json
```

其他资产接口：

- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`

## Hastur

`GET /api/hastur/status`

检查本地 Hastur broker。

`GET /api/hastur/executors`

当 broker 可用时，列出已连接的 Godot 编辑器实例。

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

后端会用 Pydantic 校验 operation，再转换为受控 GDScript。UI 不开放任意 GDScript 输入。
# v0.3 Addendum

- `POST /api/godot-projects/create`
- `GET /api/hastur/broker/status`
- `POST /api/hastur/broker/start`
- `POST /api/hastur/broker/stop`
- `GET /api/hastur/broker/logs`
- `POST /api/projects/{project_slug}/hastur/plan`
- `POST /api/projects/{project_slug}/hastur/execute-plan`
- `POST /api/projects/{project_slug}/hastur/plan-and-execute`
