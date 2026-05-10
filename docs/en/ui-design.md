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
