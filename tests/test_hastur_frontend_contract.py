from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "app" / "static" / "js" / "app.js"
INDEX_HTML = Path(__file__).resolve().parents[1] / "app" / "templates" / "index.html"


def test_task_modal_always_renders_custom_reply_textarea():
    source = APP_JS.read_text(encoding="utf-8")
    modal_start = source.index("function userPromptHTML")
    modal_end = source.index("function resumePromptChoice", modal_start)
    modal_source = source[modal_start:modal_end]

    assert 'textarea id="task_prompt_answer"' in modal_source
    assert 'inputRequired ? "required" : ""' in modal_source
    assert "detail.requires_input" in modal_source
    assert "hasInput" not in modal_source
    assert "custom-reply-box" in modal_source


def test_task_modal_choice_bypasses_required_custom_reply_validation():
    source = APP_JS.read_text(encoding="utf-8")
    assert "function promptAnswerValue(validateRequired = true)" in source
    assert "input.hasAttribute(\"required\")" in source
    assert "const answer = promptAnswerValue(false);" in source
    assert "function bindTaskModalChoices" in source
    assert "data-task-choice-id" in source


def test_task_modal_uses_generic_custom_label_when_choices_exist():
    source = APP_JS.read_text(encoding="utf-8")
    modal_start = source.index("function userPromptHTML")
    modal_end = source.index("function bindTaskModalChoices", modal_start)
    modal_source = source[modal_start:modal_end]

    assert "fallbackInputLabel" in modal_source
    assert "choices.length ? fallbackInputLabel" in modal_source


def test_resume_creates_new_assistant_continuation_bubble():
    source = APP_JS.read_text(encoding="utf-8")
    resume_start = source.index("async function resumeActiveTask")
    resume_end = source.index("async function cancelActiveTask", resume_start)
    resume_source = source[resume_start:resume_end]

    assert "startAssistantContinuation();" in resume_source
    assert "function startAssistantContinuation()" in source


def test_task_stream_ignores_malformed_empty_events():
    source = APP_JS.read_text(encoding="utf-8")
    assert "function parseTaskEvent(event, fallbackType)" in source
    assert 'event.data === "undefined"' in source
    assert "Ignored malformed task event" in source


def test_task_prompt_event_closes_stream_before_waiting():
    source = APP_JS.read_text(encoding="utf-8")
    handler_start = source.index("function handleTaskEvent")
    handler_end = source.index("function renderTaskQuestion", handler_start)
    handler_source = source[handler_start:handler_end]

    assert 'type === "user_prompt"' in handler_source
    assert "state.activeEventSource.close();" in handler_source
    assert "renderTaskModal(event);" in handler_source


def test_task_breakdown_events_render_in_independent_task_panel():
    source = APP_JS.read_text(encoding="utf-8")
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert 'id="task_overview"' in html
    assert 'id="task_list"' in html
    assert 'id="task_work_log"' in html
    assert '"task_breakdown"' in source
    assert '"task_progress"' in source
    assert "function renderTaskPanel" in source
    assert "renderTaskPanel(event.detail || {}, event)" in source
    assert "function renderAssistantTasks" not in source
    assert "assistant-tasks" not in source
    assert "state.lastTaskProgress" not in source


def test_thought_delta_streams_to_work_log_not_chat_bubble():
    source = APP_JS.read_text(encoding="utf-8")
    handler_start = source.index("function handleTaskEvent")
    handler_end = source.index("function renderTaskQuestion", handler_start)
    handler_source = source[handler_start:handler_end]

    assert 'type === "thought_delta"' in handler_source
    assert "appendWorkLog(" in handler_source
    assert "appendAssistantThought(" not in handler_source
    assert "function appendWorkLog" in source
    assert 'id="task_work_log"' in INDEX_HTML.read_text(encoding="utf-8")


def test_work_log_coalesces_streamed_delta_chunks():
    source = APP_JS.read_text(encoding="utf-8")
    append_start = source.index("function appendWorkLog")
    append_end = source.index("function renderWorkLog", append_start)
    append_source = source[append_start:append_end]
    safe_start = source.index("function safeWorkLogText")
    safe_end = source.index("function safeChatText", safe_start)
    safe_source = source[safe_start:safe_end]

    assert "last.kind === kind && last.phase === phase" in append_source
    assert "last.text += text" in append_source
    assert "text.trimStart()" in append_source
    assert ".trim()" not in safe_source


def test_assistant_message_has_no_embedded_task_or_thinking_panels():
    source = APP_JS.read_text(encoding="utf-8")
    create_start = source.index("function createAssistantMessage")
    create_end = source.index("function ensureAssistantMessage", create_start)
    create_source = source[create_start:create_end]

    assert "assistant-text" in create_source
    assert "assistant-actions" in create_source
    assert "assistant-thinking" not in create_source
    assert "assistant-tasks" not in create_source


def test_chat_errors_are_sanitized_before_rendering():
    source = APP_JS.read_text(encoding="utf-8")
    assert "function safeChatText" in source
    assert "executeContext" in source
    assert "task_failed_brief" in source
    assert "appendAssistantError(safeChatText(" in source


def test_git_workbench_has_no_selected_file_controls():
    source = APP_JS.read_text(encoding="utf-8")

    assert "git-path-checkbox" not in source
    assert "selectedGitPaths" not in source
    assert "discardSelectedChanges" not in source
    assert "Commit selected" not in source
    assert "Discard selected" not in source
    assert "Restore file" not in source
    assert "选中文件" not in source


def test_history_restore_requires_confirmation_step():
    source = APP_JS.read_text(encoding="utf-8")
    graph_sections = []
    start = 0
    while True:
        index = source.find("function gitGraphHTML", start)
        if index == -1:
            break
        next_function = source.find("\nfunction ", index + 1)
        graph_sections.append(source[index: next_function if next_function != -1 else len(source)])
        start = index + 1

    assert "function showRestoreConfirmation" in source
    assert graph_sections
    assert all("showRestoreConfirmation(" in section for section in graph_sections)
    assert all("rollbackToCommit(" not in section for section in graph_sections)
