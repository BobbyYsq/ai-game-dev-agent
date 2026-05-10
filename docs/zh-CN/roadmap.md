# 路线图

## v0.3 图像生成管线

- 增加 image-2 provider。
- 将概念图生成到 `assets/generated/cache/images/`。
- 允许生成图像链接到 `docs/GDD.md`。
- 将图片提升为 2D sprite、icon、UI 或 texture 参考。
- 将选定图片作为 Blender 或 3D 资产生成参考。

## v0.4 Claude Blender 3D 管线

- 根据项目目标生成 Blender Python 脚本。
- 在可用时以 headless 方式运行 Blender。
- 导出 `.glb` 或 `.fbx` 到 `assets/models/`。
- 为生成的 3D 资产补充评审说明。

## v0.5 Hastur / Godot Editor Bridge

- 在 `hastur_bridge.py` 中加入真实桥接层。
- 向 Godot 编辑器插件发送结构化操作。
- 创建场景、节点、信号、导入资产和编辑器侧检查。
- 读取操作结果并写入评审报告。

## v0.6 Playtest / Fix / Commit 循环

- 收集用户试玩反馈。
- 分析已生成项目文件。
- 生成修复计划。
- 修改脚本、场景和文档。
- 生成新的评审报告。
- 使用生成的 Git message 提交修改。
