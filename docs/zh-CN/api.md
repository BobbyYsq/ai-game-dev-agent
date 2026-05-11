# API 参考

## 设置

`GET /api/settings`

只返回公开设置。API key 和 Hastur token 不会返回。

`POST /api/settings`

保存本地设置到 `workspace/config/settings.json`。仪表盘常用 payload：

```json
{
  "llm_api_key": "sk-...",
  "openai_api_key": "sk-...",
  "image_api_key": "sk-...",
  "image_size": "1024x1024",
  "image_quality": "medium"
}
```

后端会自动推断 provider 和默认模型。公开 provider 列表不包含离线占位 provider。

`POST /api/settings/test-llm`

发送一次小型 LLM 请求。失败时返回可读 provider 错误。

## 项目

`POST /api/godot-projects/create`

创建启用 Hastur 的空白 Godot 项目，并初始化本地 Git。

```json
{
  "project_name": "Shadow Garden",
  "enable_git": true
}
```

`GET /api/projects`

列出已生成项目。

`GET /api/projects/{project_slug}`

返回项目详情和文件列表。

## 图像资产

`POST /api/projects/{project_slug}/assets/images/generate`

使用已保存图像设置生成图像资产。

```json
{
  "prompt": "Readable top-down concept art for a dark fantasy prototype.",
  "purpose": "concept_art",
  "size": "1024x1024",
  "quality": "medium"
}
```

后端选择默认图像模型。生成文件保存到：

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/cache/images/
```

manifest 保存到：

```text
workspace/generated_godot_projects/<project_slug>/assets/generated/asset_manifest.json
```

其他资产接口：

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

通过 vendored Hastur skill 发送聊天式指令。应用会私下注入 broker URL 和 token。

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

如果操作可能打断状态，响应会设置 `requires_confirmation`，UI 需要用 `confirmed: true` 再发送一次。

## Git

- `GET /api/projects/{project_slug}/git/status`
- `GET /api/projects/{project_slug}/git/review`
- `GET /api/projects/{project_slug}/git/diff`
- `GET /api/projects/{project_slug}/git/log`
- `POST /api/projects/{project_slug}/git/commit`
- `POST /api/projects/{project_slug}/git/rollback`

rollback 需要确认：先用 `confirm: false` 预览，再用 `confirm: true` 执行。
