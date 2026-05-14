# UI Reference

The dashboard is an operational tool for repeated Godot prototype work. It is split into **Manage**, **LLM + Hastur**, and **Image Pipeline**.

## Manage

### API Settings

- **LLM API Key**: password input for text model access. Saved locally in `workspace/config/settings.json`; never returned by public settings APIs.
- **Image API Key**: password input for image generation access. Can be the same OpenAI key if the account has image permissions.
- **Save Settings**: stores non-empty key inputs and image defaults. The fields are cleared after saving.
- **Test LLM**: sends a small provider request and displays the real error if the key, account, or network is not ready.
- **Test Image Config**: validates local image settings without spending image generation credits.
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
- **Review changes**: opens the Git workbench with branch state, project-level save/merge controls, friendly changed-file status labels, and collapsible directory groups.
- **New branch**: creates and switches to a branch from the current save point while preserving uncommitted local changes in the working tree.
- **Save**: commits all project changes with the entered message, or a timestamped default.
- **History**: lists recent commits with safe restore-to-commit actions. Full hard rollback is disabled.

### Hastur Broker

- **Start Broker**: starts the vendored broker on local defaults unless saved settings specify otherwise.
- **Stop Broker**: stops the managed broker process.
- **Status**: shows running state, PID, ports, base URL, and token presence without revealing the token.
- **Logs**: shows recent broker logs.
- **Executors**: queries connected Godot executors.

### Skills

- **Scope**: uploads skills globally to `workspace/skills/` by default, or into the selected project's `.claude/skills/` folder for project-specific behavior.
- **Skill files**: accepts a skill zip or `SKILL.md` plus supporting files. Vendored Hastur skills are listed as read-only and cannot be deleted from the UI.
- **Upload Skill**: validates the package, requires exactly one `SKILL.md`, and exposes only lightweight metadata to the LLM until the model requests the full body.
- **Skill list**: shows vendored, global, and selected-project skills, their scope, read-only state, description, trigger guidance, and path label.

## LLM + Hastur

- **Project selector**: selects the target generated Godot project.
- **Readiness pill**: reports broker/executor readiness where known.
- **Message history**: displays LLM-authored public `thought_delta` work notes, structured task progress, and streamed `assistant_delta` body text in the same assistant bubble. There is no activity-summary panel.
- **Composer**: the only instruction input. Type `/` to open the vendored skill picker.
- **Attachment button (`+`)**: uploads files and images for the request. Images are summarized once by providers that support image input and reused as compact visual context; text files are summarized into the prompt.
- **Plan**: creates a planning-only task. The LLM must design the plan, instantiate the abstract modal with its own confirmation/revision copy, and wait for approval before any GDScript generation or Hastur execution.
- **Send**: creates an automatic Hastur task session. The LLM decides whether to execute directly, show a plan, or instantiate a modal for missing user intent.
- **Stop**: cancels the active task. This is the user escape hatch for long repair loops.
- **Task modal**: the only modal is the abstract prompt UI. It renders only LLM-provided `title`, `body`, `choices`, `input_label`, and `requires_input`; the agent does not generate user-visible modal copy.
- **Task progress**: after planning, the assistant bubble shows the LLM's task breakdown. Simple tasks show one item; phased tasks show multiple items with the active task highlighted.
- **Local Git panel**: is read-only in chat. It shows branch/dirty count and opens the manual Git workbench; branch/save/merge controls live in the workbench.

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
