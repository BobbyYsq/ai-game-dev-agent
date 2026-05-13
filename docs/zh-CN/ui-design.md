# UI 参考

仪表盘是用于反复开发 Godot 原型的操作工具，分为 **管理**、**LLM + Hastur** 和 **图像管线** 三个模块。

## 管理

### API 设置

- **LLM API 密钥**：用于文本模型访问的密码输入框。保存到 `workspace/config/settings.json`，公开接口不会返回密钥。
- **图像 API 密钥**：用于图像生成。如果同一个 OpenAI key 具有图像权限，可以与 LLM key 相同。
- **保存设置**：保存非空 key、图像尺寸和图像质量；保存后清空输入框。
- **测试 LLM**：发送一个很小的真实 LLM 请求，用于确认 key、账号和网络是否可用。
- **检查图像配置**：只做本地配置检查，不消耗图像额度。它会确认图像 key、provider、尺寸和质量是否可用。
- **API 密钥状态**：显示是否已配置至少一个 key。

UI 不显示 provider、模型或 base URL 控件，这些由后端根据保存的设置自动推断。

### 空白 Godot 项目

- **项目名称**：输入人类可读的项目名，后端会转换为生成目录 slug。
- **创建项目**：创建最小 Godot 项目，安装 Hastur 编辑器插件到 `addons/`，在 `project.godot` 中启用插件，创建 `res://scenes/Main.tscn`，并初始化本地 Git。
- **内联结果**：直接显示在创建表单下方，列出项目路径、生成文件和 Git 初始化结果。

### Hastur Broker

- **启动 Broker**：启动 vendored broker，默认监听 `localhost:5301/5302`。
- **停止 Broker**：停止当前由 UI 管理的 broker 进程。
- **状态**：显示运行状态、PID、端口、base URL 和 token 是否存在，但不显示 token 内容。
- **日志**：显示 broker 最近日志。
- **Executors**：查询已连接的 Godot executor。

### 项目工作台

- **刷新**：重新扫描已生成项目。
- **项目列表**：选择一个项目；右侧输出始终贴着当前选中的项目。
- **详情**：显示项目路径和文件列表。
- **审查改动**：显示分支、干净/有改动状态、改动文件、diff stat 和 diff 预览。
- **审查改动**：打开 Git 工作台，显示分支状态、改动文件、单文件 diff、选中文件提交和选中文件丢弃。
- **提交选中**：必须填写提交信息，并至少选择一个文件。
- **历史**：列出最近 commit，并提供手动 revert 和 restore-file 操作。
- **恢复文件**：只从指定 commit 恢复用户填写的文件。完整 hard rollback 已禁用。

## LLM + Hastur

- **项目选择器**：选择本次任务操作的 Godot 项目。
- **就绪状态**：显示 broker/executor 是否可用。
- **消息时间线**：显示真实 LLM assistant delta；上下文读取、计划确认、执行、视觉 checkpoint、repair、验证和最终摘要进入折叠活动区。
- **单输入框**：唯一的任务输入位置。输入 `/` 会打开内置 Hastur skill 选择器。
- **附件按钮 (`+`)**：上传图片和文件。图片会作为模型输入或参考上下文；文本类文件会摘要进 prompt。
- **发送**：创建 Hastur task session，并通过 SSE 实时流式显示事件。
- **任务弹窗**：计划确认、方案选择、skill 确认和视觉 checkpoint 会出现在临时弹窗中。
- **视觉 checkpoint**：在可用时显示 Godot 视口截图、LLM 视觉分析，以及保持/调整选项。
- **技术细节**：每个事件的原始执行数据放在折叠区域中，默认不展开。
- **本地 Git 面板**：聊天页只读显示分支和 dirty 数量，并提供打开 Git 工作台入口。

UI 不提供任意 GDScript 输入框。执行代码由后端在读取 Godot docs 与 vendored skill 后生成，并通过 Hastur 安全通道发送。

## 图像管线

- **项目**：选择资产归属项目。
- **用途**：记录图片用途，写入 `asset_manifest.json`。
- **尺寸**：选择图像尺寸。
- **质量**：选择图像质量。
- **图像提示词**：输入生成提示。
- **参考文件与图片**：上传参考内容；文本会摘要加入 prompt，文件名会显示在 UI 中。
- **保存图像默认值**：保存尺寸和质量。
- **生成图像**：使用保存的图像 API key 和后端默认图像模型生成图片。
- **图库**：显示生成图片、prompt、模型、路径和审查操作。
- **批准加入 GDD**：把图片追加到 `docs/GDD.md`。
- **标记为 Blender 参考**：把图片加入 `docs/BLENDER_REFERENCE_NOTES.md`。
- **重新生成**：复用该资产 prompt 再生成一次。

## 失败信息

LLM、图像和 Hastur 错误必须显示为用户可理解的信息。除非服务器进程本身不可达，否则笼统的 `Internal Server Error` 都视为 UI bug。
