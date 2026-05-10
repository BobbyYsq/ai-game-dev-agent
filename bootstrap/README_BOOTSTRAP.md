# Bootstrap Runtime

The startup scripts are designed so a user does not need to install Python, Conda, Miniconda, or Docker before launching the MVP.

## Entrypoints

- Windows: `start_windows.cmd`
- macOS: `start_macos.command`

Both scripts delegate to files in this directory.

## First Launch

The bootstrap scripts:

1. Locate the project root.
2. Create `runtime/`.
3. Download portable Micromamba for the current OS.
4. Create `runtime/envs/ai-game-dev-agent` with `conda-forge` only.
5. Install Python packages from `requirements.txt`.
6. Choose a free port from 8000-8003.
7. Start `uvicorn app.main:app`.
8. Open the browser at `http://127.0.0.1:<port>`.

## Later Launches

If `runtime/micromamba/` and `runtime/envs/ai-game-dev-agent/` already exist, startup reuses them and skips dependency installation.

If the environment directory exists but does not contain Python, startup treats it as an interrupted or incomplete install, removes that environment directory, and recreates it.

## Resetting the Runtime

Close the app, delete `runtime/`, and launch again. The scripts recreate everything.

The scripts do not use Anaconda `defaults`; this avoids the Anaconda Terms warning and reduces channel solver work.

## Git Safety

`runtime/` is ignored by Git. API keys are stored in `workspace/config/settings.json`, which is also ignored.
