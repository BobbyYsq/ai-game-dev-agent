# 快速开始

## 1. 启动应用

Windows：

```text
start_windows.cmd
```

macOS：

```bash
chmod +x start_macos.command
./start_macos.command
```

Linux：

```bash
chmod +x start_unix.sh
./start_unix.sh
```

启动脚本会创建本地 `runtime/` 环境、安装依赖、选择可用 FastAPI 端口，并打开仪表盘。

## 2. 配置 API key

1. 打开 **管理**。
2. 在 **LLM API 密钥** 中粘贴文本模型 API key。
3. 在 **图像 API 密钥** 中粘贴支持图像生成的 API key。使用 OpenAI 时，如果账号有图像权限，可以填写同一个 key。
4. 点击 **保存设置**。
5. 点击 **测试 LLM**。如果 key、账号权限或网络有问题，界面会直接显示具体错误。

界面不再暴露 provider、模型、base URL 等高级选项。后端会根据 key 和已保存设置自动选择提供商与默认模型。OpenAI 图像生成使用后端默认图像模型，并遵循 OpenAI Image API 的调用方式。

## 3. 创建并打开 Godot 项目

1. 在 **空白 Godot 项目** 中输入项目名称。
2. 点击 **创建项目**。
3. 用 Godot 4 打开 `workspace/generated_godot_projects/<project-slug>/`。
4. 确认项目中存在 `addons/hasturoperationgd/`，并且 `project.godot` 已启用插件。
5. 打开 `res://scenes/Main.tscn`。

Godot 本地文档说明编辑器插件应放在 `addons/` 下，并通过 `Project > Project Settings > Plugins` 启用。生成项目遵循这个结构，主场景路径写入 `project.godot`。

## 4. 启动 Hastur 并与 Godot 交互

1. 在 **Hastur Broker** 中点击 **启动 Broker**。
2. 打开或重新加载生成的 Godot 项目，让 executor 连接 broker。
3. 点击 **Executors**，确认已有 Godot executor。
4. 打开 **LLM + Hastur**。
5. 选择项目。
6. 在输入框中输入 `/`，选择内置 Hastur skill。
7. 需要时用 `+` 上传参考文件或图片。
8. 发送请求。安全操作会通过 Hastur 执行；可能打断编辑器或运行状态的操作会先出现确认按钮。

界面不会让用户输入任意 GDScript。LLM 会读取 vendored skill 指令，broker URL 与 token 由应用私下注入。

## 5. 生成并审查图像

1. 打开 **图像管线**。
2. 选择项目和用途。
3. 选择尺寸与质量。
4. 输入图像提示词，可附加参考文件或图片。
5. 点击 **生成图像**。
6. 在图库中审查结果。
7. 点击 **批准到 GDD**，把图片写入 `docs/GDD.md`。
8. 点击 **标记 Blender 参考**，把图片写入 `docs/BLENDER_REFERENCE_NOTES.md`。

## 6. 使用本地 Git

1. 打开 **管理** 中的 **项目工作台**。
2. 选择项目。
3. 点击 **审查改动** 查看状态、文件列表和 diff。
4. 点击 **提交**，输入提交信息，并提交项目中的全部本地改动。
5. 点击 **历史** 查看最近 commit。
6. 点击 **还原**，输入 commit hash，先预览，再确认执行。

当前版本只管理本地 Git，不包含远程 push 或 PR 流程。
