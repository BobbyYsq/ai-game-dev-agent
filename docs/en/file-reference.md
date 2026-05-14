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
- `app/api/routes_hastur.py`: broker controls, skills, executors, chat, task streaming/resume/cancel, and structured operations.
- `app/api/routes_skills.py`: global/project skill listing, upload, metadata, and deletion APIs.
- `app/api/routes_assets.py`: image generation, asset files, GDD attach, Blender reference.
- `app/api/routes_git.py`: project-local Git status, branch/save/merge actions, changed files, diff, log, selected-file compatibility APIs, revert, restore-file, and safe rollback.

## Services

- `app/services/settings_service.py`: local private settings, provider inference, public settings.
- `app/services/godot_project_service.py`: blank Hastur-enabled Godot project creation.
- `app/services/hastur_chat_service.py`: LLM + Hastur chat prompt, attachments, confirmation, execution.
- `app/services/hastur_task_service.py`: streaming LLM + Hastur task loop, LLM thought deltas, task breakdown/progress events, assistant body deltas, abstract LLM-owned prompts, lightweight capability/skill/docs injection, image attachment observation summaries, context requests, whole-batch or sequential-subtask generation and repair, cancellation, and final output extraction.
- `app/services/hastur_skill_service.py`: Claude Code-style vendored/global/project skill discovery, frontmatter parsing, safe uploads/deletes, and lightweight prompt listings.
- `app/services/hastur_service.py`: safe structured operation validation and broker execution.
- `app/services/broker_service.py`: managed local Hastur broker process.
- `app/services/asset_service.py`: generated images, manifests, GDD links, Blender notes.
- `app/services/git_service.py`: generated-project safe Git helper commands, Godot VCS metadata, friendly change status fields, and local-change-preserving branch creation; hard reset rollback is disabled.

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
- `tests/test_hastur_task_service.py`: streaming task events, task breakdown/progress, image observations, LLM-owned modals, plan mode, low-token context requests, whole-batch repair loop, and final output extraction.
- `tests/test_hastur_skill_service.py`: scoped skill registry, frontmatter parsing, upload/delete safety, and read-only vendored behavior.
- `tests/test_hastur_skills.py`: legacy skill discovery and token hiding in chat.
- `tests/test_git_service.py`: local Git status, friendly change metadata, branch/save/merge/delete flows, selected-file compatibility APIs, revert, restore-file, safe restore commits, and disabled hard rollback.
