# 架构说明

## 应用层

- `app/main.py` 创建 FastAPI 应用，挂载静态文件和 dashboard。
- `app/api/` 暴露设置、项目、Godot 项目、图像资产、Hastur 和 Git 路由。
- `app/templates/index.html`、`app/static/js/app.js`、`app/static/css/app.css` 组成本地 UI。

## 服务层

- `settings_service.py` 保存私有设置，隐藏密钥，并迁移旧 provider/model 设置。
- `godot_project_service.py` 创建启用 Hastur 的空白 Godot 项目，并做幂等 Git 初始化。
- `asset_service.py` 生成图像资产、维护 manifest、写入 GDD 和 Blender 参考说明。
- `broker_service.py` 管理本地 Hastur broker 进程。
- `hastur_skill_service.py` 读取 vendored Hastur skills。
- `hastur_task_service.py` 实现 Codex-like 任务会话：流式发送真实 LLM assistant delta，读取 Godot docs 和 skill，生成隐藏的原子计划，弹出计划/方案/skill/视觉确认，逐步生成 Hastur 代码，失败后只修复当前步骤，并验证 broker 状态。
- `hastur_chat_service.py` 保留兼容旧的一次性聊天接口。
- `git_service.py` 封装项目范围内的安全 Git 操作：status、changed files、file diff、选中文件提交/丢弃、log、revert、restore-file。hard reset rollback 已禁用。

## Godot/Hastur 约束

生成项目必须包含：

- `addons/hasturoperationgd/`
- `project.godot` 中启用 Hastur editor plugin
- `[hastur_operation] broker_host="localhost"` 和 `broker_port=5301`
- `THIRD_PARTY_NOTICES.md`
- `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`

任何 Godot 操作前，任务服务都要读取本地 `godot-docs/` 中的相关文档和 vendored skill。
