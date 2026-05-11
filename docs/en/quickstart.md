# Quickstart

## Windows

Double-click:

```text
start_windows.cmd
```

The script calls `bootstrap/bootstrap_windows.ps1`. On first launch it downloads portable Micromamba, creates `runtime/envs/ai-game-dev-agent` with `conda-forge` only, installs Python packages from `requirements.txt`, chooses a free port from 8000-8003, opens the browser, and starts FastAPI.

## macOS

Run:

```bash
chmod +x start_macos.command
./start_macos.command
```

The script calls `bootstrap/bootstrap_macos.sh`, detects `arm64` or `x86_64`, downloads the matching Micromamba build, creates the local runtime environment with `conda-forge` only, installs Python packages from `requirements.txt`, opens the browser, and starts FastAPI.

## First Project

1. Keep provider set to `mock` for a no-key test.
2. Enter a project name and game idea.
3. Choose `2D Game Prototype` or `3D Game Prototype`.
4. Click `Create AI Game Project`.
5. Open the generated folder from `workspace/generated_godot_projects/` in Godot 4.
6. Run `scenes/Main.tscn`.

## Local Runtime

The `runtime/` directory is generated locally and should not be committed. If dependency setup becomes corrupted, close the app and delete `runtime/`; the next launch recreates it.

The bootstrap scripts intentionally avoid Anaconda `defaults`, so users should not see the Anaconda Terms warning during normal startup.
## Generate Image Assets

1. Create or select a generated project.
2. Open the Assets panel.
3. Use `mock` for an offline placeholder image or `openai` with an API key for real generation.
4. Choose a purpose such as `concept_art` or `blender_3d_reference`.
5. Generate the image, then attach it to the GDD or mark it as a Blender reference.

## Hastur Bridge

1. Start the Hastur broker locally.
2. Enable the Godot plugin in the target project.
3. Save the broker URL in the Hastur panel.
4. Check status and load executors.
5. Apply only structured operations from the UI.
# v0.3 Addendum

Use the Hastur panel to start the local broker. Projects created from the Godot Project panel include and enable the Hastur addon automatically. Open the generated project in Godot, load executors, then use AI Godot Operation to generate and execute validated operation plans.
