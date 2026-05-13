# API 参考

## 设置

- `GET /api/settings`：返回公开设置，不返回 API key 或 Hastur token。
- `POST /api/settings`：保存本地设置到 `workspace/config/settings.json`。
- `POST /api/settings/test-llm`：发送小型 LLM 请求检查 key 是否可用。
- `POST /api/settings/test-image-config`：只做本地图像配置检查。

## 项目

- `POST /api/godot-projects/create`：创建启用 Hastur 的空白 Godot 项目，并初始化本地 Git。
- `GET /api/projects`：列出已生成项目。
- `GET /api/projects/{project_slug}`：返回项目路径和文件列表。

## 图像资产

- `POST /api/projects/{project_slug}/assets/images/generate`
- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`

## Hastur

Broker 和 skill：

- `POST /api/hastur/broker/start`
- `POST /api/hastur/broker/stop`
- `GET /api/hastur/broker/status`
- `GET /api/hastur/broker/logs`
- `GET /api/hastur/executors`
- `GET /api/hastur/skills`

兼容聊天接口：

- `POST /api/projects/{project_slug}/hastur/chat`

Codex-like 任务接口：

- `POST /api/projects/{project_slug}/hastur/tasks`
- `GET /api/projects/{project_slug}/hastur/tasks/{task_id}/events`
- `POST /api/projects/{project_slug}/hastur/tasks/{task_id}/resume`
- `POST /api/projects/{project_slug}/hastur/tasks/{task_id}/cancel`

SSE 中，公开工作流思考通过 `thought_delta` 流式返回；用户可见计划/结果正文通过 `assistant_delta` 流式返回；需要用户输入时只使用统一的 `user_prompt`；结束状态使用 `final` 或 `error`。前端应把 `thought_delta` 和 `assistant_delta` 渲染在同一个 assistant 气泡中，不再依赖 `plan_review`、`choice_request` 或 `visual_checkpoint` 专用事件。

`user_prompt.detail` 是通用弹窗载荷，字段固定为 `title`、`body`、`choices`、`input_label`、`requires_input`。详细计划只出现在聊天正文中，弹窗只负责确认、选择或修改意见。

确认后的修改型任务会生成一个完整的 Hastur editor batch。编译或运行失败时，后端把完整 broker payload、失败代码摘要和当前目标发回 LLM，让 LLM 继续生成完整修复 batch，直到成功、用户取消或 provider/broker/executor 不可恢复失败。

任务流不再生成截图 review/checkpoint 弹窗；视觉判断来自用户上传图片的 LLM 摘要或 Hastur 返回的文本证据。

## Git

- `GET /api/projects/{project_slug}/git/status`
- `GET /api/projects/{project_slug}/git/review`
- `GET /api/projects/{project_slug}/git/diff`
- `GET /api/projects/{project_slug}/git/changes`
- `GET /api/projects/{project_slug}/git/log`
- `GET /api/projects/{project_slug}/git/branches`
- `POST /api/projects/{project_slug}/git/save`
- `POST /api/projects/{project_slug}/git/branches`
- `POST /api/projects/{project_slug}/git/branches/switch`
- `DELETE /api/projects/{project_slug}/git/branches/{branch_name}`
- `POST /api/projects/{project_slug}/git/merge-to-main`
- `POST /api/projects/{project_slug}/git/commit`
- `POST /api/projects/{project_slug}/git/discard`
- `POST /api/projects/{project_slug}/git/revert`
- `POST /api/projects/{project_slug}/git/restore-file`
- `POST /api/projects/{project_slug}/git/rollback`

`status` 和 `changes` 返回 `status_kind`、`display_status`、`directory`、`filename` 等友好字段。新建分支会保留未提交本地改动；切换分支只在 Git 判断不会覆盖本地改动时执行。`rollback` 使用安全恢复提交，不执行 `git reset --hard`。
