# 文件参考

## 应用入口

- `app/main.py`：创建 FastAPI app，注册静态文件、模板和路由。
- `app/templates/index.html`：管理、LLM + Hastur、图像管线三个视图的结构。
- `app/static/js/app.js`：仪表盘状态、API 调用、skill 选择器、聊天、图像图库和 Git 工作台。
- `app/static/css/app.css`：响应式操作界面样式。

## API 路由

- `app/api/routes_settings.py`：公开设置、保存设置、测试 LLM。
- `app/api/routes_godot_projects.py`：创建空白 Godot 项目。
- `app/api/routes_projects.py`：列出生成项目和项目详情。
- `app/api/routes_hastur.py`：broker 控制、skill、executor、聊天和结构化操作。
- `app/api/routes_assets.py`：图像生成、资产文件、附加到 GDD、标记 Blender 参考。
- `app/api/routes_git.py`：项目本地 Git 状态、审查、diff、日志、提交、还原。

## 服务层

- `app/services/settings_service.py`：本地私有设置、provider 推断、公开设置。
- `app/services/godot_project_service.py`：创建启用 Hastur 的空白 Godot 项目。
- `app/services/hastur_chat_service.py`：LLM + Hastur 聊天 prompt、附件、确认和执行。
- `app/services/hastur_skill_service.py`：发现 vendored Hastur skill。
- `app/services/hastur_service.py`：安全结构化操作验证和 broker 执行。
- `app/services/broker_service.py`：管理本地 Hastur broker 进程。
- `app/services/asset_service.py`：生成图像、manifest、GDD 链接、Blender 说明。
- `app/services/git_service.py`：生成项目范围内的 Git helper。

## Provider Adapter

- `app/models/openai_provider.py`：OpenAI-compatible 聊天、视觉输入和 Anthropic adapter。
- `app/models/llm_provider.py`：根据保存设置选择文本 provider。
- `app/models/image_provider.py`：根据保存设置选择图像 provider。

## Godot 生成

- `app/tools/godot_templates/base.py`：最小 `project.godot`、`Main.tscn`、目录和 Hastur addon 安装。
- `app/tools/godot_templates/template_2d.py`：2D 原型模板。
- `app/tools/godot_templates/template_3d.py`：3D 原型模板。

## 测试

- `tests/test_settings.py`：provider 推断和公开设置。
- `tests/test_assets.py`：生成资产 manifest 和文档链接。
- `tests/test_hastur.py`：结构化操作验证和 GDScript 构造。
- `tests/test_hastur_skills.py`：skill 发现和聊天中隐藏 token。
- `tests/test_git_service.py`：本地 Git 状态和需要确认的 rollback。
