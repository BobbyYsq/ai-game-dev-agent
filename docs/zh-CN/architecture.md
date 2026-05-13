# 架构说明

本应用是本地 FastAPI 控制台，用于反复开发 Godot 原型项目。

## 应用层

- `app/main.py` 创建 FastAPI 应用并挂载 dashboard。
- `app/api/` 暴露设置、项目、Godot 项目、图像资产、Hastur 和 Git 路由。
- `app/templates/index.html`、`app/static/js/app.js`、`app/static/css/app.css` 组成本地 UI。

## 服务层

- `settings_service.py` 保存私有设置，隐藏密钥，并自动推断 provider/model 默认值。
- `godot_project_service.py` 创建启用 Hastur 的空白 Godot 项目，并初始化本地 Git。
- `asset_service.py` 生成图像资产、维护 manifest、写入 GDD 和 Blender 参考说明。
- `broker_service.py` 管理本地 Hastur broker 进程。
- `hastur_skill_service.py` 读取 vendored Hastur skills。
- `hastur_task_service.py` 实现 Codex-like 任务会话：把公开工作流思考通过 `thought_delta` 流式显示在 assistant 气泡上方，把计划/结果正文通过 `assistant_delta` 显示在正文中，读取 Godot docs 和 skill，生成隐藏计划，所有确认/选择/视觉检查/修改意见都走统一弹窗；确认后为整个计划或调整生成一个完整 Hastur editor batch；失败时把完整 Hastur 错误、broker payload 和失败代码摘要反馈给 LLM 持续做整批修复，直到成功、用户取消或 broker/executor/provider 不可恢复；最终回答优先使用真实执行输出。
- `hastur_chat_service.py` 保留兼容的一次性 LLM + Hastur 调用。
- `git_service.py` 封装项目范围内的安全 Git 操作：Godot VCS metadata、友好的改动状态字段、保留本地改动的新建分支、受保护的切换/合并/保存/回档流程。Hard reset rollback 已禁用。

## Godot/Hastur 约束

生成项目必须包含：

- `addons/hasturoperationgd/`
- `project.godot` 中启用 Hastur editor plugin
- `[hastur_operation] broker_host="localhost"` 和 `broker_port=5301`
- `THIRD_PARTY_NOTICES.md`
- `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`

任何 Godot 操作前，任务服务都要读取本地 `godot-docs/` 的相关文档和 vendored skill。3D 相关任务会向 LLM 注入 Godot 坐标约束：右手系、Y 向上、相机 -Z forward、+X right、+Z back，模型正面按 +Z 处理。
