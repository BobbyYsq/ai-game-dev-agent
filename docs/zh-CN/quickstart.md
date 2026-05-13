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
6. LLM 回复会流式显示；执行状态只出现在活动摘要中，不再伪装成 assistant 回复。
7. 如果 agent 需要计划确认、方案选择、skill 确认或视觉调整，会弹出临时窗口等待你选择。
8. 确认后任务会按最小步骤生成代码、发送给 Hastur 执行，并只针对当前步骤修复失败。

## 6. 使用图像管线

1. 打开 **图像管线**。
2. 选择项目、用途、尺寸和质量。
3. 输入提示词，可上传参考图片或文件。
4. 点击 **生成图像**。
5. 在图库中审查结果，可批准加入 GDD、标记为 Blender 参考或重新生成。

## 7. 使用本地 Git

在 **项目工作台** 中执行 Git 操作；**LLM + Hastur** 页只显示分支和改动数量，并提供打开 Git 工作台的入口：

- **审查改动**：查看 changed files、staged/unstaged/untracked 状态和按文件 diff。
- **提交**：选择文件并输入提交信息后手动提交。
- **历史**：查看最近 commit。
- **丢弃选中文件**：只丢弃你选择的文件改动。
- **反向提交/恢复文件**：使用 `revert commit` 或从指定 commit 恢复指定文件。

当前版本不做 push、PR 或远程 Git 操作。
