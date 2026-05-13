# AI 游戏开发 Agent

这是一个面向 Godot 原型开发的本地控制台。它可以创建启用 Hastur 的 Godot 项目，运行流式 LLM + Hastur 任务流程，生成图像参考，并为生成项目提供手动、安全的本地 Git 工作台。

## 功能

- 简化 API 设置：只输入 LLM API key 和图像 API key，提供商与默认模型由后端自动选择。
- 创建空白 Godot 项目：自动安装 `addons/hasturoperationgd/`，启用编辑器插件，生成 `Main.tscn`，写入第三方声明，并初始化本地 Git。
- 管理本地 Hastur Broker：启动、停止、查看状态、日志和已连接 executor。
- LLM + Hastur 任务聊天：单输入框、`/` skill 自动选择、文件/图片附件、真实 LLM 流式回复、计划/选项/skill/视觉确认弹窗，并通过 Hastur 分步执行。
- 图像管线：使用保存的图像 API key 生成参考图，审查后可加入 GDD 或标记为 Blender 参考。
- 本地 Git 工作台：查看选中文件 diff、手动提交、丢弃选中文件、反向提交、从指定 commit 恢复文件。

## 快速开始

在 Windows 上运行 `start_windows.cmd`，macOS 上运行 `start_macos.command`，Linux/Unix 上运行 `start_unix.sh`，然后按照 [docs/zh-CN/quickstart.md](docs/zh-CN/quickstart.md) 配置。

## 文档

- [快速开始](docs/zh-CN/quickstart.md)
- [UI 参考](docs/zh-CN/ui-design.md)
- [架构说明](docs/zh-CN/architecture.md)
- [API 参考](docs/zh-CN/api.md)
- [文件参考](docs/zh-CN/file-reference.md)

## 本地数据

- 设置与密钥：`workspace/config/settings.json`
- 生成的 Godot 项目：`workspace/generated_godot_projects/`
- 本地运行时：`runtime/`

密钥只保存在本地，不会通过公开设置接口返回。
