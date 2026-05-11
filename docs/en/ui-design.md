# UI Design

The dashboard is an operational tool, not a marketing page. It is designed around the repeated workflow of configuring a model, creating a prototype, inspecting generated files, and reopening recent projects.

## Settings Panel

Fields:

- LLM Provider: `mock` or `openai`.
- OpenAI Model: model name used by the OpenAI provider.
- OpenAI API Key: password field. Saved locally and cleared after save.

The panel shows whether an API key is configured without exposing the key.

## Create Project Panel

Fields:

- Project Name
- Game Idea
- Godot Project Template: `2D Game Prototype` or `3D Game Prototype`
- Game Type
- Engine Version
- Prototype Scope
- Enable Git
- Generate Documentation
- Generate Godot Prototype

The create button sends one structured request to `POST /api/projects/create`.

## Recent Projects Panel

The panel loads `GET /api/projects` on page load. The details button calls `GET /api/projects/{slug}` and displays the file list.

## Output Panel

The output panel renders project slug, template, path, review summary, next steps, generated files, and request errors.
## v0.3 Panels

- Settings: choose `mock` or `openai`, select the text model, and save the API key locally.
- Create Project: submit the project name, GDD/idea, Godot template, game type, engine version, and prototype scope. Startup does not create a project automatically.
- Recent Projects: browse generated projects and inspect file lists without overflowing the panel.
- Assets: select an existing project, choose an image purpose, enter a prompt, generate an image, attach it to the GDD, or mark it as a Blender reference.
- Hastur Bridge: save broker settings, check status, list executors, and apply a safe test operation.
- Godot Project: create a standalone Godot project with Hastur copied and enabled automatically.
- Broker controls: start/stop the local broker, inspect status, and read recent logs.
- AI Godot Operation: enter a natural-language instruction, generate a validated operation plan, and execute it through Hastur.

The language toggle switches all dashboard labels between English and Chinese without changing stored project data.
