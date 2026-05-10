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
