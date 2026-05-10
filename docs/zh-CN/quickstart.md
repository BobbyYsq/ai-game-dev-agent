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
