# 文件参考

- `app/main.py`：FastAPI 入口。
- `app/api/routes_settings.py`：设置、LLM 测试、图像配置检查。
- `app/api/routes_godot_projects.py`：空白 Godot 项目创建。
- `app/api/routes_assets.py`：图像资产生成与审查动作。
- `app/api/routes_hastur.py`：broker、executor、skill、旧聊天接口和 task streaming 接口。
- `app/api/routes_git.py`：本地 Git 工作流。
- `app/services/settings_service.py`：私有设置、公开设置、旧配置迁移。
- `app/services/godot_project_service.py`：生成 Godot 项目、安装 Hastur、初始化 Git。
- `app/services/asset_service.py`：图像资产、manifest、GDD 和 Blender 参考。
- `app/services/hastur_task_service.py`：Codex-like Hastur 任务会话、真实 LLM 流式输出、计划/选择/视觉确认和 SSE 事件。
- `app/services/hastur_chat_service.py`：兼容的一次性 LLM + Hastur 调用。
- `app/services/git_service.py`：Git status、changed files、file diff、选中文件提交/丢弃、revert、restore-file；hard rollback 已禁用。
- `app/tools/godot_templates/`：Godot 项目模板生成器。
- `hastur-operation-plugin-main/`：vendored Hastur Operation Plugin。
- `godot-docs/`：本地 Godot 文档，Godot 相关修改的依据。
- `workspace/config/settings.json`：本地私有设置。
- `workspace/generated_godot_projects/`：生成的 Godot 项目。
