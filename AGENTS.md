# AI Game Development Agent Context

## Required Workflow

- Before any repository modification, read this file first.
- After any repository modification, update this file when the project state, task list, architecture, or workflow rules change.
- Before any Godot-related modification, read the relevant local files under `godot-docs/` instead of relying on memory. Relevant sources include:
  - `godot-docs/tutorials/plugins/editor/installing_plugins.rst.txt`
  - `godot-docs/tutorials/plugins/editor/making_plugins.rst.txt`
  - `godot-docs/tutorials/best_practices/project_organization.rst.txt`
  - `godot-docs/getting_started/step_by_step/nodes_and_scenes.rst.txt`

## Project Goal

This repository is a local AI game development control plane for Godot prototypes. It creates playable Godot project skeletons, generates planning/reference assets, supports image review, and safely operates Godot through a local Hastur broker and vendored Hastur skills.

## Current Architecture

- `app/main.py` creates the FastAPI app and mounts the dashboard.
- `app/api/` exposes settings, project, Godot project, asset, Hastur, and Git routes.
- `app/services/settings_service.py` stores private local settings, hides secrets from public settings, and infers provider defaults from API keys/saved settings.
- `app/services/project_service.py` coordinates the older combined AI document/project workflow.
- `app/services/godot_project_service.py` creates blank Hastur-enabled Godot projects with local Git initialization.
- `app/tools/godot_templates/` writes Godot 2D/3D scenes, scripts, `project.godot`, and Hastur integration files.
- `app/services/asset_service.py` owns image generation, asset manifests, GDD image attachment, and Blender reference notes.
- `app/services/hastur_service.py` validates structured Godot operations and sends controlled GDScript snippets to Hastur.
- `app/services/broker_service.py` manages dashboard-started Hastur broker processes and reports readable status for external brokers already running on the configured local ports.
- `app/services/hastur_skill_service.py` discovers Claude Code-style skills from vendored, global, and project scopes; parses `SKILL.md` frontmatter; supports safe user uploads/deletes for global/project skills; and exposes lightweight skill metadata for low-token LLM injection.
- `app/services/hastur_chat_service.py` binds saved LLM settings, uploaded file/image context, lightweight skill metadata, and private broker token state for the legacy single-composer LLM + Hastur chat endpoint; it must not inject full skill bodies by default.
- `app/services/hastur_task_service.py` runs the streaming task loop: sanitized LLM-created `thought_delta` work notes plus `assistant_delta` response text, hidden planning, abstract LLM-instantiated modal prompts, auto/plan workflow modes, lightweight capability/skill/Godot-doc index injection with deduped on-demand context requests, image attachment observation summaries, structured task breakdown/progress events, optional sequential subtask execution, whole-batch LLM repair with compact Hastur error/output-contract feedback until success/cancel/unrecoverable or repeated-stall failure, task cancellation, and final answers from `executeContext.output(...)` execution outputs.
- `app/services/git_service.py` provides generated-project-scoped Git status with friendly change metadata, branch creation/switch/delete, save commits, merge-to-main, history graph, Godot VCS ignore metadata migration, selected-file compatibility APIs, revert, restore-file, and safe restore-to-commit helpers. Hard reset rollback is disabled.
- `app/agent/godot_operation_planner.py` validates LLM-created Godot operation plans.
- The dashboard is split into Management, LLM + Hastur Chat, and Image Pipeline views.
- The Management view owns API keys, blank Godot project creation, readable Hastur broker controls, Claude Code-style skills management, and a simple project-level Git workbench with branch/save/merge/delete/history/restore operations and collapsible changed-file groups.
- The LLM + Hastur view is a ChatGPT/OpenCode-style agent workspace with one chat input plus Send/Plan actions, `/` skill detection, file/image attachments, one abstract LLM-instantiated prompt modal for confirmation/choices/feedback with an always-visible custom reply box, final result bodies in chat, and an independent task sidebar for streamed public work notes, task breakdown/progress, failures, and read-only Git status.
- The Image Pipeline view owns image generation, reference uploads, generated asset gallery review, GDD attachment, and Blender reference markers.
- `hastur-operation-plugin-main/` is a vendored MIT-licensed third-party project.
- `godot-docs/` is the local source of truth for Godot implementation details.

## v0.5 Status

Implemented:

- Runtime user-facing placeholder providers have been removed from normal app flows.
- API settings UI only exposes LLM and image API key inputs; provider/model controls are backend-only.
- Provider failures from LLM, image, and Hastur chat endpoints are converted into readable client errors instead of generic `Internal Server Error`.
- Image asset generation through saved OpenAI/OpenAI-compatible settings.
- Per-project image cache and `asset_manifest.json`.
- GDD visual reference attachment.
- Blender reference notes.
- Structured Hastur operations and broker controls.
- Automatic Hastur addon installation and editor-plugin enablement for newly generated Godot projects.
- UI-managed broker start/stop/status/logs with external-broker detection and readable status cards.
- LLM-generated Godot operation plan endpoints with schema validation.
- Vendored Hastur skill discovery from `hastur-operation-plugin-main/.claude/skills/`.
- Chat-style LLM + Hastur endpoint with optional uploaded file/image context and private token/base URL binding.
- Codex-like Hastur task sessions with streamed sanitized LLM public work thoughts, hidden plans, abstract LLM-owned modals, one complete batch execution per approved plan/direct action, whole-batch repair, and verification events.
- LLM + Hastur task sessions stream public LLM work notes through `thought_delta` into the independent work log, task breakdown/progress into the independent task panel, and user-facing result/LLM-selected plan text through `assistant_delta` into chat; final responses prefer real Hastur execution outputs such as scene-tree text.
- Submitting an LLM modal response starts a new assistant continuation bubble immediately and the backend streams fresh public thought before code generation or Hastur execution resumes.
- LLM + Hastur task planning now requires structured complexity, execution strategy, and task breakdown metadata. The UI shows one task for simple work or multiple tasks for phased work, highlights the current task, and updates progress through `task_breakdown`/`task_progress` SSE events.
- Image attachments in the task flow are summarized once through image-capable LLM providers and then reused as compact visual context; unsupported providers receive an explicit note instead of pretending to inspect screenshots.
- LLM + Hastur task intake lets the LLM choose `direct`, `plan`, or `ask`; simple low-risk commands can execute directly without a fixed plan/confirmation prompt, and the abstract modal is shown only when the LLM instantiates it for user input, choices, approval, or feedback.
- LLM + Hastur task intake now supports `workflow_mode="auto"` and `workflow_mode="plan"`; the Plan button forces planning only, requires an LLM-instantiated modal for approval/revision, and does not generate GDScript or call Hastur before confirmation.
- Plan-mode task enforcement strips any LLM-returned direct code, keeps the session planning-only, and repairs missing confirmation modal content before any Hastur execution can occur.
- Task modals render the LLM-provided concrete choice list with no fixed option count; generic "I'll type/provide my own answer" choices are filtered because the always-visible custom box owns alternate instructions/revision requests. Clicking a choice does not require the custom reply box, ask-mode prompts replan after the selected answer instead of executing an empty question plan, and Plan-mode missing-modal repair retries once with explicit LLM-authored modal/choice requirements before surfacing failure.
- Skill definition and invocation must follow the Claude Code skills standard at https://code.claude.com/docs/en/skills: a skill is a directory containing `SKILL.md` with YAML frontmatter and markdown body, invoked directly with `/skill-name` or loaded automatically from its description/`when_to_use` rules unless `disable-model-invocation` prevents that.
- The task prompt injects only a capability registry, Claude Code skill metadata listing, Godot docs index, and runtime summary by default. Full skill bodies and Godot docs excerpts are loaded only through explicit `/skill` use or LLM `context_requests`; when a full skill body is loaded, the Work Log must explicitly say which Claude Code skill was invoked.
- Automatically matched Claude Code skills contribute only lightweight metadata until the user explicitly invokes `/skill` or the LLM requests the full skill body through `context_requests`.
- Hastur GDScript execution normalizes indentation, strips code fences, rewrites unsafe generated identifiers such as `class_name`, treats broker compile/run failures as failed executions, and keeps sending the full Hastur error context and failed batch summary back to the LLM for repair until the complete script succeeds, the user cancels, or broker/executor/provider state becomes unrecoverable.
- Hastur execution normalizes generated-project paths before broker requests, resolves matching executor IDs from `/api/executors` when possible, migrates missing generated-project `[hastur_operation]` settings, and reports Godot DAP `6006` as separate from Hastur TCP `5301` when executor matching fails.
- Hastur repair handling accepts executable code from top-level `code`, nested `steps[].code`, fenced snippets, or bare GDScript responses.
- Bare GDScript repair detection recognizes output calls such as `executeContext.output(...)`, common editor/project APIs, assignments, and function-call snippets.
- LLM + Hastur editor batches must return a non-empty `executeContext.output(...)` entry. Successful broker runs without displayable outputs are treated as failed task results and repaired; fixed broker success strings such as `Hastur skill code executed` must not be used as final chat answers.
- Direction, flip, upside-down, continent, map, terrain, and orientation fixes must return before/after evidence for the exact target node or resource. Successful broker runs without that evidence are treated as output-contract failures and repaired instead of being claimed complete.
- Front/back, transparent face, material, normal, cull, winding, mesh, and terrain surface fixes also require before/after evidence for the target mesh/material state.
- Generated-project Git status with friendly file change metadata, branch creation that preserves local changes, branch switch/delete, project-level save commits, merge-to-main, visual history graph, Godot cache ignore/migration, revert commit, restore file from commit compatibility APIs, and two-step safe restore-to-commit preview/confirmation rollback.
- Blank Hastur-enabled Godot project creation with a minimal `Main.tscn`, `docs/GODOT_PROJECT.md`, Godot `.gitignore`/`.gitattributes`, and automatic Git initialization.
- The older `/api/projects/create` workflow also writes `docs/GODOT_PROJECT.md` when it generates a Godot skeleton.
- Rewritten English and Chinese docs for quickstart, UI reference, architecture, API, and file reference.
- Local Git identity is auto-configured per generated repository so first commits do not fail on machines without global git config.
- Unix bootstrap now creates/uses the bundled micromamba runtime, installs requirements, chooses a free dashboard port, and opens the local dashboard like the documented quickstart flow.
- Hastur GDScript normalization now promotes LLM-returned top-level function wrappers such as `func _execute(executeContext):` or `_hastur_batch(...)` into plugin full-class mode before execution, and also rewrites full-class entrypoint aliases such as `func run(executeContext)` or `func _execute(executeContext)` to Hastur's required `func execute(executeContext)`, so simple tasks like printing/outputting `1` are not accidentally rejected by snippet/full-class mode.
- Multi-step Hastur task plans with multiple task-breakdown items are normalized to sequential subtask execution even if the LLM asks for `single_batch`, so each small task runs through Hastur and its output feeds the next script generation before the task panel advances.
- Lighting, camera, material, environment, and post-processing prompts now enforce clear-preview guardrails: avoid blur/fog/over-darkening/overexposure/high glow/auto exposure by default, use conservative Environment/CameraAttributes/Light3D ranges, and keep visual evidence outputs compact.
- Built-in default skills for common Godot failure modes must be real Claude Code skills, not ad-hoc prompt labels: `mesh-surface-orientation-fix` and `visual-clarity-fix` live under `.claude/skills/<skill-name>/SKILL.md`, follow the standard frontmatter/body lifecycle, can be invoked with `/skill-name`, can be auto-loaded from `description`/`when_to_use`, and must be announced in the Work Log when their full body is loaded.
- Mesh/material surface-orientation tasks now have a hard output-contract gate, not only prompt guidance: a successful Hastur run must prove the intended scene-relative target path, instance visibility/transparency, material/cull/alpha state, normal or winding state, and explicit top/front visibility such as `top_visible=true`; incidental fixes to tree/decor child meshes, editor-internal paths such as `@EditorNode`, truncated output, vague `fix=saved` summaries, or Before evidence that already claims the target is visible are treated as failed results and sent back through repair.

Current Codex task:

- The local Git workbench has been simplified to project-level actions with collapsible changed-file groups and two-step restore confirmation; Godot cache files are ignored/migrated automatically, LLM + Hastur uses chat for user-facing messages and a separate task sidebar for work logs/progress/failures, the LLM decides direct execution versus visible plans/prompts in auto mode, the Plan button forces LLM-authored plan approval with direct-code stripping, abstract LLM-instantiated modals are the only task confirmation UI, and approved plans execute as whole batches or LLM-selected sequential subtasks with repair.
- Keep the UI free of advanced provider/model controls; provider detection should remain automatic from keys/saved settings.
- Preserve the safety rule that the UI never exposes arbitrary GDScript input.
- Keep broker defaults local-only: host `localhost`, TCP `5301`, HTTP `5302`.
- Use local Godot docs before Godot-related changes.

## Hastur Integration Notes

Hastur Operation Plugin is vendored from `hastur-operation-plugin-main/` under the MIT License. Generated Godot projects must include:

- `addons/hasturoperationgd/`
- `project.godot` with `[editor_plugins] enabled=PackedStringArray("res://addons/hasturoperationgd/plugin.cfg")`
- `[hastur_operation] broker_host="localhost"` and `broker_port=5301` unless the UI provides different local settings
- `THIRD_PARTY_NOTICES.md`
- `licenses/HASTUR_OPERATION_PLUGIN_LICENSE.md`

Do not add the Hastur `GameExecutor` autoload by default; editor-side automation is enough for this version.
