# Quickstart

## 1. Start the app

Windows:

```text
start_windows.cmd
```

macOS:

```bash
chmod +x start_macos.command
./start_macos.command
```

Linux:

```bash
chmod +x start_unix.sh
./start_unix.sh
```

The bootstrap script creates the local `runtime/` environment, installs dependencies, chooses a free FastAPI port, and opens the dashboard.

## 2. Configure API keys

1. Open **Manage**.
2. Paste an LLM API key into **LLM API Key**.
3. Paste an image-capable API key into **Image API Key**. For OpenAI, this can be the same key if the account has image access.
4. Click **Save Settings**.
5. Click **Test LLM**. If the key or account is not ready, the dashboard shows the provider error directly.

The UI does not expose provider/model pickers. The backend infers the provider from the key and saved settings. OpenAI image generation uses the backend default model and the Image API pattern documented by OpenAI.

## 3. Create and open a Godot project

1. In **Blank Godot Project**, enter a project name.
2. Click **Create Project**.
3. Open the generated folder from `workspace/generated_godot_projects/<project-slug>/` in Godot 4.
4. Confirm `addons/hasturoperationgd/` exists and the plugin is enabled in `project.godot`.
5. Open `res://scenes/Main.tscn`.

Godot editor plugins live under `addons/` and are enabled through `Project > Project Settings > Plugins`. The generated project follows that local Godot docs convention and stores the main scene in `project.godot`.

## 4. Start Hastur and chat with Godot

1. In **Hastur Broker**, click **Start Broker**.
2. Open or reload the generated project in Godot so the executor connects.
3. Click **Executors** to confirm a Godot executor is available.
4. Open **LLM + Hastur**.
5. Select the project.
6. Optional: in **Manage > Skills**, upload a global skill or select a project and upload a project-specific skill. Vendored Hastur skills remain read-only.
7. Type `/` in the composer and choose an available skill.
8. Attach reference files or images with the `+` button if needed.
9. Use **Send** for automatic direct/plan/ask decisions, or **Plan** to force planning first. The Plan flow requires the LLM to create the confirmation modal before any script generation or Hastur execution.
10. The chat streams LLM public thinking and assistant text in one bubble. Approved plans and direct actions run as one complete Hastur batch; failures are repaired as whole batches until success, cancellation, or an unrecoverable broker/provider problem.

The UI never asks for raw GDScript. The LLM receives a lightweight capability registry, skill metadata, and a Godot docs index by default; full skill bodies or docs snippets are loaded only when explicitly selected or requested by the LLM. Broker URL/token state is bound privately.

## 5. Generate and review images

1. Open **Image Pipeline**.
2. Select the project and purpose.
3. Choose size and quality.
4. Add an image prompt and optional reference files/images.
5. Click **Generate Image**.
6. Review the gallery.
7. Use **Approve to GDD** to append the image to `docs/GDD.md`.
8. Use **Mark Blender Reference** to add the asset to `docs/BLENDER_REFERENCE_NOTES.md`.

## 6. Use local Git

1. Open **Project Workbench** in **Manage**.
2. Select a project.
3. Click **Review changes** to inspect status, changed files, and diff.
4. Click **Commit**, enter a message, and commit all project changes.
5. Click **History** to inspect recent commits.
6. Click **Restore here** on a history entry, review the target summary, then click **Confirm restore** to create a safe restore commit.

This is local-only Git management. Remote push and pull request workflows are intentionally out of scope for this version.
