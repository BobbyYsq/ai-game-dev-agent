# File Reference

## App Entrypoints

- `app/main.py`: FastAPI app creation, static files, templates, and route registration.
- `app/templates/index.html`: dashboard structure for Manage, LLM + Hastur, and Image Pipeline.
- `app/static/js/app.js`: dashboard state, API calls, skill picker, chat, image gallery, and Git workbench.
- `app/static/css/app.css`: responsive operational UI styling.

## API Routes

- `app/api/routes_settings.py`: public settings, save settings, test LLM.
- `app/api/routes_godot_projects.py`: blank Godot project creation.
- `app/api/routes_projects.py`: generated project listing and details.
- `app/api/routes_hastur.py`: broker controls, skills, executors, chat, and structured operations.
- `app/api/routes_assets.py`: image generation, asset files, GDD attach, Blender reference.
- `app/api/routes_git.py`: project-local Git status, changed files, diff, log, selected-file commit/discard, revert, restore-file, and deprecated rollback.

## Services

- `app/services/settings_service.py`: local private settings, provider inference, public settings.
- `app/services/godot_project_service.py`: blank Hastur-enabled Godot project creation.
- `app/services/hastur_chat_service.py`: LLM + Hastur chat prompt, attachments, confirmation, execution.
- `app/services/hastur_skill_service.py`: vendored Hastur skill discovery.
- `app/services/hastur_service.py`: safe structured operation validation and broker execution.
- `app/services/broker_service.py`: managed local Hastur broker process.
- `app/services/asset_service.py`: generated images, manifests, GDD links, Blender notes.
- `app/services/git_service.py`: generated-project safe Git helper commands; hard reset rollback is disabled.

## Provider Adapters

- `app/models/openai_provider.py`: OpenAI-compatible chat, vision, and Anthropic adapter.
- `app/models/llm_provider.py`: selects the active text provider from saved settings.
- `app/models/image_provider.py`: selects the active image provider from saved settings.

## Godot Generation

- `app/tools/godot_templates/base.py`: minimal `project.godot`, `Main.tscn`, folders, and Hastur addon installation.
- `app/tools/godot_templates/template_2d.py`: 2D prototype template.
- `app/tools/godot_templates/template_3d.py`: 3D prototype template.

## Tests

- `tests/test_settings.py`: provider inference and public settings.
- `tests/test_assets.py`: generated asset manifest and document links.
- `tests/test_hastur.py`: structured operation validation and GDScript construction.
- `tests/test_hastur_skills.py`: skill discovery and token hiding in chat.
- `tests/test_git_service.py`: local Git status, selected-file commit/discard, revert, restore-file, and disabled rollback.
