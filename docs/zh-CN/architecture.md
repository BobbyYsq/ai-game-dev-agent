# 架构说明

v0.2.1 是一个本地优先的 FastAPI 应用，前端使用轻量 HTML/CSS/JavaScript 控制台。

## 主流程

```text
用户控制台
  -> FastAPI routes
  -> settings/project services
  -> LLM provider 和本地生成器
  -> workspace/generated_godot_projects/<slug>
```

## 后端

- `app/main.py` 创建 FastAPI 应用，挂载静态文件，并渲染首页。
- `app/api/routes_settings.py` 提供设置读取、保存和 LLM 连接测试。
- `app/api/routes_projects.py` 提供项目创建、列表和详情 API。
- `app/services/settings_service.py` 读写本地私有设置。
- `app/services/project_service.py` 串联文档生成、Godot 生成、评审报告和可选 Git commit。

## Agent 层

v0.2.1 的 agent 模块刻意保持简单：它们负责构造 GDD、技术设计、功能任务、资产列表和评审报告的提示词。provider 可以使用 `mock` 做离线测试，也可以使用 `openai` 调用真实模型。

## Godot 生成器

`app/tools/godot_project_tools.py` 根据模板分发到 `app/tools/godot_templates/` 下的模块。2D 和 3D 模板会写入 Godot 场景文本、脚本、项目配置、资产目录和生成资产缓存目录。

## 工作区

- `workspace/config/settings.json` 保存私有设置和 API Key。
- `workspace/generated_godot_projects/` 保存生成的 Godot 项目。
- `workspace/cache/` 预留给未来共享缓存。
- `runtime/` 保存 portable Micromamba 和本地 Python 环境。
## v0.3 管线

当前应用是一个本地 FastAPI 控制平面：

- `app/api/` 提供 settings、project、asset 和 Hastur 路由。
- `app/services/asset_service.py` 负责图像资产生成、缓存写入、manifest 更新、GDD 关联和 Blender 参考说明。
- `app/models/image_provider.py` 抽象 `mock` 和 OpenAI 图像生成，OpenAI 默认模型为 `gpt-image-2`。
- `app/services/hastur_service.py` 校验结构化 Godot operation，并在调用本地 Hastur broker 前转换成受控 GDScript。
- `app/agent/godot_operation_planner.py` 为后续 LLM 规划 Godot 操作做准备，负责校验 JSON operation plan。
- `app/templates/index.html` 和 `app/static/js/app.js` 提供中英文双语控制台。

生成资产保存在每个 Godot 项目目录内部，方便项目迁移和版本管理。
# v0.3 Addendum

- `app/services/broker_service.py` manages the local Hastur broker process and captures logs.
- `app/services/godot_project_service.py` creates standalone Godot projects with automatic Hastur addon integration.
- `app/services/godot_operation_service.py` asks the configured LLM for operation plans, validates them, and executes validated plans.
- Godot-related implementation must reference local `godot-docs/`.
