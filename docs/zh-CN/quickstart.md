# 快速开始

## 1. 启动应用

Windows：

```powershell
start_windows.cmd
```

macOS：

```bash
./start_macos.command
```

Linux/Unix：

```bash
./start_unix.sh
```

启动后打开 `http://localhost:8000/`。

## 2. 配置 API

1. 打开 **管理**。
2. 在 **LLM API 密钥** 中粘贴 ChatGPT/OpenAI API key。
3. 在 **图像 API 密钥** 中粘贴可使用图像生成的 API key。
4. 点击 **保存设置**。
5. 点击 **测试 LLM** 检查文本模型。
6. 点击 **检查图像配置** 检查图像 key 和本地默认参数。

## 3. 创建 Godot 项目

1. 在 **空白 Godot 项目** 输入项目名称。
2. 点击 **创建项目**。
3. 项目会生成在 `workspace/generated_godot_projects/<slug>/`。
4. 使用 Godot 打开该项目，确认插件列表中 Hastur 已启用。

## 4. 启动 Hastur

1. 在 **Hastur Broker** 点击 **启动 Broker**。
2. 打开 Godot 项目并等待 executor 连接。
3. 点击 **Executors** 检查连接状态。

## 5. 使用 LLM + Hastur

1. 打开 **LLM + Hastur**。
2. 选择项目。
3. 在输入框输入任务，也可以输入 `/` 选择内置 skill。
4. 上传需要的图片或文件。
5. 点击 **发送**。
6. LLM 回复会像 ChatGPT 一样在同一个 assistant 气泡中流式显示公开思考和正文；最终消息会优先返回真实 Hastur 执行输出。
7. 运行中可以点击 **停止** 取消当前任务。
8. 如果 agent 需要计划确认、方案选择、视觉检查或修改意见，会弹出同一个通用窗口等待你选择；详细计划只在聊天正文中显示。
9. 确认后任务会一次生成完整 Hastur batch 并执行；如果 batch 失败，agent 会把完整 Hastur 错误、broker payload 和失败代码摘要继续发回 LLM 修复，直到成功、你取消，或 broker/executor/provider 不可用。

## 6. 使用图像管线

1. 打开 **图像管线**。
2. 选择项目、用途、尺寸和质量。
3. 输入提示词，可上传参考图片或文件。
4. 点击 **生成图像**。
5. 在图库中审查结果，可批准加入 GDD、标记为 Blender 参考或重新生成。

## 7. 使用本地 Git

在 **项目工作台** 中执行 Git 操作；**LLM + Hastur** 页只显示分支和改动数量，并提供打开 Git 工作台的入口：

- **改动文件**：按目录折叠显示文件，使用“新增”“修改”“删除”等可读状态。
- **新建分支**：允许在有本地改动时从当前保存点创建并切换分支，未提交改动会保留在工作区。
- **保存**：输入保存说明后提交整个项目的当前改动。
- **合并到 main**：把当前分支合并回 `main`；如果会覆盖本地改动，先保存或丢弃受影响文件。
- **历史图**：查看最近 commit，并可安全回档到指定保存点。

当前版本不做 push、PR 或远程 Git 操作。
