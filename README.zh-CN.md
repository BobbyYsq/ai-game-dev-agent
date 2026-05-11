# AI Game Development Agent

AI Game Development Agent 是一个应用层 AI 游戏开发 Agent 平台。它不是“一句话生成完整商业游戏”的工具，而是一个本地 Agent 控制台：把游戏想法或 GDD 转成文档、Godot 原型文件、视觉参考、Review Report，并为后续 Godot 编辑器自动操作做准备。

## v0.3 已提供能力

- Windows / macOS 一键启动，使用 portable Micromamba 自动准备运行环境。
- FastAPI 后端和中英文双语本地控制台。
- 在 UI 中配置 API Key、文本模型、图像模型和 Hastur broker。
- 2D / 3D Godot 4 可运行原型模板。
- 图像资产生成管线，支持 `mock` 和 OpenAI provider。
- 默认 OpenAI 图像模型：`gpt-image-2`。
- 每个生成项目都有图像缓存目录：`assets/generated/cache/images/`。
- 使用 `asset_manifest.json` 记录生成图片的用途、prompt、路径和状态。
- 可将生成图片追加到 `docs/GDD.md`。
- 可将图片标记为 Blender / 3D 建模参考，并生成 `docs/BLENDER_REFERENCE_NOTES.md`。
- Hastur 安全桥接 API：只接收结构化 Godot operation，不在 UI 暴露任意 GDScript 输入。

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

首次启动会自动下载 portable Micromamba，只使用 `conda-forge` 创建 `runtime/envs/ai-game-dev-agent`，安装 `requirements.txt`，在 8000-8003 中寻找可用端口，启动 FastAPI，并打开浏览器。

## UI 工作流

1. 打开控制台。
2. 用右上角按钮切换 English / 中文。
3. 离线测试可使用 `mock`，需要真实模型时选择 `openai` 并保存 API Key。
4. 在 Project 面板创建 2D 或 3D Godot 原型。
5. 在 Assets 面板生成概念图、GDD 参考图、2D 草稿、UI 图标、贴图参考或 Blender 参考图。
6. 只有在本地 Hastur broker 和 Godot 插件启动后，才使用 Hastur 面板执行 Godot 编辑器操作。

生成项目位置：

```text
workspace/generated_godot_projects/
```

私有配置位置：

```text
workspace/config/settings.json
```

该文件已被 Git 忽略，只用于保存本地 API Key 和本地 broker 配置。

## API 摘要

- `GET /api/health`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/settings/test-llm`
- `POST /api/projects/create`
- `GET /api/projects`
- `GET /api/projects/{project_slug}`
- `POST /api/projects/{project_slug}/assets/images/generate`
- `GET /api/projects/{project_slug}/assets`
- `GET /api/projects/{project_slug}/assets/{asset_id}/file`
- `POST /api/projects/{project_slug}/assets/{asset_id}/attach-to-gdd`
- `POST /api/projects/{project_slug}/assets/{asset_id}/mark-blender-reference`
- `GET /api/hastur/status`
- `GET /api/hastur/executors`
- `POST /api/projects/{project_slug}/hastur/apply-operation`

## 文档

- [快速开始](docs/zh-CN/quickstart.md)
- [架构说明](docs/zh-CN/architecture.md)
- [API 说明](docs/zh-CN/api.md)
- [UI 设计](docs/zh-CN/ui-design.md)
- [文件和函数参考](docs/zh-CN/file-reference.md)
- [路线图](docs/zh-CN/roadmap.md)

## 当前边界

v0.3 已经把图像资产和 Godot 编辑器操作桥接的基础管线接进项目，但还没有实现 Claude Blender 自动建模、完整任意 Godot 编辑器操作、多人联机完整系统、云端登录、支付或托管用户系统。
# v0.3 Addendum

- Standalone Godot Project panel creates Godot projects with the Hastur editor plugin copied and enabled automatically.
- The dashboard can start/stop the local Hastur broker, show broker logs, and use the bound LLM to plan validated Godot operations.
- `AGENTS.md` is the AI-facing project context; Godot changes must consult local `godot-docs/` first.
- Hastur Operation Plugin is vendored in `hastur-operation-plugin-main/` under the MIT License. Generated projects include `THIRD_PARTY_NOTICES.md` and `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`.
