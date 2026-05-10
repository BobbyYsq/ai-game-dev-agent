# AI Game Development Agent

AI Game Development Agent 是一个面向 Godot 原型开发的应用层 AI 游戏开发工作流平台。它不是“一次提示词生成完整商业游戏”的工具，而是把用户的一句话需求或 GDD 转换为可迭代的 Godot 原型项目：包含文档、场景、脚本、资产目录、评审报告和后续修复循环的基础结构。

## v0.2.1 已提供能力

- Windows 和 macOS 一键启动入口。
- 首次启动自动在 `runtime/` 下准备 portable Micromamba 环境。
- FastAPI 后端和本地 Web 控制台。
- 在 UI 中配置 LLM provider、OpenAI model 和 API Key。
- API Key 保存在 `workspace/config/settings.json`，并被 `.gitignore` 排除。
- 项目创建 API 和项目创建 UI。
- Godot 4 的 2D / 3D 最小可运行原型模板。
- 自动生成 GDD、技术设计、功能任务、资产列表和评审报告。
- 可选为生成项目执行 Git init 和初始 commit。

## 快速启动

Windows：

```powershell
start_windows.cmd
```

macOS：

```bash
chmod +x start_macos.command
./start_macos.command
```

第一次启动时，脚本会下载 portable Micromamba，只使用 `conda-forge` 创建 `runtime/envs/ai-game-dev-agent`，再从 `requirements.txt` 安装 Python 包，自动选择 8000-8003 中可用端口，启动 FastAPI，并打开浏览器。脚本不使用 Anaconda `defaults` channel。

## UI 使用流程

1. 打开控制台页面。
2. 离线测试时使用 `mock` provider；需要真实 LLM 时选择 `openai` 并填写 API Key。
3. 保存设置，并按需测试连接。
4. 输入项目名称和游戏想法。
5. 选择 `2D Game Prototype` 或 `3D Game Prototype`。
6. 创建项目。
7. 用 Godot 4 打开生成目录，并运行 `scenes/Main.tscn`。

生成项目目录：

```text
workspace/generated_godot_projects/
```

## API 概览

- `GET /api/health`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/settings/test-llm`
- `POST /api/projects/create`
- `GET /api/projects`
- `GET /api/projects/{project_slug}`

创建项目请求示例：

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

## 文档

- [快速开始](docs/zh-CN/quickstart.md)
- [架构说明](docs/zh-CN/architecture.md)
- [API 说明](docs/zh-CN/api.md)
- [UI 设计](docs/zh-CN/ui-design.md)
- [文件与函数说明](docs/zh-CN/file-reference.md)
- [路线图](docs/zh-CN/roadmap.md)

## 路线图

v0.3 计划加入 image-2 图像生成和概念图缓存。v0.4 计划加入 Claude/Blender 3D 资产管线。v0.5 计划接入 Hastur 或其他 Godot 编辑器操作桥。v0.6 计划加入试玩反馈、自动修复、评审报告和 Git commit 循环。
