# API 参考

## 设置

`GET /api/settings`

返回公开设置状态。不会返回 API key 或 Hastur token。

`POST /api/settings`

保存本地设置到 `workspace/config/settings.json`。

```json
{
  "llm_api_key": "sk-...",
  "openai_api_key": "sk-...",
  "image_api_key": "sk-...",
  "image_size": "1024x1024",
  "image_quality": "medium"
}
```

`POST /api/settings/test-llm`

发送小型 LLM 请求，用于检查 LLM key 是否可用。

`POST /api/settings/test-image-config`

只做本地图像配置检查，不调用付费图像生成接口。

## 项目

`POST /api/godot-projects/create`

创建启用 Hastur 的空白 Godot 项目，并初始化本地 Git。重复创建同名项目时会刷新文件；如果 Git 没有新增改动，会返回成功消息而不是 500。

```json
{
  "project_name": "Shadow Garden",
  "enable_git": true
}
```

`GET /api/projects`

列出已生成项目。

`GET /api/projects/{project_slug}`

返回项目路径和文件列表。

## 图像资产

`POST /api/projects/{project_slug}/assets/images/generate`

使用保存的图像 API key 生成图片，写入项目缓存并更新 manifest。

```json
{
  "prompt": "Readable top-down concept art for a dark fantasy prototype.",
  "purpose": "concept_art",
  "size": "1024x1024",
  "quality": "medium"
}
```

相关接口：

- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`

## Hastur

Broker 与 skill：

- `POST /api/hastur/broker/start`
- `POST /api/hastur/broker/stop`
- `GET /api/hastur/broker/status`
- `GET /api/hastur/broker/logs`
- `GET /api/hastur/executors`
- `GET /api/hastur/skills`

兼容旧聊天接口：

- `POST /api/projects/{project_slug}/hastur/chat`

Codex-like 任务接口：

- `POST /api/projects/{project_slug}/hastur/tasks`
- `GET /api/projects/{project_slug}/hastur/tasks/{task_id}/events`
- `POST /api/projects/{project_slug}/hastur/tasks/{task_id}/resume`

任务创建示例：

```json
{
  "instruction": "/godot-remote-executor Add a Label node and save the scene.",
  "skill_name": "godot-remote-executor",
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

SSE 事件类型包括 `status`、`context`、`plan`、`question`、`hastur_execution`、`verification`、`git`、`final` 和 `error`。

新任务流还会发送 `assistant_delta`、`activity`、`plan_review`、`choice_request`、`skill_confirmation`、`visual_checkpoint`、`step_result`、`final` 和 `error`。`resume` 请求体支持 `answer`、`confirmed`、`choice_id` 和 `revision_request`。视觉 checkpoint 文件可通过 `GET /api/projects/{project_slug}/visual-checkpoints/{filename}` 读取。

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

`commit` 可传入 `paths`，只提交选中文件。`rollback` 已废弃，会返回安全错误，不再执行 `git reset --hard`；请使用丢弃选中文件、反向提交或从指定 commit 恢复文件。
