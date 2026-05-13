# 文件参考

- `app/main.py`：FastAPI 入口。
- `app/api/routes_settings.py`：设置、LLM 测试、图像配置检查。
- `app/api/routes_godot_projects.py`：空白 Godot 项目创建。
- `app/api/routes_assets.py`：图像资产生成与审查动作。
- `app/api/routes_hastur.py`：broker、executor、skill、兼容聊天接口、task streaming/resume/cancel 接口。
- `app/api/routes_git.py`：本地 Git 工作流，包括状态、分支、保存、合并、diff、历史和回档。
- `app/services/settings_service.py`：私有设置、公开设置、provider 默认值推断。
- `app/services/godot_project_service.py`：生成 Godot 项目、安装 Hastur、初始化 Git。
- `app/services/asset_service.py`：图像资产、manifest、GDD 和 Blender 参考。
- `app/services/hastur_task_service.py`：Codex-like Hastur 任务会话、公开 `thought_delta` 思考流、`assistant_delta` 正文流、统一通用提示、完整 batch 生成与持续 repair、取消任务、视觉/执行文本证据和最终输出提取。
- `app/services/hastur_chat_service.py`：兼容的一次性 LLM + Hastur 调用。
- `app/services/git_service.py`：Godot VCS metadata、友好改动状态、分支/保存/合并/回档；hard rollback 已禁用。
- `app/tools/godot_templates/`：Godot 项目模板生成器。
- `hastur-operation-plugin-main/`：vendored Hastur Operation Plugin。
- `godot-docs/`：本地 Godot 文档，是 Godot 相关修改和 LLM 提示上下文的来源。
- `workspace/config/settings.json`：本地私有设置。
- `workspace/generated_godot_projects/`：生成的 Godot 项目。
