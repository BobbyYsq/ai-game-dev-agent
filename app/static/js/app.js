const translations = {
  en: {
    eyebrow: "Godot control plane",
    app_title: "AI Game Development Agent",
    header_note: "Create Hastur-enabled Godot projects, chat with vendored skills, generate references, and review local Git changes.",
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
    saving_settings: "Saving settings...",
    settings_saved: "Settings saved.",
    testing_connection: "Testing connection...",
    connection_ok: "Connection test succeeded.",
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
    workbench_note: "Select a generated project, inspect its files, and run a local Codex/OpenCode-style Git review loop.",
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
    hastur_config_title: "Hastur Broker",
    hastur_config_note: "Start the local broker, keep the token private, and check whether Godot executors are connected.",
    start_broker: "Start Broker",
    stop_broker: "Stop Broker",
    broker_status: "Status",
    broker_logs: "Logs",
    load_executors: "Executors",
    chat_title: "LLM + Hastur Chat",
    chat_note: "Use one input. Type `/` to choose a vendored Hastur skill; token and broker URL stay private.",
    hastur_project: "Project",
    chat_placeholder: "/godot-remote-executor Add a Label node to Main.tscn and save the scene.",
    send_to_llm: "Send",
    chat_required: "Select a project and enter a message.",
    sending_chat: "Sending...",
    chat_done: "Response received.",
    confirmation_needed: "Confirmation required before execution.",
    confirm_execute: "Confirm and execute",
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
    saving_settings: "正在保存设置...",
    settings_saved: "设置已保存。",
    testing_connection: "正在测试连接...",
    connection_ok: "连接测试成功。",
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
    workbench_note: "选择已生成项目，查看文件，并按 Codex/OpenCode 风格完成本地 Git 审查流程。",
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
    hastur_config_title: "Hastur Broker",
    hastur_config_note: "启动本地 broker，私下保存 token，并检查 Godot executor 是否连接。",
    start_broker: "启动 Broker",
    stop_broker: "停止 Broker",
    broker_status: "状态",
    broker_logs: "日志",
    load_executors: "Executors",
    chat_title: "LLM + Hastur 聊天",
    chat_note: "只使用一个输入框。输入 `/` 选择内置 Hastur skill；token 与 broker URL 不会暴露。",
    hastur_project: "项目",
    chat_placeholder: "/godot-remote-executor 给 Main.tscn 添加一个 Label 节点并保存场景。",
    send_to_llm: "发送",
    chat_required: "请选择项目并输入消息。",
    sending_chat: "正在发送...",
    chat_done: "已收到响应。",
    confirmation_needed: "执行前需要确认。",
    confirm_execute: "确认并执行",
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
    asset_prompt_placeholder: "适合黑暗幻想 Godot 原型的清晰俯视概念图。",
    asset_uploads: "参考文件与图片",
    save_asset_settings: "保存图像默认值",
    generate_image: "生成图像",
    asset_project_required: "请选择项目并输入图像提示词。",
    generating_image: "正在生成图像...",
    image_generated: "图像已生成。",
    no_assets: "还没有生成图像资产。",
    attach_gdd: "批准到 GDD",
    mark_blender: "标记 Blender 参考",
    regenerate: "重新生成",
    asset_updated: "资产已更新。",
    file_path: "文件路径",
    status: "状态",
    project_path: "项目路径",
    generated_files: "生成文件",
  },
};

const state = {
  language: localStorage.getItem("language") || "en",
  view: localStorage.getItem("view") || "manage",
  projects: [],
  selectedProject: localStorage.getItem("selectedProject") || "",
  assets: [],
  skills: [],
  selectedSkill: "godot-remote-executor",
  chatAttachments: [],
  pendingChat: null,
};

function $(id) {
  return document.getElementById(id);
}

function t(key) {
  return translations[state.language][key] || translations.en[key] || key;
}

function setLanguage(language) {
  state.language = language;
  localStorage.setItem("language", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  applyTranslations();
  renderProjects();
  renderAssetGallery();
  renderChatAttachments();
}

function showView(view) {
  state.view = view;
  localStorage.setItem("view", view);
  ["manage", "hastur", "images"].forEach((name) => {
    $(`view${capitalize(name)}`).classList.toggle("active", name === view);
    $(`tab${capitalize(name)}`).classList.toggle("active", name === view);
  });
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
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

function setConnectionStatus(text, kind = "") {
  $("connectionStatus").textContent = text;
  $("connectionStatus").className = `status-pill ${kind}`.trim();
}

function setMessage(id, text, kind = "") {
  const node = $(id);
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
    $("hasturTokenStatus").textContent = data.has_hastur_auth_token ? "token: ready" : "token: missing";
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
    setMessage("projectMessage", t("godot_project_created"), "success");
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
    if (!state.selectedProject && state.projects.length) {
      state.selectedProject = state.projects[0].slug;
    }
    renderProjects();
    renderProjectSelectors();
    if (state.selectedProject) {
      await showProjectDetails(state.selectedProject);
    }
  } catch (error) {
    $("recent_projects").innerHTML = `<li class="error-row">${escapeHTML(error.message)}</li>`;
  }
}

function renderProjectSelectors() {
  const selects = [$("asset_project_slug"), $("hastur_project_slug")];
  selects.forEach((select) => {
    const selected = select.value || state.selectedProject;
    select.innerHTML = state.projects
      .map((project) => `<option value="${escapeAttr(project.slug)}">${escapeHTML(project.slug)}</option>`)
      .join("");
    if (!state.projects.length) {
      select.innerHTML = `<option value="">${escapeHTML(t("no_projects"))}</option>`;
    } else {
      select.value = selected && state.projects.some((project) => project.slug === selected) ? selected : state.projects[0].slug;
    }
  });
  if (state.projects.length) {
    loadAssetsForSelectedProject();
  }
}

function renderProjects() {
  const list = $("recent_projects");
  if (!state.projects.length) {
    list.innerHTML = `<li class="muted-row">${escapeHTML(t("no_projects"))}</li>`;
    $("project_detail_pane").innerHTML = `<p class="muted-row">${escapeHTML(t("select_project_hint"))}</p>`;
    return;
  }
  list.innerHTML = state.projects
    .map((project) => {
      const active = project.slug === state.selectedProject ? "active" : "";
      return `
        <li>
          <button type="button" class="project-card ${active}" onclick="selectProject('${escapeAttr(project.slug)}')">
            <strong>${escapeHTML(project.slug)}</strong>
            <span title="${escapeAttr(project.path)}">${escapeHTML(project.path)}</span>
          </button>
        </li>
      `;
    })
    .join("");
}

async function selectProject(slug) {
  state.selectedProject = slug;
  localStorage.setItem("selectedProject", slug);
  renderProjects();
  renderProjectSelectors();
  await showProjectDetails(slug);
}

function selectedProject() {
  return state.projects.find((project) => project.slug === state.selectedProject);
}

async function showProjectDetails(slug) {
  try {
    const details = await requestJSON(`/api/projects/${encodeURIComponent(slug)}`);
    $("project_detail_pane").innerHTML = `
      <div class="detail-header">
        <div>
          <h3>${escapeHTML(details.slug)}</h3>
          <p>${escapeHTML(details.path)}</p>
        </div>
        <div class="segmented-actions">
          <button type="button" onclick="showProjectDetails('${escapeAttr(slug)}')">${escapeHTML(t("open_details"))}</button>
          <button type="button" onclick="reviewProjectChanges('${escapeAttr(slug)}')">${escapeHTML(t("review_changes"))}</button>
          <button type="button" onclick="renderCommitPane('${escapeAttr(slug)}')">${escapeHTML(t("commit_changes"))}</button>
          <button type="button" onclick="showGitHistory('${escapeAttr(slug)}')">${escapeHTML(t("history"))}</button>
          <button type="button" onclick="renderRestorePane('${escapeAttr(slug)}')">${escapeHTML(t("restore"))}</button>
        </div>
      </div>
      ${projectSummaryHTML({ project_slug: details.slug, project_path: details.path, generated_files: details.files || [] })}
    `;
  } catch (error) {
    renderProjectError(error.message);
  }
}

async function reviewProjectChanges(slug) {
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/review`);
    const status = data.status || {};
    const files = status.files || [];
    $("project_detail_pane").innerHTML = projectActionShell(slug, `
      <div class="status-strip">
        <span>${escapeHTML(t("branch"))}: ${escapeHTML(status.branch || "-")}</span>
        <span>${escapeHTML(status.dirty ? t("dirty") : t("clean"))}</span>
      </div>
      <h4>${escapeHTML(t("files"))}</h4>
      ${files.length ? `<ul class="file-list">${files.map((file) => `<li><code>${escapeHTML(file.status)}</code> ${escapeHTML(file.path)}</li>`).join("")}</ul>` : `<p class="muted-row">${escapeHTML(t("clean"))}</p>`}
      <h4>${escapeHTML(t("diff"))}</h4>
      <pre>${escapeHTML((data.diff && (data.diff.stat || data.diff.diff)) || "")}</pre>
    `);
  } catch (error) {
    renderProjectError(error.message);
  }
}

function renderCommitPane(slug) {
  $("project_detail_pane").innerHTML = projectActionShell(slug, `
    <label>
      <span>${escapeHTML(t("commit_message"))}</span>
      <input id="commit_message" autocomplete="off" placeholder="${escapeAttr(t("commit_placeholder"))}">
    </label>
    <button type="button" onclick="commitProject('${escapeAttr(slug)}')">${escapeHTML(t("commit_now"))}</button>
    <div id="git_action_output" class="inline-result"></div>
  `);
}

async function commitProject(slug) {
  const message = $("commit_message").value.trim();
  if (!message) return;
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/commit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    $("git_action_output").innerHTML = gitResultHTML(data);
  } catch (error) {
    $("git_action_output").innerHTML = `<p class="error-text">${escapeHTML(error.message)}</p>`;
  }
}

async function showGitHistory(slug) {
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/log`);
    const commits = data.commits || [];
    $("project_detail_pane").innerHTML = projectActionShell(slug, `
      <div class="commit-list">
        ${commits.length ? commits.map((commit) => `
          <article>
            <strong>${escapeHTML(commit.short_hash)} ${escapeHTML(commit.subject)}</strong>
            <span>${escapeHTML(commit.date)} ${escapeHTML(commit.author)}</span>
            <button type="button" class="secondary compact" onclick="renderRestorePane('${escapeAttr(slug)}', '${escapeAttr(commit.hash)}')">${escapeHTML(t("restore"))}</button>
          </article>
        `).join("") : `<p class="muted-row">No commits.</p>`}
      </div>
    `);
  } catch (error) {
    renderProjectError(error.message);
  }
}

function renderRestorePane(slug, hash = "") {
  $("project_detail_pane").innerHTML = projectActionShell(slug, `
    <label>
      <span>${escapeHTML(t("restore_hash"))}</span>
      <input id="restore_hash" autocomplete="off" value="${escapeAttr(hash)}">
    </label>
    <div class="button-row">
      <button type="button" onclick="previewRollback('${escapeAttr(slug)}')">${escapeHTML(t("preview_restore"))}</button>
      <button type="button" class="secondary" id="confirm_restore_btn" onclick="confirmRollback('${escapeAttr(slug)}')" disabled>${escapeHTML(t("confirm_restore"))}</button>
    </div>
    <div id="git_action_output" class="inline-result"></div>
  `);
}

async function previewRollback(slug) {
  const commitHash = $("restore_hash").value.trim();
  if (!commitHash) return;
  try {
    const preview = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/rollback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commit_hash: commitHash, confirm: false }),
    });
    $("confirm_restore_btn").disabled = !preview.requires_confirmation;
    $("git_action_output").innerHTML = gitResultHTML(preview);
  } catch (error) {
    $("git_action_output").innerHTML = `<p class="error-text">${escapeHTML(error.message)}</p>`;
  }
}

async function confirmRollback(slug) {
  const commitHash = $("restore_hash").value.trim();
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/git/rollback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commit_hash: commitHash, confirm: true }),
    });
    $("git_action_output").innerHTML = gitResultHTML(data);
  } catch (error) {
    $("git_action_output").innerHTML = `<p class="error-text">${escapeHTML(error.message)}</p>`;
  }
}

function projectActionShell(slug, inner) {
  const project = selectedProject();
  return `
    <div class="detail-header">
      <div>
        <h3>${escapeHTML(slug)}</h3>
        <p>${escapeHTML(project ? project.path : "")}</p>
      </div>
      <div class="segmented-actions">
        <button type="button" onclick="showProjectDetails('${escapeAttr(slug)}')">${escapeHTML(t("open_details"))}</button>
        <button type="button" onclick="reviewProjectChanges('${escapeAttr(slug)}')">${escapeHTML(t("review_changes"))}</button>
        <button type="button" onclick="renderCommitPane('${escapeAttr(slug)}')">${escapeHTML(t("commit_changes"))}</button>
        <button type="button" onclick="showGitHistory('${escapeAttr(slug)}')">${escapeHTML(t("history"))}</button>
        <button type="button" onclick="renderRestorePane('${escapeAttr(slug)}')">${escapeHTML(t("restore"))}</button>
      </div>
    </div>
    ${inner}
  `;
}

function renderProjectError(message) {
  $("project_detail_pane").innerHTML = `<p class="error-text">${escapeHTML(message)}</p>`;
}

function projectSummaryHTML(result) {
  const files = result.generated_files || [];
  return `
    <dl>
      <dt>${escapeHTML(t("project_path"))}</dt>
      <dd>${escapeHTML(result.project_path || "")}</dd>
    </dl>
    ${files.length ? `<h4>${escapeHTML(t("generated_files"))}</h4><ul class="file-list">${files.map((file) => `<li>${escapeHTML(file)}</li>`).join("")}</ul>` : ""}
  `;
}

function gitResultHTML(data) {
  return `<pre>${escapeHTML(JSON.stringify(data, null, 2))}</pre>`;
}

async function saveAssetSettings() {
  setMessage("assetMessage", t("saving_settings"));
  try {
    await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_size: $("image_size").value,
        image_quality: $("image_quality").value,
      }),
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
  gallery.innerHTML = state.assets
    .map(
      (asset) => `
        <article class="asset-card">
          <img src="/api/projects/${encodeURIComponent(slug)}/assets/${encodeURIComponent(asset.id)}/file" alt="${escapeAttr(asset.purpose)}">
          <div>
            <strong>${escapeHTML(asset.id)} - ${escapeHTML(asset.purpose)}</strong>
            <span>${escapeHTML(asset.model || "")}</span>
            <p>${escapeHTML(asset.prompt || "")}</p>
            <p><b>${escapeHTML(t("file_path"))}:</b> ${escapeHTML(asset.path || "")}</p>
            <div class="button-row">
              <button type="button" class="secondary compact" onclick="updateAsset('/attach-to-gdd', '${escapeAttr(asset.id)}')">${escapeHTML(t("attach_gdd"))}</button>
              <button type="button" class="secondary compact" onclick="updateAsset('/mark-blender-reference', '${escapeAttr(asset.id)}')">${escapeHTML(t("mark_blender"))}</button>
              <button type="button" class="secondary compact" onclick="regenerateAsset('${escapeAttr(asset.id)}')">${escapeHTML(t("regenerate"))}</button>
            </div>
          </div>
        </article>
      `,
    )
    .join("");
}

async function loadSkills() {
  try {
    const data = await requestJSON("/api/hastur/skills");
    state.skills = data.skills || [];
    const preferred = state.skills.find((skill) => skill.name === "godot-remote-executor") || state.skills[0];
    state.selectedSkill = preferred ? preferred.name : "godot-remote-executor";
    renderSkillPicker();
  } catch (error) {
    setMessage("chatMessage", error.message, "error");
  }
}

async function startBroker() {
  setMessage("hasturMessage", t("loading"));
  try {
    const data = await requestJSON("/api/hastur/broker/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    renderMiniOutput("broker_output", data);
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
    renderMiniOutput("broker_output", data);
    setMessage("hasturMessage", data.message, data.success ? "success" : "error");
    await loadSettings();
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function loadBrokerStatus() {
  try {
    const data = await requestJSON("/api/hastur/broker/status");
    renderMiniOutput("broker_output", data);
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
    if (state.view === "hastur") {
      addChatMessage("assistant", data.available ? "Executors loaded." : data.message || "No executor available.", data);
    } else {
      renderMiniOutput("broker_output", data);
    }
    updateChatReadiness(null, data);
  } catch (error) {
    setMessage(state.view === "hastur" ? "chatMessage" : "hasturMessage", error.message, "error");
  }
}

function updateChatReadiness(status = null, executors = null) {
  const pill = $("chatReadiness");
  if (!pill) return;
  if (executors && !executors.available) {
    pill.textContent = "executor missing";
    pill.className = "status-pill error";
    return;
  }
  if (status && !status.running) {
    pill.textContent = "broker stopped";
    pill.className = "status-pill error";
    return;
  }
  pill.textContent = t("ready");
  pill.className = "status-pill success";
}

function triggerChatFiles() {
  $("chat_files").click();
}

async function sendHasturChat(confirmed = false) {
  const slug = $("hastur_project_slug").value;
  const instruction = $("chat_instruction").value.trim();
  if (!slug || !instruction) {
    setMessage("chatMessage", t("chat_required"), "error");
    return;
  }
  const skillName = detectSkill(instruction);
  setMessage("chatMessage", t("sending_chat"));
  if (!confirmed) {
    addChatMessage("user", instruction, state.chatAttachments);
  }
  try {
    const payload = {
      instruction,
      skill_name: skillName,
      execute: true,
      confirmed,
      attachments: state.chatAttachments,
    };
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.pendingChat = data.requires_confirmation && !confirmed ? payload : null;
    addChatMessage("assistant", data.message || t("chat_done"), data);
    setMessage("chatMessage", data.message || t("chat_done"), data.success ? "success" : "error");
    if (!data.requires_confirmation) {
      $("chat_instruction").value = "";
      state.chatAttachments = [];
      renderChatAttachments();
    }
  } catch (error) {
    addChatMessage("assistant", error.message);
    setMessage("chatMessage", error.message, "error");
  }
}

async function confirmPendingChat() {
  if (!state.pendingChat) return;
  $("chat_instruction").value = state.pendingChat.instruction;
  await sendHasturChat(true);
  state.pendingChat = null;
}

function addChatMessage(role, text, detail = null) {
  const messages = $("chat_messages");
  const article = document.createElement("article");
  article.className = `chat-message ${role}`;
  const confirmation = detail && detail.requires_confirmation && !detail.success ? `<button type="button" onclick="confirmPendingChat()">${escapeHTML(t("confirm_execute"))}</button>` : "";
  article.innerHTML = `
    <div>${escapeHTML(text || "")}</div>
    ${confirmation}
    ${detail ? `<details><summary>${escapeHTML(t("technical_details"))}</summary><pre>${escapeHTML(JSON.stringify(detail, null, 2))}</pre></details>` : ""}
  `;
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function detectSkill(text) {
  const first = text.trim().split(/\s+/)[0] || "";
  if (first.startsWith("/")) {
    const skill = first.slice(1);
    if (state.skills.some((item) => item.name === skill)) return skill;
  }
  return state.selectedSkill || "godot-remote-executor";
}

function renderSkillPicker(filter = "") {
  const picker = $("skill_picker");
  if (!picker) return;
  const needle = filter.replace(/^\//, "").toLowerCase();
  const skills = state.skills.filter((skill) => !needle || skill.name.toLowerCase().includes(needle)).slice(0, 8);
  picker.innerHTML = skills
    .map((skill) => `<button type="button" onclick="chooseSkill('${escapeAttr(skill.name)}')"><strong>/${escapeHTML(skill.name)}</strong><span>${escapeHTML(skill.description || "")}</span></button>`)
    .join("");
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
    items.push({
      filename: file.name,
      media_type: file.type || "application/octet-stream",
      data,
      preview: await previewFile(file),
    });
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
  list.innerHTML = state.chatAttachments
    .map((file, index) => `<span>${escapeHTML(file.filename)} <button type="button" onclick="removeChatAttachment(${index})">x</button></span>`)
    .join("");
}

function removeChatAttachment(index) {
  state.chatAttachments.splice(index, 1);
  renderChatAttachments();
}

function renderMiniOutput(id, data) {
  $(id).textContent = JSON.stringify(data, null, 2);
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
  $("hastur_project_slug").addEventListener("change", () => {
    state.selectedProject = $("hastur_project_slug").value;
  });
  $("chat_instruction").addEventListener("input", () => {
    renderSkillPicker($("chat_instruction").value.trim().split(/\s+/)[0] || "");
  });
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
  loadSettings();
  loadProjects();
  loadSkills();
  loadBrokerStatus();
});
