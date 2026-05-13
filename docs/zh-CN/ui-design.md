# UI 参考

仪表盘用于反复开发 Godot 原型，分为 **管理**、**LLM + Hastur** 和 **图像管线**。

## 管理

### API 设置

- **LLM API Key**：文本模型访问密钥，保存在 `workspace/config/settings.json`，公开接口不会返回。
- **图像 API Key**：图像生成访问密钥。
- **保存设置**：保存非空 key 和图像默认值，保存后清空输入框。
- **测试 LLM**：发送小型真实请求，展示 provider 返回的可读错误。
- **测试图像配置**：只验证本地配置，不消耗图像额度。

UI 不显示 provider、model 或 base URL 控件，这些由后端根据保存设置自动推断。

### 空白 Godot 项目

- **项目名称**：输入人类可读名称，后端转换为目录 slug。
- **创建项目**：创建最小 Godot 项目，安装并启用 Hastur editor plugin，创建 `res://scenes/Main.tscn`，并初始化本地 Git。

### 项目工作台

- **刷新**：重新扫描已生成项目。
- **详情**：显示项目路径和文件列表。
- **Git 工作台**：显示分支状态、项目级保存/合并操作、友好的改动状态标签，以及可折叠的目录分组。
- **新建分支**：从当前保存点创建并切换分支，同时保留未提交的本地改动。
- **保存**：提交整个项目的当前改动。
- **历史图**：列出最近提交，并提供安全回档到指定保存点。完整 hard reset 已禁用。

### Hastur Broker

- **启动 Broker**：按本地默认值 `localhost:5301/5302` 启动 vendored broker。
- **停止 Broker**：只停止由 UI 管理的 broker。
- **状态/日志/Executors**：检查运行状态、端口、token 是否存在和 Godot executor 连接情况；不会显示 token 内容。

## LLM + Hastur

- **项目选择器**：选择本次任务操作的 Godot 项目。
- **就绪状态**：显示 broker/executor 是否可用。
- **消息历史**：同一个 assistant 气泡上方显示公开 `thought_delta` 工作流思考，下方显示 `assistant_delta` 正文；不再显示单独的活动摘要或执行记录区域。
- **输入框**：唯一任务输入位置；输入 `/` 会打开 vendored Hastur skill 选择器。
- **附件按钮 (`+`)**：上传图片和文件，作为模型输入或上下文。
- **发送**：创建 Hastur task session，流式显示思考与正文；确认计划后一次生成完整 Hastur batch 执行。
- **停止**：取消当前任务，防止长时间 repair 循环无法退出。
- **任务弹窗**：唯一弹窗是通用 prompt modal，通过 `title`、`body`、`choices`、`input_label`、`requires_input` 处理计划确认、方案选择和修改意见。详细计划只在聊天正文中显示。
- **本地 Git 面板**：聊天页只读显示分支和改动数量，并提供打开 Git 工作台入口。

UI 不提供任意 GDScript 输入框。执行代码由后端在读取 Godot docs 与轻量 skill 信息后生成，并通过 Hastur 安全通道发送；完整 skill 正文只在显式选择或 LLM 请求上下文时加载。

## 图像管线

- **项目**：选择资产归属项目。
- **用途**：记录图片用途并写入 `asset_manifest.json`。
- **图像 Prompt**：输入生成提示。
- **参考文件与图片**：上传参考上下文。
- **生成图像**：使用保存的图像 API key 和后端默认模型生成图片。
- **批准加入 GDD**：把图片追加到 `docs/GDD.md`。
- **标记为 Blender 参考**：把图片加入 `docs/BLENDER_REFERENCE_NOTES.md`。

## 失败消息

LLM、图像和 Hastur 错误必须显示为用户可理解的消息。除非服务器进程本身不可达，否则泛化的 `Internal Server Error` 都视为 UI bug。
