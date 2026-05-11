# 架构

本应用是一个本地 FastAPI 控制台，用于管理 Godot 原型项目。

```text
浏览器仪表盘
  -> app/api/ 中的 FastAPI 路由
  -> app/services/ 中的服务层
  -> app/models/ 中的 provider adapter
  -> workspace/generated_godot_projects/ 中的生成项目
```

## 核心服务

- `app/main.py` 创建 FastAPI app 并提供仪表盘。
- `app/api/routes_settings.py` 提供 key 保存和 LLM 连接测试。
- `app/api/routes_godot_projects.py` 创建启用 Hastur 的空白 Godot 项目。
- `app/api/routes_hastur.py` 管理 broker 状态、skill、executor 和聊天式 Hastur 交互。
- `app/api/routes_assets.py` 提供图像生成和资产审查动作。
- `app/api/routes_git.py` 提供项目本地 Git 审查、提交、历史和还原。
- `app/services/settings_service.py` 在本地保存私有设置，并从公开响应中隐藏密钥。
- `app/services/hastur_chat_service.py` 构造基于 skill 的 LLM prompt，加入上传上下文，并在允许时执行安全 Hastur 代码。
- `app/services/asset_service.py` 写入图像文件、manifest、GDD 引用和 Blender 参考说明。
- `app/services/git_service.py` 封装只作用于生成项目的 Git 命令。

## Provider 模型

仪表盘只接收 API key。provider 选择和模型默认值属于后端逻辑。OpenAI 是默认路径；Anthropic、DeepSeek 和 OpenAI-compatible 设置仍可通过已保存配置支持高级或本地部署。

正常运行路径不包含离线占位 provider。缺少 API key 或 provider 调用失败时，会返回用户可读的错误。

## Godot/Hastur 项目结构

生成项目包含：

- `project.godot`
- `scenes/Main.tscn`
- `addons/hasturoperationgd/`
- `docs/GODOT_PROJECT.md`
- 第三方声明与 Hastur 许可证文件

Hastur 编辑器插件会在 `project.godot` 中启用。本版本默认不添加 `GameExecutor` autoload。

## 本地状态

- `workspace/config/settings.json`：本地私有设置和密钥。
- `workspace/generated_godot_projects/`：生成的 Godot 项目。
- `workspace/cache/`：本地缓存。
- `runtime/`：启动脚本创建的本地 Python 运行时，不提交到仓库。
