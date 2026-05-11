# UI Reference

The dashboard is an operational tool for repeated Godot prototype work. It is split into **Manage**, **LLM + Hastur**, and **Image Pipeline**.

## Manage

### API Settings

- **LLM API Key**: password input for text model access. Saved locally in `workspace/config/settings.json`; never returned by public settings APIs.
- **Image API Key**: password input for image generation access. Can be the same OpenAI key if the account has image permissions.
- **Save Settings**: stores non-empty key inputs and image defaults. The fields are cleared after saving.
- **Test LLM**: sends a small provider request and displays the real error if the key, account, or network is not ready.
- **API key status**: shows whether either key slot is configured.

There is no provider/model picker in the UI. Provider selection is automatic.

### Blank Godot Project

- **Project Name**: human-readable project name. The backend slugifies it for the generated folder.
- **Create Project**: creates a minimal Godot project, installs the Hastur editor plugin under `addons/`, enables it in `project.godot`, creates `res://scenes/Main.tscn`, and initializes local Git.
- **Inline result**: appears directly under the create form and lists the generated path and files.

### Project Workbench

- **Refresh**: reloads generated project folders.
- **Project list**: selects one generated project. The output pane is attached to the selected project instead of floating below unrelated rows.
- **Details**: shows the generated path and file list.
- **Review changes**: shows branch, dirty/clean state, changed files, diff stat, and diff preview.
- **Commit**: opens a commit message input and commits all local project changes.
- **History**: lists recent commits.
- **Restore**: accepts a commit hash, previews rollback impact, then enables explicit confirmation.

### Hastur Broker

- **Start Broker**: starts the vendored broker on local defaults unless saved settings specify otherwise.
- **Stop Broker**: stops the managed broker process.
- **Status**: shows running state, PID, ports, base URL, and token presence without revealing the token.
- **Logs**: shows recent broker logs.
- **Executors**: queries connected Godot executors.

## LLM + Hastur

- **Project selector**: selects the target generated Godot project.
- **Readiness pill**: reports broker/executor readiness where known.
- **Message history**: displays user and assistant messages; technical JSON stays inside collapsible details.
- **Composer**: the only instruction input. Type `/` to open the vendored skill picker.
- **Attachment button (`+`)**: uploads files and images for the request. Images are passed to providers that support image input; text files are summarized into the prompt.
- **Send**: sends the message through the configured LLM and executes safe Hastur actions by default.
- **Confirm and execute**: appears only when the LLM marks an operation as requiring confirmation.

The UI does not expose arbitrary GDScript entry. Hastur code is produced by the LLM under vendored skill instructions and sent through backend validation/safety checks.

## Image Pipeline

- **Project**: target project for generated assets and manifest updates.
- **Purpose**: records intended use in `asset_manifest.json`.
- **Size**: image dimensions sent to the backend.
- **Quality**: image quality sent to the backend.
- **Image Prompt**: generation prompt.
- **Reference Files and Images**: optional context. Text-like files are summarized into the prompt; uploaded file names are visible to the user.
- **Save Image Defaults**: stores size and quality.
- **Generate Image**: calls the image provider using the saved image API key and backend model default.
- **Gallery**: shows generated images, prompt, model, path, and review actions.
- **Approve to GDD**: appends the image to `docs/GDD.md`.
- **Mark Blender Reference**: adds the image to `docs/BLENDER_REFERENCE_NOTES.md`.
- **Regenerate**: reuses the asset prompt for another generation.

## Failure Messages

Provider, image, and Hastur errors should be displayed as direct user-facing messages. Generic `Internal Server Error` is considered a UI bug unless the server process itself is unreachable.
