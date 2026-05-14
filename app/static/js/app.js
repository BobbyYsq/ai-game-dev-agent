const translations = {
  en: {
    eyebrow: "Godot control plane",
    app_title: "AI Game Development Agent",
    header_note: "Create Hastur-enabled Godot projects, use skill-grounded chat operations, generate references, and review local Git changes.",
    loading: "Loading",
    ready: "Ready",
    settings_error: "Settings error",
    tab_manage: "Manage",
    tab_hastur: "LLM + Hastur",
    tab_images: "Image Pipeline",
    settings_title: "API Settings",
    settings_note: "Paste API keys here. Providers and default models are selected automatically.",
    checking_key: "Checking key",
    key_configured: "API key configured",
    key_missing: "API key missing",
    llm_key: "LLM API Key",
    image_key: "Image API Key",
    save_settings: "Save Settings",
    test_connection: "Test LLM",
    test_image_config: "Test Image Config",
    saving_settings: "Saving settings...",
    settings_saved: "Settings saved.",
    testing_connection: "Testing connection...",
    checking_image_config: "Checking image configuration...",
    connection_ok: "Connection test succeeded.",
    image_config_ok: "Image configuration is ready.",
    godot_project_title: "Blank Godot Project",
    godot_project_badge: "Hastur enabled",
    godot_project_note: "Create a minimal Godot project with the Hastur editor plugin enabled and local Git initialized.",
    project_name: "Project Name",
    project_name_placeholder: "Example: Shadow Garden",
    create_godot_project: "Create Project",
    project_required: "Enter a project name.",
    creating_project: "Creating project...",
    godot_project_created: "Project created.",
    project_workbench: "Project Workbench",
    refresh: "Refresh",
    workbench_note: "Select a generated project and use the simple local Git workbench.",
    select_project_hint: "Select a project to inspect it.",
    no_projects: "No generated projects yet.",
    open_details: "Details",
    review_changes: "Review changes",
    commit_changes: "Commit",
    history: "History",
    restore: "Restore",
    commit_message: "Commit message",
    commit_placeholder: "Describe the project change",
    commit_now: "Commit all changes",
    restore_hash: "Commit hash",
    preview_restore: "Preview restore",
    confirm_restore: "Confirm restore",
    dirty: "Changed",
    clean: "Clean",
    branch: "Branch",
    files: "Files",
    diff: "Diff",
    local_git: "Local Git",
    branch_name: "Branch name",
    create_branch: "New branch",
    switch_branch: "Switch",
    save_snapshot: "Save",
    save_message: "Save message",
    merge_to_main: "Merge to main",
    delete_branch: "Delete branch",
    rollback_to_save: "Restore here",
    git_history_graph: "History graph",
    no_commits: "No saves yet.",
    restore_confirm_prompt: "Review this restore target, then confirm to create a safe restore commit:",
    confirm_restore: "Confirm restore",
    broker_managed: "Dashboard broker",
    broker_external: "External broker",
    broker_stopped: "Broker stopped",
    broker_http: "HTTP",
    broker_token: "Token",
    token_ready: "token: ready",
    token_missing: "token: missing",
    broker_executors: "Executors",
    hastur_config_title: "Hastur Broker",
    hastur_config_note: "Start the local broker, keep the token private, and check whether Godot executors are connected.",
    skills_title: "Skills",
    skills_note: "Manage global and project skills. Vendored Hastur skills are read-only.",
    skill_scope: "Scope",
    skill_scope_global: "Global",
    skill_scope_project: "Project",
    skill_project: "Project",
    skill_uploads: "Skill files",
    skill_file_button: "Choose files",
    skill_no_files: "No files selected",
    skill_files_selected: "files selected",
    upload_skill: "Upload Skill",
    skill_uploaded: "Skill uploaded.",
    skills_loaded: "Skills loaded.",
    delete_skill: "Delete",
    readonly_skill: "read-only",
    user_skill: "user skill",
    start_broker: "Start Broker",
    stop_broker: "Stop Broker",
    broker_status: "Status",
    broker_logs: "Logs",
    load_executors: "Executors",
    chat_title: "LLM + Hastur Chat",
    chat_note: "Use one input. The agent streams LLM text, asks for choices when needed, and executes confirmed steps through Hastur.",
    hastur_project: "Project",
    chat_placeholder: "/godot-remote-executor Add a Label node to Main.tscn and save the scene.",
    send_to_llm: "Send",
    plan_with_llm: "Plan",
    chat_required: "Select a project and enter a message.",
    sending_chat: "Starting task...",
    chat_done: "Task completed.",
    chat_git_note: "Git actions are manual. Open the workbench to save, merge, restore, or manage branches.",
    open_git_workbench: "Open Git Workbench",
    changed_files: "Changed files",
    revert_commit: "Revert commit",
    restore_confirm_prompt: "Review this restore target, then confirm to create a safe restore commit:",
    confirm_restore: "Confirm restore",
    no_changes: "No local changes.",
    task_review: "Task review",
    confirm_plan: "Confirm plan",
    request_changes: "Request changes",
    choose_option: "Choose option",
    keep_visual: "Keep",
    send_feedback: "Send feedback",
    confirmation_needed: "Confirmation required before execution.",
    confirm_execute: "Confirm and execute",
    answer_and_continue: "Answer and continue",
    custom_reply: "Other instructions",
    technical_details: "Technical details",
    assets_title: "Image Pipeline",
    assets_badge: "review workflow",
    assets_note: "Generate visual references with the saved image API key, review them, then attach approved assets to project docs.",
    asset_project: "Project",
    asset_purpose: "Purpose",
    purpose_concept: "Concept art",
    purpose_gdd: "GDD reference",
    purpose_sprite: "2D sprite draft",
    purpose_icon: "UI/Icon",
    purpose_texture: "Texture reference",
    purpose_blender: "Blender/3D reference",
    image_size: "Size",
    image_quality: "Quality",
    asset_prompt: "Image Prompt",
    asset_prompt_placeholder: "A readable top-down concept image for a dark fantasy Godot prototype.",
    asset_uploads: "Reference Files and Images",
    save_asset_settings: "Save Image Defaults",
    generate_image: "Generate Image",
    asset_project_required: "Select a project and enter an image prompt.",
    generating_image: "Generating image...",
    image_generated: "Image generated.",
    no_assets: "No generated image assets yet.",
    attach_gdd: "Approve to GDD",
    mark_blender: "Mark Blender Reference",
    regenerate: "Regenerate",
    asset_updated: "Asset updated.",
    file_path: "File path",
    status: "Status",
    project_path: "Project path",
    generated_files: "Generated files",
  },
  zh: {
    eyebrow: "Godot 控制台",
    app_title: "AI 游戏开发 Agent",
    header_note: "创建启用 Hastur 的 Godot 项目，使用内置 skill 聊天操作，生成参考图，并审查本地 Git 改动。",
    loading: "加载中",
    ready: "就绪",
    settings_error: "设置错误",
    tab_manage: "管理",
    tab_hastur: "LLM + Hastur",
    tab_images: "图像管线",
    settings_title: "API 设置",
    settings_note: "只粘贴 API key。提供商与默认模型会自动选择。",
    checking_key: "检查密钥",
    key_configured: "API 密钥已配置",
    key_missing: "API 密钥未配置",
    llm_key: "LLM API 密钥",
    image_key: "图像 API 密钥",
    save_settings: "保存设置",
    test_connection: "测试 LLM",
    test_image_config: "检查图像配置",
    saving_settings: "正在保存设置...",
    settings_saved: "设置已保存。",
    testing_connection: "正在测试连接...",
    checking_image_config: "正在检查图像配置...",
    connection_ok: "连接测试成功。",
    image_config_ok: "图像配置可用。",
    godot_project_title: "空白 Godot 项目",
    godot_project_badge: "已启用 Hastur",
    godot_project_note: "创建一个最小 Godot 项目，自动启用 Hastur 编辑器插件并初始化本地 Git。",
    project_name: "项目名称",
    project_name_placeholder: "例如：Shadow Garden",
    create_godot_project: "创建项目",
    project_required: "请输入项目名称。",
    creating_project: "正在创建项目...",
    godot_project_created: "项目已创建。",
    project_workbench: "项目工作台",
    refresh: "刷新",
    workbench_note: "选择已生成项目，并使用简化的本地 Git 工作台。",
    select_project_hint: "请选择一个项目。",
    no_projects: "还没有生成项目。",
    open_details: "详情",
    review_changes: "审查改动",
    commit_changes: "提交",
    history: "历史",
    restore: "还原",
    commit_message: "提交信息",
    commit_placeholder: "描述这次项目改动",
    commit_now: "提交全部改动",
    restore_hash: "Commit hash",
    preview_restore: "预览还原",
    confirm_restore: "确认还原",
    dirty: "有改动",
    clean: "干净",
    branch: "分支",
    files: "文件",
    diff: "Diff",
    local_git: "本地 Git",
    hastur_config_title: "Hastur Broker",
    hastur_config_note: "启动本地 broker，私下保存 token，并检查 Godot executor 是否连接。",
    start_broker: "启动 Broker",
    stop_broker: "停止 Broker",
    broker_status: "状态",
    broker_logs: "日志",
    load_executors: "Executors",
    chat_title: "LLM + Hastur 聊天",
    chat_note: "只使用一个输入框。Agent 会流式返回 LLM 内容，在需要时询问选择，并通过 Hastur 执行已确认步骤。",
    hastur_project: "项目",
    chat_placeholder: "/godot-remote-executor 给 Main.tscn 添加一个 Label 节点并保存场景。",
    send_to_llm: "发送",
    chat_required: "请选择项目并输入消息。",
    sending_chat: "正在启动任务...",
    chat_done: "任务完成。",
    chat_git_note: "Git 操作需要手动执行。打开工作台来保存、合并、回档或管理分支。",
    open_git_workbench: "打开 Git 工作台",
    changed_files: "改动文件",
    revert_commit: "反向提交",
    restore_confirm_prompt: "请先确认这个回档目标；确认后会创建一个安全恢复提交：",
    confirm_restore: "确认回档",
    no_changes: "没有本地改动。",
    task_review: "任务确认",
    confirm_plan: "确认计划",
    request_changes: "要求修改",
    choose_option: "选择方案",
    keep_visual: "保持",
    send_feedback: "发送反馈",
    confirmation_needed: "执行前需要确认。",
    confirm_execute: "确认并执行",
    answer_and_continue: "回答并继续",
    technical_details: "技术细节",
    assets_title: "图像管线",
    assets_badge: "审查流程",
    assets_note: "使用保存的图像 API key 生成视觉参考，审查后附加到项目文档。",
    asset_project: "项目",
    asset_purpose: "用途",
    purpose_concept: "概念图",
    purpose_gdd: "GDD 参考",
    purpose_sprite: "2D 草图",
    purpose_icon: "UI/图标",
    purpose_texture: "材质参考",
    purpose_blender: "Blender/3D 参考",
    image_size: "尺寸",
    image_quality: "质量",
    asset_prompt: "图像提示词",
    asset_prompt_placeholder: "为暗黑幻想 Godot 原型生成一张清晰易读的俯视概念图。",
    asset_uploads: "参考文件与图片",
    save_asset_settings: "保存图像默认值",
    generate_image: "生成图像",
    asset_project_required: "请选择项目并输入图像提示词。",
    generating_image: "正在生成图像...",
    image_generated: "图像已生成。",
    no_assets: "还没有生成图像资产。",
    attach_gdd: "批准加入 GDD",
    mark_blender: "标记为 Blender 参考",
    regenerate: "重新生成",
    asset_updated: "资产已更新。",
    file_path: "文件路径",
    status: "状态",
    project_path: "项目路径",
    generated_files: "生成文件",
  },
};

const uiTranslations = {
  en: {
    eyebrow: "Godot control plane",
    app_title: "AI Game Development Agent",
    header_note: "Create Hastur-enabled Godot projects, use skill-grounded chat operations, generate references, and review local Git changes.",
    loading: "Loading",
    ready: "Ready",
    settings_error: "Settings error",
    tab_manage: "Manage",
    tab_hastur: "LLM + Hastur",
    tab_images: "Image Pipeline",
    settings_title: "API Settings",
    settings_note: "Paste API keys here. Providers and default models are selected automatically.",
    checking_key: "Checking key",
    key_configured: "API key configured",
    key_missing: "API key missing",
    llm_key: "LLM API Key",
    image_key: "Image API Key",
    save_settings: "Save Settings",
    test_connection: "Test LLM",
    test_image_config: "Test Image Config",
    saving_settings: "Saving settings...",
    settings_saved: "Settings saved.",
    testing_connection: "Testing connection...",
    checking_image_config: "Checking image configuration...",
    connection_ok: "Connection test succeeded.",
    image_config_ok: "Image configuration is ready.",
    godot_project_title: "Blank Godot Project",
    godot_project_badge: "Hastur enabled",
    godot_project_note: "Create a minimal Godot project with the Hastur editor plugin enabled and local Git initialized.",
    project_name: "Project Name",
    project_name_placeholder: "Example: Shadow Garden",
    create_godot_project: "Create Project",
    project_required: "Enter a project name.",
    creating_project: "Creating project...",
    godot_project_created: "Project created.",
    project_workbench: "Project Workbench",
    refresh: "Refresh",
    workbench_note: "Select a generated project and use the simple local Git workbench.",
    select_project_hint: "Select a project to inspect it.",
    no_projects: "No generated projects yet.",
    open_details: "Details",
    review_changes: "Git Workbench",
    dirty: "changed",
    clean: "clean",
    branch: "Branch",
    files: "Files",
    local_git: "Local Git",
    branch_name: "Branch name",
    create_branch: "New branch",
    switch_branch: "Switch",
    save_snapshot: "Save",
    save_message: "Save message",
    commit_placeholder: "Describe this project change",
    merge_to_main: "Merge to main",
    delete_branch: "Delete branch",
    rollback_to_save: "Restore here",
    git_history_graph: "History graph",
    no_commits: "No saves yet.",
    changed_files: "Changed files",
    no_changes: "No local changes.",
    not_git_repository: "Not a Git repository.",
    project_root: "Project root",
    stop_task: "Stop",
    task_cancelled: "Task cancelled.",
    git_status_added: "Added",
    git_status_modified: "Modified",
    git_status_deleted: "Deleted",
    git_status_renamed: "Renamed",
    git_status_copied: "Copied",
    git_status_type_changed: "Type changed",
    git_status_conflict: "Conflict",
    git_status_changed: "Changed",
    broker_managed: "Dashboard broker",
    broker_external: "External broker",
    broker_stopped: "Broker stopped",
    broker_http: "HTTP",
    broker_token: "Token",
    token_ready: "token: ready",
    token_missing: "token: missing",
    broker_executors: "Executors",
    broker_running: "running",
    broker_state_stopped: "stopped",
    broker_reachable: "reachable",
    broker_unreachable: "unreachable",
    external_broker_note: "This broker was not started by the dashboard, so this page cannot stop it.",
    hastur_config_title: "Hastur Broker",
    hastur_config_note: "Start the local broker, keep the token private, and check whether Godot executors are connected.",
    start_broker: "Start Broker",
    stop_broker: "Stop Broker",
    broker_status: "Status",
    broker_logs: "Logs",
    load_executors: "Executors",
    skills_title: "Skills",
    skills_note: "Manage global and project skills. Vendored Hastur skills are read-only.",
    skill_scope: "Scope",
    skill_scope_global: "Global",
    skill_scope_project: "Project",
    skill_project: "Project",
    skill_uploads: "Skill files",
    skill_file_button: "Choose files",
    skill_no_files: "No files selected",
    skill_files_selected: "files selected",
    upload_skill: "Upload Skill",
    skill_uploaded: "Skill uploaded.",
    skills_loaded: "Skills loaded.",
    delete_skill: "Delete",
    readonly_skill: "read-only",
    user_skill: "user skill",
    chat_title: "LLM + Hastur Chat",
    chat_note: "Use one input. The agent streams public work notes, asks only when needed, and executes through Hastur.",
    hastur_project: "Project",
    chat_placeholder: "/godot-remote-executor Add a Label node to Main.tscn and save the scene.",
    send_to_llm: "Send",
    plan_with_llm: "Plan",
    chat_required: "Select a project and enter a message.",
    sending_chat: "Starting task...",
    chat_done: "Task completed.",
    chat_git_note: "Git actions are manual. Open the workbench to save, merge, restore, or manage branches.",
    open_git_workbench: "Open Git Workbench",
    executor_missing: "executor missing",
    executors_loaded: "Executors loaded.",
    no_executor_available: "No executor available.",
    broker_stopped_state: "broker stopped",
    confirmation_needed: "Confirmation required",
    answer_and_continue: "Answer and continue",
    custom_reply: "Other instructions",
    thinking_placeholder: "Thinking...",
    current_task_panel: "Current Task",
    idle: "Idle",
    task_idle_note: "Send a message to start a task. Progress will appear here instead of inside the chat.",
    task_started: "Task started.",
    task_phase: "Phase",
    task_strategy: "Strategy",
    task_complexity: "Complexity",
    task_failed_brief: "The task failed. Check the task panel for the last error and repair status.",
    work_log: "Work Log",
    clear_log: "Clear",
    work_log_empty: "Public work notes will stream here.",
    close: "Close",
    attach_files: "Attach files",
    assets_title: "Image Pipeline",
    assets_badge: "review workflow",
    assets_note: "Generate visual references with the saved image API key, review them, then attach approved assets to project docs.",
    asset_project: "Project",
    asset_purpose: "Purpose",
    purpose_concept: "Concept art",
    purpose_gdd: "GDD reference",
    purpose_sprite: "2D sprite draft",
    purpose_icon: "UI/Icon",
    purpose_texture: "Texture reference",
    purpose_blender: "Blender/3D reference",
    image_size: "Size",
    image_quality: "Quality",
    asset_prompt: "Image Prompt",
    asset_prompt_placeholder: "A readable top-down concept image for a dark fantasy Godot prototype.",
    asset_uploads: "Reference Files and Images",
    asset_file_button: "Choose files",
    asset_no_files: "No files selected",
    asset_files_selected: "files selected",
    save_asset_settings: "Save Image Defaults",
    generate_image: "Generate Image",
    asset_project_required: "Select a project and enter an image prompt.",
    generating_image: "Generating image...",
    image_generated: "Image generated.",
    no_assets: "No generated image assets yet.",
    attach_gdd: "Approve to GDD",
    mark_blender: "Mark Blender Reference",
    regenerate: "Regenerate",
    asset_updated: "Asset updated.",
    file_path: "File path",
    status: "Status",
    project_path: "Project path",
    generated_files: "Generated files",
  },
  zh: {
    eyebrow: "Godot 控制台",
    app_title: "AI 游戏开发 Agent",
    header_note: "创建启用 Hastur 的 Godot 项目，使用内置 skill 聊天操作，生成参考图，并审查本地 Git 改动。",
    loading: "加载中",
    ready: "就绪",
    settings_error: "设置错误",
    tab_manage: "管理",
    tab_hastur: "LLM + Hastur",
    tab_images: "图像管线",
    settings_title: "API 设置",
    settings_note: "只粘贴 API key。提供商与默认模型会自动选择。",
    checking_key: "检查密钥",
    key_configured: "API 密钥已配置",
    key_missing: "API 密钥未配置",
    llm_key: "LLM API 密钥",
    image_key: "图像 API 密钥",
    save_settings: "保存设置",
    test_connection: "测试 LLM",
    test_image_config: "检查图像配置",
    saving_settings: "正在保存设置...",
    settings_saved: "设置已保存。",
    testing_connection: "正在测试连接...",
    checking_image_config: "正在检查图像配置...",
    connection_ok: "连接测试成功。",
    image_config_ok: "图像配置可用。",
    godot_project_title: "空白 Godot 项目",
    godot_project_badge: "已启用 Hastur",
    godot_project_note: "创建一个最小 Godot 项目，自动启用 Hastur 编辑器插件并初始化本地 Git。",
    project_name: "项目名称",
    project_name_placeholder: "例如：Shadow Garden",
    create_godot_project: "创建项目",
    project_required: "请输入项目名称。",
    creating_project: "正在创建项目...",
    godot_project_created: "项目已创建。",
    project_workbench: "项目工作台",
    refresh: "刷新",
    workbench_note: "选择已生成项目，并使用简化的本地 Git 工作台。",
    select_project_hint: "请选择一个项目。",
    no_projects: "还没有生成项目。",
    open_details: "详情",
    review_changes: "Git 工作台",
    dirty: "有改动",
    clean: "干净",
    branch: "分支",
    files: "文件",
    local_git: "本地 Git",
    branch_name: "分支名称",
    create_branch: "新建分支",
    switch_branch: "切换",
    save_snapshot: "保存",
    save_message: "保存说明",
    commit_placeholder: "描述这次项目改动",
    merge_to_main: "合并到 main",
    delete_branch: "删除分支",
    rollback_to_save: "安全回档到这里",
    git_history_graph: "历史图",
    no_commits: "还没有保存点。",
    restore_confirm_prompt: "请先确认这个回档目标；确认后会创建一个安全恢复提交：",
    confirm_restore: "确认回档",
    changed_files: "改动文件",
    no_changes: "没有本地改动。",
    not_git_repository: "这不是 Git 仓库。",
    project_root: "项目根目录",
    stop_task: "停止",
    task_cancelled: "任务已停止。",
    git_status_added: "新增",
    git_status_modified: "修改",
    git_status_deleted: "删除",
    git_status_renamed: "重命名",
    git_status_copied: "复制",
    git_status_type_changed: "类型变化",
    git_status_conflict: "冲突",
    git_status_changed: "改动",
    broker_managed: "控制台启动的 broker",
    broker_external: "外部运行的 broker",
    broker_stopped: "Broker 已停止",
    broker_http: "HTTP",
    broker_token: "Token",
    token_ready: "token: 就绪",
    token_missing: "token: 缺失",
    broker_executors: "Executors",
    broker_running: "运行中",
    broker_state_stopped: "已停止",
    broker_reachable: "可连接",
    broker_unreachable: "不可连接",
    external_broker_note: "这个 broker 不是由控制台启动的，所以这里不能停止它。",
    hastur_config_title: "Hastur Broker",
    hastur_config_note: "启动本地 broker，私下保存 token，并检查 Godot executor 是否连接。",
    start_broker: "启动 Broker",
    stop_broker: "停止 Broker",
    broker_status: "状态",
    broker_logs: "日志",
    load_executors: "Executors",
    skills_title: "Skills",
    skills_note: "管理全局和项目 skills。内置 Hastur skills 为只读。",
    skill_scope: "范围",
    skill_scope_global: "全局",
    skill_scope_project: "项目",
    skill_project: "项目",
    skill_uploads: "Skill 文件",
    skill_file_button: "选择文件",
    skill_no_files: "未选择文件",
    skill_files_selected: "个文件已选择",
    upload_skill: "上传 Skill",
    skill_uploaded: "Skill 已上传。",
    skills_loaded: "Skills 已加载。",
    delete_skill: "删除",
    readonly_skill: "只读",
    user_skill: "用户 skill",
    chat_title: "LLM + Hastur 聊天",
    chat_note: "只使用一个输入框。Agent 会流式显示公开工作记录，只在需要时询问，并通过 Hastur 执行。",
    hastur_project: "项目",
    chat_placeholder: "/godot-remote-executor 给 Main.tscn 添加一个 Label 节点并保存场景。",
    send_to_llm: "发送",
    plan_with_llm: "计划",
    chat_required: "请选择项目并输入消息。",
    sending_chat: "正在启动任务...",
    chat_done: "任务完成。",
    chat_git_note: "Git 操作需要手动执行。打开工作台来保存、合并、回档或管理分支。",
    open_git_workbench: "打开 Git 工作台",
    executor_missing: "executor 未连接",
    executors_loaded: "Executors 已加载。",
    no_executor_available: "没有可用 executor。",
    broker_stopped_state: "broker 已停止",
    confirmation_needed: "需要确认",
    answer_and_continue: "回答并继续",
    thinking_placeholder: "思考中...",
    close: "关闭",
    attach_files: "添加文件",
    assets_title: "图像管线",
    assets_badge: "审查流程",
    assets_note: "使用保存的图像 API key 生成视觉参考，审查后附加到项目文档。",
    asset_project: "项目",
    asset_purpose: "用途",
    purpose_concept: "概念图",
    purpose_gdd: "GDD 参考",
    purpose_sprite: "2D 草图",
    purpose_icon: "UI/图标",
    purpose_texture: "材质参考",
    purpose_blender: "Blender/3D 参考",
    image_size: "尺寸",
    image_quality: "质量",
    asset_prompt: "图像提示词",
    asset_prompt_placeholder: "为暗黑幻想 Godot 原型生成一张清晰易读的俯视概念图。",
    asset_uploads: "参考文件与图片",
    asset_file_button: "选择文件",
    asset_no_files: "未选择文件",
    asset_files_selected: "个文件已选择",
    save_asset_settings: "保存图像默认值",
    generate_image: "生成图像",
    asset_project_required: "请选择项目并输入图像提示词。",
    generating_image: "正在生成图像...",
    image_generated: "图像已生成。",
    no_assets: "还没有生成图像资产。",
    attach_gdd: "批准加入 GDD",
    mark_blender: "标记为 Blender 参考",
    regenerate: "重新生成",
    asset_updated: "资产已更新。",
    file_path: "文件路径",
    status: "状态",
    project_path: "项目路径",
    generated_files: "生成文件",
  },
};

const state = {
  language: localStorage.getItem("language") || "zh",
  view: localStorage.getItem("view") || "manage",
  projects: [],
  selectedProject: localStorage.getItem("selectedProject") || "",
  assets: [],
  skills: [],
  skillProject: localStorage.getItem("skillProject") || "",
  selectedSkill: "godot-remote-executor",
  chatAttachments: [],
  activeTask: null,
  activeEventSource: null,
  activeAssistantMessage: null,
  taskProgress: null,
  taskError: "",
  workLog: [],
  taskWaiting: false,
  projectDetailMode: "details",
  lastBrokerStatus: null,
  lastBrokerMessage: "",
  lastReadinessStatus: null,
  lastExecutorStatus: null,
  lastHasHasturToken: null,
};

function $(id) {
  return document.getElementById(id);
}

function t(key) {
  return uiTranslations[state.language][key] || uiTranslations.en[key] || key;
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function setLanguage(language) {
  state.language = language;
  localStorage.setItem("language", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  applyTranslations();
  if ($("connectionStatus").classList.contains("success")) setConnectionStatus(t("ready"), "success");
  renderProjects();
  renderProjectSelectors();
  renderAssetGallery();
  renderChatAttachments();
  renderAssetFileLabel();
  renderSkillFileLabel();
  renderSkillsPanel();
  renderTaskPanel(state.taskProgress || {});
  renderWorkLog();
  if ($("hasturTokenStatus") && state.lastHasHasturToken !== null) $("hasturTokenStatus").textContent = state.lastHasHasturToken ? t("token_ready") : t("token_missing");
  updateChatReadiness(state.lastReadinessStatus, state.lastExecutorStatus);
  if (state.lastBrokerStatus) renderBrokerStatus(state.lastBrokerStatus, state.lastBrokerMessage);
  if (state.selectedProject) {
    if (state.projectDetailMode === "git") reviewProjectChanges(state.selectedProject);
    else showProjectDetails(state.selectedProject);
  }
  if ($("chat_git_output")) refreshChatGit();
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  $("langEn").classList.toggle("active", state.language === "en");
  $("langZh").classList.toggle("active", state.language === "zh");
}

function showView(view) {
  state.view = view;
  localStorage.setItem("view", view);
  ["manage", "hastur", "images"].forEach((name) => {
    $(`view${capitalize(name)}`).classList.toggle("active", name === view);
    $(`tab${capitalize(name)}`).classList.toggle("active", name === view);
  });
  if (view === "hastur") refreshChatGit();
}

function setConnectionStatus(text, kind = "") {
  $("connectionStatus").textContent = text;
  $("connectionStatus").className = `status-pill ${kind}`.trim();
}

function setMessage(id, text, kind = "") {
  const node = $(id);
  if (!node) return;
  node.textContent = text || "";
  node.className = `message ${kind}`.trim();
}

async function requestJSON(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let payload = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { detail: text };
  }
  if (!response.ok) {
    const detail = payload.detail || response.statusText || "Request failed";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

async function loadSettings() {
  try {
    const data = await requestJSON("/api/settings");
    $("image_size").value = data.image_size || "1024x1024";
    $("image_quality").value = data.image_quality || "medium";
    const hasAnyKey = data.has_llm_api_key || data.has_image_api_key;
    $("apiKeyStatus").textContent = hasAnyKey ? t("key_configured") : t("key_missing");
    state.lastHasHasturToken = Boolean(data.has_hastur_auth_token);
    $("hasturTokenStatus").textContent = state.lastHasHasturToken ? t("token_ready") : t("token_missing");
    setConnectionStatus(t("ready"), "success");
    updateChatReadiness();
  } catch (error) {
    setConnectionStatus(t("settings_error"), "error");
    setMessage("settingsMessage", error.message, "error");
  }
}

async function saveSettings() {
  setMessage("settingsMessage", t("saving_settings"));
  try {
    const body = {
      llm_api_key: $("apiKey").value || null,
      openai_api_key: $("apiKey").value || null,
      image_api_key: $("imageApiKey").value || null,
      image_size: $("image_size").value,
      image_quality: $("image_quality").value,
    };
    const result = await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    $("apiKey").value = "";
    $("imageApiKey").value = "";
    setMessage("settingsMessage", result.message || t("settings_saved"), "success");
    await loadSettings();
  } catch (error) {
    setMessage("settingsMessage", error.message, "error");
  }
}

async function testLLM() {
  setMessage("settingsMessage", t("testing_connection"));
  try {
    const result = await requestJSON("/api/settings/test-llm", { method: "POST" });
    setMessage("settingsMessage", result.message || t("connection_ok"), "success");
  } catch (error) {
    setMessage("settingsMessage", error.message, "error");
  }
}

async function testImageConfig() {
  setMessage("settingsMessage", t("checking_image_config"));
  try {
    const result = await requestJSON("/api/settings/test-image-config", { method: "POST" });
    setMessage("settingsMessage", result.message || t("image_config_ok"), "success");
  } catch (error) {
    setMessage("settingsMessage", error.message, "error");
  }
}

async function createProject() {
  const projectName = $("project_name").value.trim();
  if (!projectName) {
    setMessage("projectMessage", t("project_required"), "error");
    return;
  }
  setMessage("projectMessage", t("creating_project"));
  $("project_output").innerHTML = `<p>${escapeHTML(t("creating_project"))}</p>`;
  try {
    const result = await requestJSON("/api/godot-projects/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_name: projectName }),
    });
    setMessage("projectMessage", result.message || t("godot_project_created"), "success");
    state.selectedProject = result.project_slug;
    localStorage.setItem("selectedProject", state.selectedProject);
    $("project_output").innerHTML = projectSummaryHTML(result);
    await loadProjects();
  } catch (error) {
    setMessage("projectMessage", error.message, "error");
    $("project_output").innerHTML = `<p class="error-text">${escapeHTML(error.message)}</p>`;
  }
}

async function loadProjects() {
  try {
    const data = await requestJSON("/api/projects");
    state.projects = data.projects || [];
    if (!state.selectedProject && state.projects.length) state.selectedProject = state.projects[0].slug;
    renderProjects();
    renderProjectSelectors();
    if (state.selectedProject) await showProjectDetails(state.selectedProject);
  } catch (error) {
    $("recent_projects").innerHTML = `<li class="error-row">${escapeHTML(error.message)}</li>`;
  }
}

function renderProjectSelectors() {
  [$("asset_project_slug"), $("hastur_project_slug"), $("skill_project_slug")].filter(Boolean).forEach((select) => {
    const selected = select.value || state.selectedProject;
    select.innerHTML = state.projects.map((project) => `<option value="${escapeAttr(project.slug)}">${escapeHTML(project.slug)}</option>`).join("");
    if (!state.projects.length) {
      select.innerHTML = `<option value="">${escapeHTML(t("no_projects"))}</option>`;
    } else {
      select.value = selected && state.projects.some((project) => project.slug === selected) ? selected : state.projects[0].slug;
    }
  });
  if (state.projects.length) loadAssetsForSelectedProject();
  if ($("skill_project_slug") && state.skillProject) $("skill_project_slug").value = state.skillProject;
  loadSkills();
}

function renderProjects() {
  const list = $("recent_projects");
  if (!state.projects.length) {
    list.innerHTML = `<li class="muted-row">${escapeHTML(t("no_projects"))}</li>`;
    $("project_detail_pane").innerHTML = `<p class="muted-row">${escapeHTML(t("select_project_hint"))}</p>`;
    return;
  }
  list.innerHTML = state.projects.map((project) => {
    const active = project.slug === state.selectedProject ? "active" : "";
    return `<li><button type="button" class="project-card ${active}" onclick="selectProject('${escapeAttr(project.slug)}')"><strong>${escapeHTML(project.slug)}</strong><span title="${escapeAttr(project.path)}">${escapeHTML(project.path)}</span></button></li>`;
  }).join("");
}

async function selectProject(slug) {
  state.selectedProject = slug;
  localStorage.setItem("selectedProject", slug);
  renderProjects();
  renderProjectSelectors();
  await showProjectDetails(slug);
  await refreshChatGit();
}

function selectedProject() {
  return state.projects.find((project) => project.slug === state.selectedProject);
}

async function showProjectDetails(slug) {
  state.projectDetailMode = "details";
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}`);
    $("project_detail_pane").innerHTML = projectActionShell(slug, projectSummaryHTML({
      project_path: data.path,
      generated_files: data.files || [],
    }));
  } catch (error) {
    renderProjectError(error.message);
  }
}

async function reviewProjectChanges(slug) {
  state.projectDetailMode = "git";
  try {
    const [data, graphData] = await Promise.all([
      requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/changes`),
      requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/graph`),
    ]);
    $("project_detail_pane").innerHTML = projectActionShell(slug, gitWorkbenchHTML(slug, data, "project_detail_pane", graphData));
  } catch (error) {
    renderProjectError(error.message);
  }
}

async function refreshGitWorkbench(slug, targetId = "project_detail_pane") {
  const [data, graphData] = await Promise.all([
    requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/changes`),
    requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/graph`),
  ]);
  const target = $(targetId);
  if (target) target.innerHTML = targetId === "project_detail_pane" ? projectActionShell(slug, gitWorkbenchHTML(slug, data, targetId, graphData)) : gitCompactHTML(slug, data.status || {});
  await refreshChatGit();
}

async function saveGitSnapshot(slug, targetId = "project_detail_pane") {
  const input = $(`${targetId}_save_message`);
  const message = input ? input.value.trim() : "";
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
    setGitActionOutput(targetId, data);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

async function createGitBranch(slug, targetId = "project_detail_pane") {
  const input = $(`${targetId}_new_branch`);
  const name = input ? input.value.trim() : "";
  if (!name) return;
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/branches`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
    setGitActionOutput(targetId, data);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

async function switchGitBranch(slug, targetId = "project_detail_pane") {
  const select = $(`${targetId}_branch_select`);
  const name = select ? select.value : "";
  if (!name) return;
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/branches/switch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

async function mergeGitToMain(slug, targetId = "project_detail_pane") {
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/merge-to-main`, { method: "POST" });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
    setGitActionOutput(targetId, data);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

async function deleteGitBranch(slug, branch, targetId = "project_detail_pane") {
  if (!branch) return;
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/branches/${encodeURIComponent(branch)}`, { method: "DELETE" });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
    setGitActionOutput(targetId, data);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

async function rollbackToCommit(slug, commitHash, targetId = "project_detail_pane") {
  if (!commitHash) return;
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/rollback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commit_hash: commitHash, confirm: true }),
    });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
    setGitActionOutput(targetId, data);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

function showRestoreConfirmation(slug, commitHash, shortHash, subject, targetId = "project_detail_pane") {
  const node = $(`${targetId}_git_action_output`);
  if (!node || !commitHash) return;
  const label = [shortHash, subject].filter(Boolean).join(" ");
  node.innerHTML = `
    <div class="restore-confirm">
      <p>${escapeHTML(t("restore_confirm_prompt"))}</p>
      <p><code>${escapeHTML(label || commitHash)}</code></p>
      <button type="button" onclick="rollbackToCommit('${escapeAttr(slug)}', '${escapeAttr(commitHash)}', '${escapeAttr(targetId)}')">${escapeHTML(t("confirm_restore"))}</button>
    </div>`;
}

async function revertCommit(slug, commitHash, targetId = "project_detail_pane") {
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/revert`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commit_hash: commitHash }),
    });
    setGitActionOutput(targetId, data);
    await refreshGitWorkbench(slug, targetId);
    setGitActionOutput(targetId, data);
  } catch (error) {
    setGitActionOutput(targetId, { success: false, message: error.message });
  }
}

function projectActionShell(slug, inner) {
  const project = state.projects.find((item) => item.slug === slug) || selectedProject();
  return `
    <div class="detail-header">
      <div><h3>${escapeHTML(slug)}</h3><p>${escapeHTML(project ? project.path : "")}</p></div>
      <div class="segmented-actions">
        <button type="button" onclick="showProjectDetails('${escapeAttr(slug)}')">${escapeHTML(t("open_details"))}</button>
        <button type="button" onclick="reviewProjectChanges('${escapeAttr(slug)}')">${escapeHTML(t("review_changes"))}</button>
      </div>
    </div>${inner}`;
}

function renderProjectError(message) {
  $("project_detail_pane").innerHTML = `<p class="error-text">${escapeHTML(message)}</p>`;
}

function projectSummaryHTML(result) {
  const files = result.generated_files || [];
  return `<dl><dt>${escapeHTML(t("project_path"))}</dt><dd><code>${escapeHTML(result.project_path || "")}</code></dd></dl>${files.length ? `<h4>${escapeHTML(t("generated_files"))}</h4><ul class="file-list">${files.map((file) => `<li>${escapeHTML(file)}</li>`).join("")}</ul>` : ""}`;
}

function gitWorkbenchHTML(slug, data, targetId = "project_detail_pane", graphData = null) {
  const status = data.status || {};
  const files = data.files || [];
  const branches = status.branches || [];
  const current = status.branch || "";
  return `
    <div class="git-control-grid">
      <label><span>${escapeHTML(t("branch"))}</span><select id="${targetId}_branch_select" onchange="switchGitBranch('${escapeAttr(slug)}', '${escapeAttr(targetId)}')">${branches.map((branch) => `<option value="${escapeAttr(branch.name)}" ${branch.current ? "selected" : ""}>${escapeHTML(branch.name)}</option>`).join("")}</select></label>
      <label><span>${escapeHTML(t("branch_name"))}</span><input id="${targetId}_new_branch" autocomplete="off" placeholder="feature-name"></label>
      <button type="button" onclick="createGitBranch('${escapeAttr(slug)}', '${escapeAttr(targetId)}')">${escapeHTML(t("create_branch"))}</button>
    </div>
    <div class="status-strip"><span>${escapeHTML(t("branch"))}: ${escapeHTML(current || "-")}</span><span>${escapeHTML(status.dirty ? `${status.dirty_count || files.length} ${t("dirty")}` : t("clean"))}</span></div>
    <div class="git-save-row">
      <label><span>${escapeHTML(t("save_message"))}</span><input id="${targetId}_save_message" autocomplete="off" placeholder="${escapeAttr(t("commit_placeholder"))}"></label>
      <button type="button" onclick="saveGitSnapshot('${escapeAttr(slug)}', '${escapeAttr(targetId)}')" ${status.can_save ? "" : "disabled"}>${escapeHTML(t("save_snapshot"))}</button>
      <button type="button" class="secondary" onclick="mergeGitToMain('${escapeAttr(slug)}', '${escapeAttr(targetId)}')" ${status.can_merge_to_main ? "" : "disabled"}>${escapeHTML(t("merge_to_main"))}</button>
    </div>
    <h4>${escapeHTML(t("changed_files"))}</h4>
    ${files.length ? gitFileTreeHTML(files) : `<p class="muted-row">${escapeHTML(t("no_changes"))}</p>`}
    ${branchListHTML(slug, branches, current, targetId)}
    ${gitGraphHTML(slug, graphData || data.graph || {}, targetId)}
    <div id="${targetId}_git_action_output" class="inline-result"></div>`;
}

function branchListHTML(slug, branches, current, targetId) {
  if (!branches.length) return "";
  return `<h4>${escapeHTML(t("branch"))}</h4><div class="branch-list">${branches.map((branch) => `
    <div class="branch-row ${branch.current ? "active" : ""}">
      <span>${escapeHTML(branch.name)}${branch.default ? " · main" : ""}</span>
      <button type="button" class="secondary compact" onclick="deleteGitBranch('${escapeAttr(slug)}', '${escapeAttr(branch.name)}', '${escapeAttr(targetId)}')" ${branch.can_delete ? "" : "disabled"}>${escapeHTML(t("delete_branch"))}</button>
    </div>`).join("")}</div>`;
}

function gitGraphHTML(slug, graphData, targetId) {
  const commits = graphData.commits || [];
  return `
    <h4>${escapeHTML(t("git_history_graph"))}</h4>
    <div class="git-graph">
      ${commits.length ? commits.map((commit) => `
        <article class="git-commit-node ${commit.main ? "main" : ""}">
          <div class="commit-dot"></div>
          <div>
            <strong>${escapeHTML(commit.short_hash)} ${escapeHTML(commit.subject || "")}</strong>
            <span>${escapeHTML(commit.date || "")} ${escapeHTML((commit.refs || []).filter((ref) => ref !== "HEAD").join(" · "))}</span>
          </div>
          <button type="button" class="secondary compact" onclick="showRestoreConfirmation('${escapeAttr(slug)}', '${escapeAttr(commit.hash)}', '${escapeAttr(commit.short_hash)}', '${escapeAttr(commit.subject || "")}', '${escapeAttr(targetId)}')">${escapeHTML(t("rollback_to_save"))}</button>
        </article>`).join("") : `<p class="muted-row">${escapeHTML(t("no_commits"))}</p>`}
    </div>`;
}

function branchListHTML(slug, branches, current, targetId) {
  if (!branches.length) return "";
  return `<h4>${escapeHTML(t("branch"))}</h4><div class="branch-list">${branches.map((branch) => `
    <div class="branch-row ${branch.current ? "active" : ""}">
      <span>${escapeHTML(branch.name)}${branch.default ? " / main" : ""}</span>
      <button type="button" class="secondary compact" onclick="deleteGitBranch('${escapeAttr(slug)}', '${escapeAttr(branch.name)}', '${escapeAttr(targetId)}')" ${branch.can_delete ? "" : "disabled"}>${escapeHTML(t("delete_branch"))}</button>
    </div>`).join("")}</div>`;
}

function gitGraphHTML(slug, graphData, targetId) {
  const commits = graphData.commits || [];
  return `
    <h4>${escapeHTML(t("git_history_graph"))}</h4>
    <div class="git-graph">
      ${commits.length ? commits.map((commit) => `
        <article class="git-commit-node ${commit.main ? "main" : ""}">
          <div class="commit-dot"></div>
          <div>
            <strong>${escapeHTML(commit.short_hash)} ${escapeHTML(commit.subject || "")}</strong>
            <span>${escapeHTML(commit.date || "")} ${escapeHTML((commit.refs || []).filter((ref) => ref !== "HEAD").join(" / "))}</span>
          </div>
          <button type="button" class="secondary compact" onclick="showRestoreConfirmation('${escapeAttr(slug)}', '${escapeAttr(commit.hash)}', '${escapeAttr(commit.short_hash)}', '${escapeAttr(commit.subject || "")}', '${escapeAttr(targetId)}')">${escapeHTML(t("rollback_to_save"))}</button>
        </article>`).join("") : `<p class="muted-row">${escapeHTML(t("no_commits"))}</p>`}
    </div>`;
}

function gitFileTreeHTML(files) {
  const groups = files.reduce((result, file) => {
    const directory = file.directory || "";
    if (!result[directory]) result[directory] = [];
    result[directory].push(file);
    return result;
  }, {});
  return `<div class="git-file-list">${Object.entries(groups).map(([directory, entries]) => `
    <details class="git-dir-group" open>
      <summary><span>${escapeHTML(directory || t("project_root"))}</span><small>${entries.length}</small></summary>
      <div class="git-dir-files">${entries.map((file) => gitFileRow(file)).join("")}</div>
    </details>`).join("")}</div>`;
}

function gitFileRow(file) {
  const path = file.path || "";
  const kind = file.status_kind || "changed";
  const label = t(`git_status_${kind}`) || file.display_status || file.status || "";
  return `
    <div class="git-file-row">
      <span class="git-status-badge ${escapeAttr(kind)}">${escapeHTML(label)}</span>
      <span class="git-file-path">${escapeHTML(path)}</span>
    </div>`;
}

function gitResultHTML(data) {
  const kind = data && data.success ? "success" : "error";
  return `<p class="${kind === "success" ? "success-text" : "error-text"}">${escapeHTML((data && data.message) || "")}</p>`;
}

function setGitActionOutput(targetId, data) {
  const node = $(`${targetId}_git_action_output`);
  if (node) node.innerHTML = gitResultHTML(data);
}

async function refreshChatGit() {
  const slug = $("hastur_project_slug") ? $("hastur_project_slug").value : state.selectedProject;
  if (!slug || !$("chat_git_output")) return;
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/status`);
    $("chat_git_output").innerHTML = chatGitStatusHTML(data);
  } catch (error) {
    $("chat_git_output").innerHTML = `<p class="error-text">${escapeHTML(error.message)}</p>`;
  }
}

function chatGitStatusHTML(data) {
  if (!data.is_repo) return `<p class="muted-row">${escapeHTML(t("not_git_repository"))}</p>`;
  return gitCompactHTML($("hastur_project_slug").value || state.selectedProject, data);
}

function gitCompactHTML(slug, status) {
  return `
    <div class="status-strip"><span>${escapeHTML(t("branch"))}: ${escapeHTML(status.branch || "-")}</span><span>${escapeHTML(status.dirty ? `${status.dirty_count || 0} ${t("dirty")}` : t("clean"))}</span></div>
    <p class="muted-row">${escapeHTML(t("chat_git_note"))}</p>`;
}

function openGitWorkbench() {
  const slug = $("hastur_project_slug").value || state.selectedProject;
  if (!slug) return;
  state.selectedProject = slug;
  localStorage.setItem("selectedProject", slug);
  showView("manage");
  renderProjectSelectors();
  renderProjects();
  reviewProjectChanges(slug);
}

async function saveAssetSettings() {
  setMessage("assetMessage", t("saving_settings"));
  try {
    await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_size: $("image_size").value, image_quality: $("image_quality").value }),
    });
    setMessage("assetMessage", t("settings_saved"), "success");
  } catch (error) {
    setMessage("assetMessage", error.message, "error");
  }
}

async function loadAssetsForSelectedProject() {
  const slug = $("asset_project_slug").value;
  if (!slug) {
    state.assets = [];
    renderAssetGallery();
    return;
  }
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/assets`);
    state.assets = data.assets || [];
    renderAssetGallery();
  } catch (error) {
    state.assets = [];
    setMessage("assetMessage", error.message, "error");
    renderAssetGallery();
  }
}

async function generateImageAsset() {
  const slug = $("asset_project_slug").value;
  const prompt = $("asset_prompt").value.trim();
  if (!slug || !prompt) {
    setMessage("assetMessage", t("asset_project_required"), "error");
    return;
  }
  await saveAssetSettings();
  setMessage("assetMessage", t("generating_image"));
  try {
    const references = await readSelectedFiles($("asset_files").files);
    const referenceText = references.length ? `\n\nReference uploads:\n${references.map((file) => `- ${file.filename} (${file.media_type})${file.preview ? `: ${file.preview}` : ""}`).join("\n")}` : "";
    await requestJSON(`/api/projects/${encodeURIComponent(slug)}/assets/images/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt + referenceText,
        purpose: $("asset_purpose").value,
        size: $("image_size").value,
        quality: $("image_quality").value,
      }),
    });
    setMessage("assetMessage", t("image_generated"), "success");
    await loadAssetsForSelectedProject();
  } catch (error) {
    setMessage("assetMessage", error.message, "error");
  }
}

async function updateAsset(actionPath, assetId) {
  const slug = $("asset_project_slug").value;
  try {
    await requestJSON(`/api/projects/${encodeURIComponent(slug)}/assets/${encodeURIComponent(assetId)}${actionPath}`, { method: "POST" });
    setMessage("assetMessage", t("asset_updated"), "success");
    await loadAssetsForSelectedProject();
  } catch (error) {
    setMessage("assetMessage", error.message, "error");
  }
}

function regenerateAsset(assetId) {
  const asset = state.assets.find((item) => item.id === assetId);
  if (!asset) return;
  $("asset_prompt").value = asset.prompt || "";
  generateImageAsset();
}

function renderAssetGallery() {
  const gallery = $("asset_gallery");
  const slug = $("asset_project_slug").value;
  if (!state.assets.length) {
    gallery.innerHTML = `<p class="muted-row">${escapeHTML(t("no_assets"))}</p>`;
    return;
  }
  gallery.innerHTML = state.assets.map((asset) => `
    <article class="asset-card">
      <img src="/api/projects/${encodeURIComponent(slug)}/assets/${encodeURIComponent(asset.id)}/file" alt="${escapeAttr(asset.purpose)}">
      <div><strong>${escapeHTML(asset.id)} - ${escapeHTML(asset.purpose)}</strong><span>${escapeHTML(asset.model || "")}</span><p>${escapeHTML(asset.prompt || "")}</p><p><b>${escapeHTML(t("file_path"))}:</b> ${escapeHTML(asset.path || "")}</p><div class="button-row"><button type="button" class="secondary compact" onclick="updateAsset('/attach-to-gdd', '${escapeAttr(asset.id)}')">${escapeHTML(t("attach_gdd"))}</button><button type="button" class="secondary compact" onclick="updateAsset('/mark-blender-reference', '${escapeAttr(asset.id)}')">${escapeHTML(t("mark_blender"))}</button><button type="button" class="secondary compact" onclick="regenerateAsset('${escapeAttr(asset.id)}')">${escapeHTML(t("regenerate"))}</button></div></div>
    </article>`).join("");
}

async function loadSkills() {
  try {
    const projectSlug = $("skill_project_slug") ? $("skill_project_slug").value : state.selectedProject;
    const query = projectSlug ? `?project_slug=${encodeURIComponent(projectSlug)}` : "";
    const data = await requestJSON(`/api/skills${query}`);
    state.skills = data.skills || [];
    const preferred = state.skills.find((skill) => skill.name === "godot-remote-executor") || state.skills[0];
    state.selectedSkill = preferred ? preferred.name : "godot-remote-executor";
    renderSkillPicker();
    renderSkillsPanel();
    if ($("skillsMessage")) setMessage("skillsMessage", t("skills_loaded"), "success");
  } catch (error) {
    setMessage($("skillsMessage") ? "skillsMessage" : "chatMessage", error.message, "error");
  }
}

function triggerSkillFiles() {
  $("skill_files").click();
}

function renderSkillFileLabel() {
  const input = $("skill_files");
  const label = $("skill_files_label");
  if (!input || !label) return;
  const count = input.files ? input.files.length : 0;
  label.textContent = count ? `${count} ${t("skill_files_selected")}` : t("skill_no_files");
}

async function uploadSkill() {
  const input = $("skill_files");
  const scope = $("skill_scope").value || "global";
  const projectSlug = $("skill_project_slug").value || state.selectedProject;
  if (!input || !input.files || !input.files.length) {
    setMessage("skillsMessage", t("skill_no_files"), "error");
    return;
  }
  if (scope === "project" && !projectSlug) {
    setMessage("skillsMessage", t("select_project_hint"), "error");
    return;
  }
  try {
    const files = [];
    for (const file of Array.from(input.files)) {
      const dataUrl = await readAsDataURL(file);
      const comma = dataUrl.indexOf(",");
      files.push({
        filename: file.name,
        relative_path: file.webkitRelativePath || file.name,
        media_type: file.type || "application/octet-stream",
        data: comma >= 0 ? dataUrl.slice(comma + 1) : dataUrl,
      });
    }
    const result = await requestJSON("/api/skills/upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scope, project_slug: scope === "project" ? projectSlug : "", files }),
    });
    input.value = "";
    renderSkillFileLabel();
    setMessage("skillsMessage", result.message || t("skill_uploaded"), "success");
    await loadSkills();
  } catch (error) {
    setMessage("skillsMessage", error.message, "error");
  }
}

function renderSkillsPanel() {
  const output = $("skills_output");
  if (!output) return;
  if (!state.skills.length) {
    output.innerHTML = `<p class="muted-row">${escapeHTML(t("skill_no_files"))}</p>`;
    return;
  }
  output.innerHTML = state.skills.map((skill) => `
    <article class="skill-admin-card">
      <header>
        <div>
          <strong>/${escapeHTML(skill.name)}</strong>
          <span class="scope-pill">${escapeHTML(skill.scope || "")}</span>
          <span class="scope-pill">${escapeHTML(skill.readonly ? t("readonly_skill") : t("user_skill"))}</span>
        </div>
        ${skill.readonly ? "" : `<button type="button" class="secondary compact" onclick="deleteSkill('${escapeAttr(skill.scope)}', '${escapeAttr(skill.name)}')">${escapeHTML(t("delete_skill"))}</button>`}
      </header>
      <p>${escapeHTML(skill.description || "")}</p>
      ${skill.when_to_use ? `<p class="muted-row">${escapeHTML(skill.when_to_use)}</p>` : ""}
      <p class="muted-row">${escapeHTML(skill.path_label || skill.path || "")}</p>
    </article>`).join("");
}

async function deleteSkill(scope, name) {
  const projectSlug = $("skill_project_slug") ? $("skill_project_slug").value : state.selectedProject;
  try {
    const query = projectSlug ? `?project_slug=${encodeURIComponent(projectSlug)}` : "";
    const result = await requestJSON(`/api/skills/${encodeURIComponent(scope)}/${encodeURIComponent(name)}${query}`, { method: "DELETE" });
    setMessage("skillsMessage", result.message || t("delete_skill"), "success");
    await loadSkills();
  } catch (error) {
    setMessage("skillsMessage", error.message, "error");
  }
}

async function startBroker() {
  setMessage("hasturMessage", t("loading"));
  try {
    const data = await requestJSON("/api/hastur/broker/start", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
    renderBrokerStatus(data.status || data, data.message);
    setMessage("hasturMessage", data.message, data.success ? "success" : "error");
    await loadSettings();
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function stopBroker() {
  setMessage("hasturMessage", t("loading"));
  try {
    const data = await requestJSON("/api/hastur/broker/stop", { method: "POST" });
    renderBrokerStatus(data.status || data, data.message);
    setMessage("hasturMessage", data.message, data.success ? "success" : "error");
    await loadSettings();
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function loadBrokerStatus() {
  try {
    const data = await requestJSON("/api/hastur/broker/status");
    renderBrokerStatus(data);
    updateChatReadiness(data);
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function loadBrokerLogs() {
  try {
    const data = await requestJSON("/api/hastur/broker/logs");
    $("broker_output").textContent = (data.logs || []).join("\n");
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function loadHasturExecutors() {
  try {
    const data = await requestJSON("/api/hastur/executors");
    if (state.view === "hastur") addChatMessage("assistant", data.available ? t("executors_loaded") : data.message || t("no_executor_available"), data);
    else await loadBrokerStatus();
    updateChatReadiness(null, data);
  } catch (error) {
    setMessage(state.view === "hastur" ? "chatMessage" : "hasturMessage", error.message, "error");
  }
}

function updateChatReadiness(status = null, executors = null) {
  if (status) state.lastReadinessStatus = status;
  if (executors) state.lastExecutorStatus = executors;
  const pill = $("chatReadiness");
  if (!pill) return;
  const executorStatus = executors || state.lastExecutorStatus;
  const brokerStatus = status || state.lastReadinessStatus;
  if (executorStatus && !executorStatus.available) {
    pill.textContent = t("executor_missing");
    pill.className = "status-pill error";
    return;
  }
  if (brokerStatus && !brokerStatus.running) {
    pill.textContent = t("broker_stopped_state");
    pill.className = "status-pill error";
    return;
  }
  pill.textContent = t("ready");
  pill.className = "status-pill success";
}

function triggerChatFiles() {
  $("chat_files").click();
}

function triggerAssetFiles() {
  $("asset_files").click();
}

function renderAssetFileLabel() {
  const input = $("asset_files");
  const label = $("asset_files_label");
  if (!input || !label) return;
  const count = input.files ? input.files.length : 0;
  label.textContent = count ? `${count} ${t("asset_files_selected")}` : t("asset_no_files");
}

async function sendHasturChat(workflowMode = "auto") {
  if (typeof workflowMode !== "string") workflowMode = "auto";
  const slug = $("hastur_project_slug").value;
  const instruction = $("chat_instruction").value.trim();
  if (!slug || !instruction) {
    setMessage("chatMessage", t("chat_required"), "error");
    return;
  }
  setChatBusy(true);
  if (state.activeEventSource) state.activeEventSource.close();
  const skillName = detectSkill(instruction);
  setMessage("chatMessage", t("sending_chat"));
  addChatMessage("user", instruction, state.chatAttachments);
  beginTaskPanel({ instruction, workflowMode, skillName });
  state.activeAssistantMessage = createAssistantMessage();
  try {
    const task = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instruction, skill_name: skillName, workflow_mode: workflowMode, attachments: state.chatAttachments }),
    });
    state.activeTask = { ...task, instruction };
    openTaskStream(slug, task.task_id);
  } catch (error) {
    renderTaskFailure(error.message);
    appendAssistantDelta(safeChatText(error.message));
    setMessage("chatMessage", error.message, "error");
    setChatBusy(false);
  }
}

function openTaskStream(slug, taskId) {
  const source = new EventSource(`/api/projects/${encodeURIComponent(slug)}/hastur/tasks/${encodeURIComponent(taskId)}/events`);
  state.activeEventSource = source;
  ["thought_delta", "assistant_delta", "task_breakdown", "task_progress", "user_prompt", "final", "error"].forEach((type) => {
    source.addEventListener(type, (event) => {
      const payload = parseTaskEvent(event, type);
      if (payload) handleTaskEvent(payload);
    });
  });
  source.onerror = () => {
    source.close();
    state.activeEventSource = null;
    if (!state.taskWaiting) setChatBusy(false);
  };
}

function parseTaskEvent(event, fallbackType) {
  if (!event || !event.data || event.data === "undefined") return null;
  try {
    return JSON.parse(event.data);
  } catch (error) {
    console.warn("Ignored malformed task event", fallbackType, error);
    return null;
  }
}

function handleTaskEvent(event) {
  const type = event.type || "status";
  const kind = type === "error" ? "error" : type === "final" ? "success" : "";
  if (type === "thought_delta") appendWorkLog(event.detail && event.detail.delta ? event.detail.delta : event.message || "", event);
  if (type === "thought_delta" && event.detail && event.detail.kind === "skill" && event.detail.skill_name) {
    const current = (state.taskProgress && Array.isArray(state.taskProgress.active_skills)) ? state.taskProgress.active_skills : [];
    const nextSkills = current.includes(event.detail.skill_name) ? current : [...current, event.detail.skill_name];
    renderTaskPanel({ active_skills: nextSkills }, event);
  }
  if (type === "assistant_delta") appendAssistantDelta(safeChatText(event.detail && event.detail.delta ? event.detail.delta : event.message || ""));
  if (type === "task_breakdown" || type === "task_progress") renderTaskPanel(event.detail || {}, event);
  if (!["thought_delta", "assistant_delta", "task_breakdown", "task_progress"].includes(type)) setMessage("chatMessage", event.message || "", kind);
  if (type === "user_prompt") {
    renderTaskPanel({ phase: event.state || "awaiting_user" }, event);
    if (state.activeEventSource) {
      state.activeEventSource.close();
      state.activeEventSource = null;
    }
    renderTaskModal(event);
  }
  if (type === "final") {
    renderTaskPanel({ phase: "complete" }, event);
    appendAssistantFinal(safeChatText(event.message || t("chat_done")));
  }
  if (type === "error") {
    renderTaskFailure(event.message || "Task failed.", event);
    appendAssistantError(safeChatText(event.message || t("task_failed_brief")));
  }
  if (type === "final") refreshChatGit();
  if (type === "final" || type === "error") {
    if (state.activeEventSource) state.activeEventSource.close();
    state.activeEventSource = null;
    finalizeAssistantMessage();
    state.activeTask = null;
    setChatBusy(false);
    closeTaskModal();
    $("chat_instruction").value = "";
    state.chatAttachments = [];
    renderChatAttachments();
  }
}

function renderTaskQuestion(event) {
  renderTaskModal(event);
}

async function resumeActiveTask(answer = "", confirmed = false, choiceId = "", revisionRequest = "") {
  if (!state.activeTask) return;
  const slug = $("hastur_project_slug").value;
  try {
    closeTaskModal();
    setChatBusy(true);
    startAssistantContinuation();
    await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/tasks/${encodeURIComponent(state.activeTask.task_id)}/resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer, confirmed, choice_id: choiceId, revision_request: revisionRequest }),
    });
    openTaskStream(slug, state.activeTask.task_id);
  } catch (error) {
    renderTaskFailure(error.message);
    appendAssistantDelta(safeChatText(error.message));
    setChatBusy(false);
  }
}

async function cancelActiveTask() {
  if (!state.activeTask) return;
  const slug = $("hastur_project_slug").value;
  const taskId = state.activeTask.task_id;
  if (state.activeEventSource) state.activeEventSource.close();
  state.activeEventSource = null;
  try {
    await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/tasks/${encodeURIComponent(taskId)}/cancel`, { method: "POST" });
    renderTaskFailure(t("task_cancelled"));
    appendAssistantError(t("task_cancelled"));
  } catch (error) {
    renderTaskFailure(error.message);
    appendAssistantError(safeChatText(error.message));
  }
  finalizeAssistantMessage();
  state.activeTask = null;
  closeTaskModal();
  setChatBusy(false);
}

function setChatBusy(busy) {
  const button = $("chat_send_button");
  const planButton = $("chat_plan_button");
  const stopButton = $("chat_stop_button");
  const input = $("chat_instruction");
  if (button) button.disabled = busy;
  if (planButton) planButton.disabled = busy;
  if (stopButton) stopButton.classList.toggle("hidden", !busy);
  if (input) input.disabled = busy;
}

function renderTaskModal(event) {
  const modal = $("task_modal");
  const body = $("task_modal_body");
  const title = $("task_modal_title");
  if (!modal || !body || !title) return;
  setChatBusy(false);
  state.taskWaiting = true;
  if ($("chat_send_button")) $("chat_send_button").disabled = true;
  if ($("chat_plan_button")) $("chat_plan_button").disabled = true;
  const detail = event.detail || {};
  title.textContent = detail.title || t("confirmation_needed");
  body.innerHTML = userPromptHTML(event, detail);
  bindTaskModalChoices(body);
  modal.classList.remove("hidden");
}

function userPromptHTML(event, detail) {
  const choices = Array.isArray(detail.choices) ? detail.choices : [];
  const inputRequired = Boolean(detail.requires_input);
  const fallbackInputLabel = state.language === "zh" ? "\u5176\u4ed6\u610f\u89c1\u6216\u81ea\u5b9a\u4e49\u65b9\u6848" : t("custom_reply");
  const inputLabel = choices.length ? fallbackInputLabel : (detail.input_label || fallbackInputLabel);
  const customButtonLabel = choices.length
    ? (state.language === "zh" ? "\u63d0\u4ea4\u81ea\u5b9a\u4e49\u65b9\u6848" : "Submit custom option")
    : t("answer_and_continue");
  return `
    <p>${escapeHTML(detail.body || event.message || "")}</p>
    ${choices.length ? `<div class="choice-list">
      ${choices.map((choice) => `<button type="button" class="choice-card" data-task-choice-id="${escapeAttr(choice.id || "")}"><strong>${escapeHTML(choice.label || choice.id || "")}</strong><span>${escapeHTML(choice.description || "")}</span></button>`).join("")}
    </div>` : ""}
    <div class="custom-reply-box">
      <label><span>${escapeHTML(inputLabel)}</span><textarea id="task_prompt_answer" rows="3" ${inputRequired ? "required" : ""}></textarea></label>
      <button type="button" class="secondary" onclick="resumePromptAnswer()">${escapeHTML(customButtonLabel)}</button>
    </div>`;
}

function bindTaskModalChoices(body) {
  body.querySelectorAll("[data-task-choice-id]").forEach((button) => {
    button.addEventListener("click", () => resumePromptChoice(button.dataset.taskChoiceId || ""));
  });
}

function resumePromptChoice(choiceId) {
  const answer = promptAnswerValue(false);
  if (answer === null) return;
  resumeActiveTask(answer, false, choiceId);
}

function resumePromptAnswer() {
  const answer = promptAnswerValue();
  if (answer === null) return;
  resumeActiveTask(answer, false);
}

function promptAnswerValue(validateRequired = true) {
  const input = $("task_prompt_answer");
  if (!input) return "";
  const answer = input.value || "";
  if (validateRequired && input.hasAttribute("required") && !answer.trim()) {
    if (typeof input.reportValidity === "function") input.reportValidity();
    input.focus();
    return null;
  }
  return answer;
}

function closeTaskModal() {
  const modal = $("task_modal");
  if (modal) modal.classList.add("hidden");
  state.taskWaiting = false;
}

function addChatMessage(role, text, detail = null, eventType = "") {
  const messages = $("chat_messages");
  const article = document.createElement("article");
  article.className = `chat-message ${role}`;
  const badge = eventType ? `<strong>${escapeHTML(eventType)}</strong><br>` : "";
  article.innerHTML = `<div>${badge}${escapeHTML(text || "")}</div>`;
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function createAssistantMessage() {
  const messages = $("chat_messages");
  const article = document.createElement("article");
  article.className = "chat-message assistant streaming";
  article.innerHTML = `<div class="assistant-text" data-placeholder="${escapeAttr(t("thinking_placeholder"))}"></div><div class="assistant-actions hidden"></div>`;
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return {
    article,
    text: article.querySelector(".assistant-text"),
    actions: article.querySelector(".assistant-actions"),
  };
}

function ensureAssistantMessage() {
  if (!state.activeAssistantMessage) state.activeAssistantMessage = createAssistantMessage();
  return state.activeAssistantMessage;
}

function startAssistantContinuation() {
  if (state.activeAssistantMessage) finalizeAssistantMessage();
  state.activeAssistantMessage = createAssistantMessage();
}

function beginTaskPanel(task) {
  state.taskError = "";
  state.workLog = [];
  state.taskProgress = {
    phase: "intake",
    instruction: task.instruction || "",
    workflow_mode: task.workflowMode || "auto",
    skill_name: task.skillName || "",
    complexity: "",
    execution_strategy: "",
    current_task_id: "",
    active_skills: [],
    tasks: [],
  };
  renderTaskPanel(state.taskProgress);
  renderWorkLog();
}

function renderTaskPanel(detail = {}, event = null) {
  const overview = $("task_overview");
  const list = $("task_list");
  const pill = $("task_state_pill");
  if (!overview || !list || !pill) return;

  const previous = state.taskProgress || {};
  const next = { ...previous, ...detail };
  if (Array.isArray(detail.tasks)) next.tasks = detail.tasks;
  if (!next.phase) next.phase = (event && event.state) || previous.phase || "idle";
  if (event && event.state && !detail.phase) next.phase = event.state;
  state.taskProgress = next;

  const phase = next.phase || "idle";
  pill.textContent = taskPhaseLabel(phase);
  pill.className = `status-pill ${taskPhaseKind(phase)}`.trim();

  const facts = [
    [t("task_phase"), taskPhaseLabel(phase)],
    [t("task_strategy"), next.execution_strategy || next.workflow_mode || "-"],
    [t("task_complexity"), next.complexity || "-"],
  ];
  if (Array.isArray(next.active_skills) && next.active_skills.length) {
    facts.push([state.language === "zh" ? "\u5df2\u8c03\u7528 Skills" : "Invoked skills", next.active_skills.map((name) => `/${name}`).join(", ")]);
  }
  overview.innerHTML = `
    <dl>
      ${facts.map(([key, value]) => `<dt>${escapeHTML(key)}</dt><dd>${escapeHTML(value)}</dd>`).join("")}
    </dl>
    ${next.instruction ? `<p class="muted-row">${escapeHTML(next.instruction)}</p>` : ""}`;

  const tasks = Array.isArray(next.tasks) ? next.tasks : [];
  if (!tasks.length) {
    list.innerHTML = "";
    if (phase === "idle") {
      overview.innerHTML = `<p class="muted-row">${escapeHTML(t("task_idle_note"))}</p>`;
    }
    renderTaskError();
    return;
  }

  const activeId = next.current_task_id || (tasks.find((task) => task.status === "active") || {}).id || "";
  const heading = tasks.length === 1
    ? (state.language === "zh" ? "\u5f53\u524d\u4efb\u52a1" : "Current task")
    : (state.language === "zh" ? "\u4efb\u52a1\u5217\u8868" : "Task list");
  list.innerHTML = `
    <div class="task-list-heading">${escapeHTML(heading)}</div>
    <ol>
      ${tasks.map((task, index) => {
        const status = task.status || "pending";
        const isActive = (task.id || "") === activeId || status === "active";
        const title = task.title || task.id || `Task ${index + 1}`;
        const goal = task.goal || "";
        return `<li class="task-item ${escapeAttr(status)}${isActive ? " active" : ""}">
          <span class="task-index">${index + 1}</span>
          <span class="task-copy"><strong>${escapeHTML(title)}</strong>${goal ? `<small>${escapeHTML(goal)}</small>` : ""}</span>
          <span class="task-status">${escapeHTML(taskStatusLabel(status, isActive))}</span>
        </li>`;
      }).join("")}
    </ol>`;
  renderTaskError();
}

function renderTaskError(message = "") {
  if (message) state.taskError = message;
  const node = $("task_error");
  if (!node) return;
  node.textContent = state.taskError || "";
  node.classList.toggle("hidden", !state.taskError);
}

function renderTaskFailure(message, event = null) {
  const clean = safeChatText(message || t("task_failed_brief"));
  renderTaskPanel({ phase: (event && event.state) || "failed" }, event);
  renderTaskError(clean);
}

function taskPhaseLabel(phase) {
  const labels = state.language === "zh"
    ? {
        idle: "\u7a7a\u95f2",
        intake: "\u63a5\u6536\u4efb\u52a1",
        context: "\u8bfb\u53d6\u4e0a\u4e0b\u6587",
        planning: "\u89c4\u5212\u4e2d",
        awaiting_user: "\u7b49\u5f85\u786e\u8ba4",
        executing: "\u6267\u884c\u4e2d",
        repairing: "\u4fee\u590d\u4e2d",
        verifying: "\u9a8c\u8bc1\u4e2d",
        complete: "\u5df2\u5b8c\u6210",
        failed: "\u5931\u8d25",
        cancelled: "\u5df2\u53d6\u6d88",
      }
    : {
        idle: "Idle",
        intake: "Starting",
        context: "Loading context",
        planning: "Planning",
        awaiting_user: "Waiting for input",
        executing: "Executing",
        repairing: "Repairing",
        verifying: "Verifying",
        complete: "Complete",
        failed: "Failed",
        cancelled: "Cancelled",
      };
  return labels[phase] || phase || t("idle");
}

function taskPhaseKind(phase) {
  if (phase === "complete") return "success";
  if (phase === "failed" || phase === "cancelled") return "error";
  if (phase && phase !== "idle") return "active";
  return "";
}

function taskStatusLabel(status, active) {
  if (active) return state.language === "zh" ? "\u6267\u884c\u4e2d" : "active";
  const labels = state.language === "zh"
    ? { pending: "\u5f85\u6267\u884c", completed: "\u5df2\u5b8c\u6210", failed: "\u5931\u8d25", skipped: "\u5df2\u8df3\u8fc7" }
    : { pending: "pending", completed: "done", failed: "failed", skipped: "skipped" };
  return labels[status] || status || "";
}

function appendWorkLog(delta, event = null) {
  const text = safeWorkLogText(delta);
  if (!text && !String(delta || "").trim()) return;
  const detail = event && event.detail ? event.detail : {};
  const kind = detail.kind || event?.type || "work";
  const phase = event?.state || "";
  const last = state.workLog[state.workLog.length - 1];
  if (last && last.kind === kind && last.phase === phase) {
    last.text += text;
  } else {
    state.workLog.push({ text: text.trimStart(), kind, phase });
  }
  state.workLog = state.workLog.slice(-40);
  renderWorkLog();
  if (event && event.state) renderTaskPanel({ phase: event.state }, event);
}

function renderWorkLog() {
  const node = $("task_work_log");
  if (!node) return;
  if (!state.workLog.length) {
    node.innerHTML = `<p class="muted-row">${escapeHTML(t("work_log_empty"))}</p>`;
    return;
  }
  node.innerHTML = state.workLog.map((entry) => `
    <div class="work-log-entry">
      <strong>${escapeHTML(taskPhaseLabel(entry.phase || entry.kind || "context"))}</strong>
      ${escapeHTML(entry.text)}
    </div>`).join("");
  node.scrollTop = node.scrollHeight;
}

function clearWorkLog() {
  state.workLog = [];
  renderWorkLog();
}

function safeWorkLogText(text) {
  return String(text || "").replace(/\r\n/g, "\n");
}

function safeChatText(text) {
  const value = String(text || "").replace(/\r\n/g, "\n").trim();
  if (!value) return "";
  if (/```|executeContext|EditorInterface|ProjectSettings|broker_response|gdscript|extends\s+RefCounted|func\s+execute/i.test(value)) {
    return t("task_failed_brief");
  }
  return value.length > 2400 ? `${value.slice(0, 2400).trim()}...` : value;
}

function appendAssistantDelta(delta) {
  if (!delta) return;
  const assistant = ensureAssistantMessage();
  assistant.text.textContent += delta;
  const messages = $("chat_messages");
  messages.scrollTop = messages.scrollHeight;
}

function appendAssistantThought(delta) {
  appendWorkLog(delta, { type: "thought_delta", state: "planning", detail: { kind: "work" } });
}

function appendAssistantFinal(text) {
  if (!text) return;
  const assistant = ensureAssistantMessage();
  assistant.text.textContent = text;
  const messages = $("chat_messages");
  messages.scrollTop = messages.scrollHeight;
}

function appendAssistantError(text) {
  if (!text) return;
  const assistant = ensureAssistantMessage();
  const current = assistant.text.textContent.trim();
  assistant.text.textContent = current ? `${current}\n\n${text}` : text;
  const messages = $("chat_messages");
  messages.scrollTop = messages.scrollHeight;
}

function assistantHasText() {
  return Boolean(state.activeAssistantMessage && state.activeAssistantMessage.text.textContent.trim());
}

function finalizeAssistantMessage() {
  if (!state.activeAssistantMessage) return;
  state.activeAssistantMessage.article.classList.remove("streaming");
  state.activeAssistantMessage = null;
}

function detectSkill(text) {
  const first = text.trim().split(/\s+/)[0] || "";
  if (first.startsWith("/")) {
    const skill = first.slice(1);
    if (state.skills.some((item) => item.name === skill && item.user_invocable !== false)) return skill;
  }
  return state.selectedSkill || "godot-remote-executor";
}

function renderSkillPicker(filter = "") {
  const picker = $("skill_picker");
  if (!picker) return;
  const needle = filter.replace(/^\//, "").toLowerCase();
  const skills = state.skills.filter((skill) => skill.user_invocable !== false && (!needle || skill.name.toLowerCase().includes(needle))).slice(0, 8);
  picker.innerHTML = skills.map((skill) => `<button type="button" onclick="chooseSkill('${escapeAttr(skill.name)}')"><strong>/${escapeHTML(skill.name)}</strong><span>${escapeHTML(skill.description || "")}</span></button>`).join("");
  picker.classList.toggle("hidden", !filter.startsWith("/") || !skills.length);
}

function chooseSkill(name) {
  state.selectedSkill = name;
  const input = $("chat_instruction");
  const text = input.value.trim();
  input.value = text.startsWith("/") ? `/${name} ` : `/${name} ${text}`;
  $("skill_picker").classList.add("hidden");
  input.focus();
}

async function readSelectedFiles(files) {
  const items = [];
  for (const file of Array.from(files || [])) {
    const dataUrl = await readAsDataURL(file);
    const comma = dataUrl.indexOf(",");
    const data = comma >= 0 ? dataUrl.slice(comma + 1) : dataUrl;
    items.push({ filename: file.name, media_type: file.type || "application/octet-stream", data, preview: await previewFile(file) });
  }
  return items;
}

function previewFile(file) {
  return new Promise((resolve) => {
    if (!(file.type.startsWith("text/") || /\.(txt|md|json|csv|gd|tscn)$/i.test(file.name))) {
      resolve("");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || "").slice(0, 800));
    reader.onerror = () => resolve("");
    reader.readAsText(file);
  });
}

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error("Could not read file"));
    reader.readAsDataURL(file);
  });
}

function renderChatAttachments() {
  const list = $("chat_attachment_list");
  if (!list) return;
  list.innerHTML = state.chatAttachments.map((file, index) => `<span>${escapeHTML(file.filename)} <button type="button" onclick="removeChatAttachment(${index})">x</button></span>`).join("");
}

function removeChatAttachment(index) {
  state.chatAttachments.splice(index, 1);
  renderChatAttachments();
}

function renderMiniOutput(id, data) {
  const node = $(id);
  if (!node) return;
  node.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

function renderBrokerStatus(status, message = "") {
  state.lastBrokerStatus = status;
  state.lastBrokerMessage = message;
  const node = $("broker_output");
  if (!node) return;
  const runningLabel = status.managed_running ? t("broker_managed") : status.external_running ? t("broker_external") : t("broker_stopped");
  const tokenLabel = status.token_state || (status.has_auth_token ? "ready" : "missing");
  const executors = status.executors || [];
  node.innerHTML = `
    <div class="broker-status-card">
      <div class="broker-status-head">
        <strong>${escapeHTML(runningLabel)}</strong>
        <span class="status-pill ${status.running ? "success" : "error"}">${escapeHTML(status.running ? t("broker_running") : t("broker_state_stopped"))}</span>
      </div>
      <p>${escapeHTML(message || status.message || "")}</p>
      <div class="broker-facts">
        <span>${escapeHTML(t("broker_http"))}: ${escapeHTML(status.http_available ? t("broker_reachable") : t("broker_unreachable"))}</span>
        <span>${escapeHTML(t("broker_token"))}: ${escapeHTML(tokenLabel)}</span>
        <span>${escapeHTML(t("broker_executors"))}: ${escapeHTML(String(status.executor_count || executors.length || 0))}</span>
        <span>HTTP ${escapeHTML(status.base_url || `http://${status.host || "localhost"}:${status.http_port || 5302}`)}</span>
        <span>TCP ${escapeHTML(status.host || "localhost")}:${escapeHTML(status.tcp_port || 5301)}</span>
        ${status.pid ? `<span>PID ${escapeHTML(status.pid)}</span>` : ""}
      </div>
      ${status.external_running ? `<p class="muted-row">${escapeHTML(t("external_broker_note"))}</p>` : ""}
      ${executors.length ? `<div class="executor-list">${executors.map((executor) => `<div><strong>${escapeHTML(executor.project_name || executor.id || "executor")}</strong><span>${escapeHTML(executor.project_path || executor.status || "")}</span></div>`).join("")}</div>` : ""}
    </div>`;
}

function escapeHTML(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttr(value) {
  return escapeHTML(value).replace(/`/g, "&#096;");
}

window.addEventListener("DOMContentLoaded", () => {
  setLanguage(state.language);
  showView(state.view);
  $("asset_project_slug").addEventListener("change", loadAssetsForSelectedProject);
  $("skill_scope").addEventListener("change", loadSkills);
  $("skill_project_slug").addEventListener("change", () => {
    state.skillProject = $("skill_project_slug").value;
    localStorage.setItem("skillProject", state.skillProject);
    loadSkills();
  });
  $("hastur_project_slug").addEventListener("change", () => {
    state.selectedProject = $("hastur_project_slug").value;
    localStorage.setItem("selectedProject", state.selectedProject);
    refreshChatGit();
  });
  $("chat_instruction").addEventListener("input", () => renderSkillPicker($("chat_instruction").value.trim().split(/\s+/)[0] || ""));
  $("chat_instruction").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      sendHasturChat();
    }
  });
  $("chat_files").addEventListener("change", async () => {
    state.chatAttachments.push(...(await readSelectedFiles($("chat_files").files)));
    $("chat_files").value = "";
    renderChatAttachments();
  });
  $("asset_files").addEventListener("change", renderAssetFileLabel);
  $("skill_files").addEventListener("change", renderSkillFileLabel);
  loadSettings();
  loadProjects();
  loadSkills();
  loadBrokerStatus();
});
