# AI 游戏开发 Agent

这是一个本地 Godot 原型控制台。它可以创建启用 Hastur 的 Godot 项目，提供 ChatGPT/OpenCode 风格的 Hastur 聊天工作流，生成图像参考，并为生成项目提供本地 Git 审查、提交和还原流程。

## 功能

- 简化 API 设置，只保留 LLM key 和图像 key。provider 与默认模型由后端自动判断。
- 创建空白 Godot 项目，包含 `addons/hasturoperationgd/`、已启用的编辑器插件设置、`Main.tscn`、第三方声明和本地 Git 初始化。
- 管理本地 Hastur broker：启动、停止、状态、日志和 executor 查询。
- 单输入框聊天 UI，支持 `/` 自动识别 skill、文件/图片附件、安全执行和打断性操作确认。
- 图像生成与审查图库，支持附加到 GDD 和写入 Blender 参考说明。
- 项目本地 Git 工作台：详情、审查改动、提交、历史、确认后还原。

## 快速开始

运行 `start_windows.cmd`、`start_macos.command` 或 `start_unix.sh`，然后参考 [docs/zh-CN/quickstart.md](docs/zh-CN/quickstart.md)。

## 文档

- [快速开始](docs/zh-CN/quickstart.md)
- [UI 模块说明](docs/zh-CN/ui-design.md)
- [架构](docs/zh-CN/architecture.md)
- [API 参考](docs/zh-CN/api.md)
- [文件参考](docs/zh-CN/file-reference.md)

## 本地数据

- 设置与密钥：`workspace/config/settings.json`
- 生成的 Godot 项目：`workspace/generated_godot_projects/`
- 本地运行时：`runtime/`

密钥只保存在本地，公开设置接口不会返回明文。
