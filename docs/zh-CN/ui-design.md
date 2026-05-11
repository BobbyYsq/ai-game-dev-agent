# UI 设计

控制台是一个工作型界面，不是营销页面。它围绕重复使用流程设计：配置模型、创建原型、查看生成文件、重新打开最近项目。

## Settings Panel

字段：

- LLM Provider：`mock` 或 `openai`。
- OpenAI Model：OpenAI provider 使用的模型名。
- OpenAI API Key：密码输入框。保存后会清空输入框。

该区域会显示是否已配置 API Key，但不会显示密钥明文。

## Create Project Panel

字段：

- Project Name
- Game Idea
- Godot Project Template：`2D Game Prototype` 或 `3D Game Prototype`
- Game Type
- Engine Version
- Prototype Scope
- Enable Git
- Generate Documentation
- Generate Godot Prototype

创建按钮会向 `POST /api/projects/create` 发送一个结构化请求。

## Recent Projects Panel

页面加载时调用 `GET /api/projects`。详情按钮调用 `GET /api/projects/{slug}` 并显示文件列表。

## Output Panel

输出区域展示项目 slug、模板、路径、评审摘要、下一步、生成文件和请求错误。
## v0.3 面板

- Settings：选择 `mock` 或 `openai`，选择文本模型，并在本地保存 API Key。
- Create Project：提交项目名称、GDD/想法、Godot 模板、游戏类型、引擎版本和原型范围。启动应用不会自动创建项目。
- Recent Projects：查看已生成项目和文件列表，详情输出限制在面板内滚动。
- Assets：选择已有项目，选择图像用途，输入 prompt，生成图像，加入 GDD，或标记为 Blender 参考图。
- Hastur Bridge：保存 broker 设置，检查状态，加载执行器，并执行安全测试 operation。

语言切换按钮会在英文和中文之间切换控制台文案，不会改变已保存项目数据。
# v0.3 Addendum

- Godot Project panel creates a standalone Godot project with Hastur copied and enabled automatically.
- Hastur Bridge panel can start/stop the broker, inspect status/logs, generate LLM operation plans, and execute validated plans.
