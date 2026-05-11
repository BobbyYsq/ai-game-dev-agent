# 快速开始

## Windows

双击：

```text
start_windows.cmd
```

该入口会调用 `bootstrap/bootstrap_windows.ps1`。第一次启动时，它会下载 portable Micromamba，只使用 `conda-forge` 创建 `runtime/envs/ai-game-dev-agent`，从 `requirements.txt` 安装 Python 包，从 8000-8003 中选择可用端口，打开浏览器，并启动 FastAPI。

## macOS

运行：

```bash
chmod +x start_macos.command
./start_macos.command
```

该入口会调用 `bootstrap/bootstrap_macos.sh`，自动识别 `arm64` 或 `x86_64`，下载对应的 Micromamba，只使用 `conda-forge` 创建本地运行环境，从 `requirements.txt` 安装 Python 包，打开浏览器，并启动 FastAPI。

## 创建第一个项目

1. 离线测试时保留 `mock` provider。
2. 输入项目名称和游戏想法。
3. 选择 `2D Game Prototype` 或 `3D Game Prototype`。
4. 点击 `Create AI Game Project`。
5. 在 Godot 4 中打开 `workspace/generated_godot_projects/` 下生成的项目。
6. 运行 `scenes/Main.tscn`。

## 本地运行环境

`runtime/` 是自动生成的本地目录，不应该提交到 Git。如果依赖环境损坏，可以关闭应用并删除 `runtime/`，下一次启动会重新创建。

启动脚本不会使用 Anaconda `defaults` channel，因此正常启动时不应该再看到 Anaconda Terms warning。
## 生成图像资产

1. 先创建或选择一个已有生成项目。
2. 打开 Assets 面板。
3. 离线测试使用 `mock`，真实生成选择 `openai` 并配置 API Key。
4. 选择用途，例如 `concept_art` 或 `blender_3d_reference`。
5. 生成图片后，可以加入 GDD 或标记为 Blender 参考。

## Hastur 桥接

1. 在本机启动 Hastur broker。
2. 在目标 Godot 项目中启用插件。
3. 在 Hastur 面板保存 broker 地址。
4. 检查状态并加载执行器。
5. UI 只执行结构化 operation，不直接执行任意 GDScript。
# v0.3 Addendum

Use the Hastur panel to start the local broker. Projects created from the Godot Project panel include and enable the Hastur addon automatically. Open the generated project in Godot, load executors, then use AI Godot Operation to generate and execute validated operation plans.
