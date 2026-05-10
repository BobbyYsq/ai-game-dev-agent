# 文件与函数说明

## 根目录

- `start_windows.cmd`：Windows 双击启动入口。
- `start_macos.command`：macOS 启动入口。
- `environment.yml`：Micromamba 环境定义。
- `requirements.txt`：Python 依赖列表。

## Bootstrap

- `bootstrap/bootstrap_windows.ps1`：在 Windows 下载 Micromamba、创建 runtime 环境、选择端口并启动 FastAPI。
- `bootstrap/bootstrap_macos.sh`：在 macOS 执行同样流程，并自动识别 CPU 架构。
- `bootstrap/README_BOOTSTRAP.md`：说明本地 runtime 目录结构。

## 应用入口

- `app/main.py`
  - `create_app()`：创建 FastAPI，挂载 `/static`，注册 routes，并渲染首页。
- `app/config.py`
  - `ensure_workspace_dirs()`：创建工作区目录。

## API Routes

- `app/api/routes_settings.py`
  - `get_settings()`：返回公开设置。
  - `save_settings()`：保存 provider、model 和 API Key。
  - `test_llm_connection()`：调用当前 provider 做连接测试。
- `app/api/routes_projects.py`
  - `create_project()`：验证模板并创建项目。
  - `list_projects()`：列出最近生成项目。
  - `get_project()`：返回单个项目文件列表。

## Services

- `app/services/settings_service.py`
  - `load_private_settings()`：读取本地私有设置。
  - `save_private_settings()`：写入本地私有设置。
  - `get_public_settings()`：隐藏 API Key 明文。
  - `update_settings()`：合并 UI 更新。
- `app/services/project_service.py`
  - `slugify()`：把项目名转换为安全目录名。
  - `create_ai_game_project()`：串联文档、Godot 文件、评审报告和 Git。
- `app/services/git_service.py`
  - `init_repo()`：执行 `git init`。
  - `commit_all()`：执行 stage 和 commit。

## 生成器

- `app/tools/godot_project_tools.py`
  - `generate_godot_template_project()`：分发 `2d` 或 `3d` 模板生成。
- `app/tools/godot_templates/base.py`：共享目录、project.godot 和脚本辅助函数。
- `app/tools/godot_templates/template_2d.py`：生成最小可运行 2D 模板。
- `app/tools/godot_templates/template_3d.py`：生成最小可运行 3D 模板。
