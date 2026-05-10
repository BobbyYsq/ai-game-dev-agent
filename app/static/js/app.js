const translations = {
  en: {
    eyebrow: "Godot prototype workflow",
    header_note: "Startup only opens the agent dashboard. Projects are created only when you submit this form.",
    loading: "Loading",
    ready: "Ready",
    settings_error: "Settings error",
    settings_title: "Settings",
    checking_key: "Checking key",
    key_configured: "API key configured",
    key_missing: "API key not configured",
    llm_provider: "LLM Provider",
    openai_model: "OpenAI Model",
    openai_key: "OpenAI API Key",
    save_settings: "Save Settings",
    test_connection: "Test Connection",
    saving_settings: "Saving settings...",
    settings_saved: "Settings saved.",
    testing_connection: "Testing connection...",
    connection_ok: "Connection test succeeded.",
    create_project: "Create Project",
    templates_badge: "v0.2.1 templates",
    project_note: "This form starts the AI workflow: LLM planning and docs, then Godot project generation. Hastur/Godot editor bridge can be added as the next backend.",
    project_name: "Project Name",
    project_name_placeholder: "Example: Shadow Garden",
    game_idea: "Game Idea / GDD",
    game_idea_placeholder: "Describe the game you want the AI agent to build...",
    generation_pipeline: "Generation Pipeline",
    pipeline_llm_godot: "LLM + Godot file generator",
    pipeline_hastur: "Hastur / Godot editor bridge (planned)",
    godot_template: "Godot Project Template",
    template_2d: "2D Game Prototype",
    template_3d: "3D Game Prototype",
    game_type: "Game Type",
    engine_version: "Engine Version",
    prototype_scope: "Prototype Scope",
    scope_vertical: "vertical slice",
    scope_mechanics: "mechanics prototype",
    scope_demo: "playable demo",
    enable_git: "Enable Git",
    generate_docs: "Generate Documentation",
    generate_godot: "Generate Godot Prototype",
    create_button: "Run AI Project Generation",
    project_required: "Project name and game idea are required.",
    creating_project: "Creating project...",
    project_working: "The agent is generating docs, Godot files, and a review report.",
    project_created: "Project created.",
    recent_projects: "Recent Projects",
    recent_note: "These are existing generated projects. Startup does not create new projects.",
    refresh: "Refresh",
    details: "Details",
    no_projects: "No generated projects yet.",
    output: "Output",
    output_badge: "Generation result and errors",
    output_empty: "No project created yet.",
    status: "Status",
    project_slug: "Project slug",
    template: "Template",
    project_path: "Project path",
    review_summary: "Review summary",
    next_steps: "Next steps",
    generated_files: "Generated files",
  },
  zh: {
    eyebrow: "Godot 原型工作流",
    header_note: "启动脚本只打开 Agent 控制台。只有提交这个表单时，系统才会创建项目。",
    loading: "加载中",
    ready: "就绪",
    settings_error: "设置错误",
    settings_title: "设置",
    checking_key: "正在检查密钥",
    key_configured: "API Key 已配置",
    key_missing: "API Key 未配置",
    llm_provider: "LLM 提供方",
    openai_model: "OpenAI 模型",
    openai_key: "OpenAI API Key",
    save_settings: "保存设置",
    test_connection: "测试连接",
    saving_settings: "正在保存设置...",
    settings_saved: "设置已保存。",
    testing_connection: "正在测试连接...",
    connection_ok: "连接测试成功。",
    create_project: "创建项目",
    templates_badge: "v0.2.1 模板",
    project_note: "这个表单用于启动 AI 工作流：先调用 LLM 规划和生成文档，再生成 Godot 项目。Hastur/Godot 编辑器桥接会作为后续后端接入。",
    project_name: "项目名称",
    project_name_placeholder: "例如：Shadow Garden",
    game_idea: "游戏需求 / GDD",
    game_idea_placeholder: "描述你希望 AI Agent 构建的游戏...",
    generation_pipeline: "生成管线",
    pipeline_llm_godot: "LLM + Godot 文件生成器",
    pipeline_hastur: "Hastur / Godot 编辑器桥接（计划中）",
    godot_template: "Godot 项目模板",
    template_2d: "2D 游戏原型",
    template_3d: "3D 游戏原型",
    game_type: "游戏类型",
    engine_version: "引擎版本",
    prototype_scope: "原型范围",
    scope_vertical: "垂直切片",
    scope_mechanics: "机制原型",
    scope_demo: "可玩 Demo",
    enable_git: "启用 Git",
    generate_docs: "生成文档",
    generate_godot: "生成 Godot 原型",
    create_button: "运行 AI 项目生成",
    project_required: "项目名称和游戏需求不能为空。",
    creating_project: "正在创建项目...",
    project_working: "Agent 正在生成文档、Godot 文件和评审报告。",
    project_created: "项目已创建。",
    recent_projects: "最近项目",
    recent_note: "这里显示已经生成过的项目。启动程序不会自动创建新项目。",
    refresh: "刷新",
    details: "详情",
    no_projects: "还没有生成项目。",
    output: "输出",
    output_badge: "生成结果和错误",
    output_empty: "还没有创建项目。",
    status: "状态",
    project_slug: "项目 slug",
    template: "模板",
    project_path: "项目路径",
    review_summary: "评审摘要",
    next_steps: "下一步",
    generated_files: "生成文件",
  },
};

const state = {
  language: localStorage.getItem("language") || "en",
  projects: [],
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
  if ($("output").dataset.renderState) {
    renderOutput(JSON.parse($("output").dataset.renderState));
  }
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  $("langEn").classList.toggle("active", state.language === "en");
  $("langZh").classList.toggle("active", state.language === "zh");
}

function setMessage(id, text, type = "info") {
  const el = $(id);
  el.textContent = text || "";
  el.className = `message ${type}`;
}

function setConnectionStatus(text, type = "info") {
  const el = $("connectionStatus");
  el.textContent = text;
  el.className = `status-pill ${type}`;
}

async function requestJSON(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || response.statusText || "Request failed";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

function ensureSelectValue(select, value) {
  if (!value) {
    return;
  }
  const exists = Array.from(select.options).some((option) => option.value === value);
  if (!exists) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }
  select.value = value;
}

async function loadSettings() {
  try {
    const data = await requestJSON("/api/settings");
    $("provider").value = data.llm_provider;
    ensureSelectValue($("model"), data.openai_model);
    $("apiKeyStatus").textContent = data.has_openai_api_key ? t("key_configured") : t("key_missing");
    setConnectionStatus(t("ready"), "success");
  } catch (error) {
    setConnectionStatus(t("settings_error"), "error");
    setMessage("settingsMessage", error.message, "error");
  }
}

async function saveSettings() {
  setMessage("settingsMessage", t("saving_settings"));
  const body = {
    llm_provider: $("provider").value,
    openai_model: $("model").value,
    openai_api_key: $("apiKey").value,
  };

  try {
    const result = await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    $("apiKey").value = "";
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

function buildProjectPayload() {
  return {
    project_name: $("project_name").value.trim(),
    game_idea: $("game_idea").value.trim(),
    project_template: $("project_template").value,
    game_type: $("game_type").value.trim(),
    engine: $("engine").value,
    prototype_scope: $("prototype_scope").value,
    enable_git: $("enable_git").checked,
    generate_docs: $("generate_docs").checked,
    generate_godot_skeleton: $("generate_godot_skeleton").checked,
  };
}

async function createProject() {
  const payload = buildProjectPayload();
  if (!payload.project_name || !payload.game_idea) {
    setMessage("projectMessage", t("project_required"), "error");
    return;
  }

  setMessage("projectMessage", t("creating_project"));
  renderOutput({ status: "working", message: t("project_working") });

  try {
    const result = await requestJSON("/api/projects/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setMessage("projectMessage", t("project_created"), "success");
    renderProjectResult(result);
    await loadProjects();
  } catch (error) {
    setMessage("projectMessage", error.message, "error");
    renderOutput({ status: "error", message: error.message });
  }
}

async function loadProjects() {
  try {
    const data = await requestJSON("/api/projects");
    state.projects = data.projects || [];
    renderProjects();
  } catch (error) {
    $("recent_projects").innerHTML = `<li class="error-row">${escapeHTML(error.message)}</li>`;
  }
}

async function showProjectDetails(slug) {
  try {
    const details = await requestJSON(`/api/projects/${encodeURIComponent(slug)}`);
    renderOutput({
      status: "details",
      slug: details.slug,
      path: details.path,
      generated_files: details.files,
    });
  } catch (error) {
    renderOutput({ status: "error", message: error.message });
  }
}

function renderProjects() {
  const list = $("recent_projects");
  if (!state.projects.length) {
    list.innerHTML = `<li class="muted-row">${escapeHTML(t("no_projects"))}</li>`;
    return;
  }

  list.innerHTML = state.projects
    .map(
      (project) => `
        <li>
          <div>
            <strong>${escapeHTML(project.slug)}</strong>
            <span title="${escapeAttr(project.path)}">${escapeHTML(project.path)}</span>
          </div>
          <button type="button" class="secondary compact" onclick="showProjectDetails('${escapeAttr(project.slug)}')">${escapeHTML(t("details"))}</button>
        </li>
      `,
    )
    .join("");
}

function renderProjectResult(result) {
  renderOutput({
    status: "success",
    project_slug: result.project_slug,
    project_template: result.project_template,
    project_path: result.project_path,
    review_summary: result.review_summary,
    next_steps: result.next_steps,
    generated_files: result.generated_files,
  });
}

function renderOutput(data) {
  const output = $("output");
  output.className = "output-card";
  output.dataset.renderState = JSON.stringify(data);

  if (data.status === "working") {
    output.innerHTML = `<p>${escapeHTML(data.message)}</p>`;
    return;
  }

  if (data.status === "error") {
    output.innerHTML = `<p class="error-text">${escapeHTML(data.message)}</p>`;
    return;
  }

  const files = data.generated_files || [];
  const steps = data.next_steps || [];
  output.innerHTML = `
    <dl>
      ${field(t("status"), data.status || "success")}
      ${field(t("project_slug"), data.project_slug || data.slug)}
      ${field(t("template"), data.project_template)}
      ${field(t("project_path"), data.project_path || data.path)}
      ${field(t("review_summary"), data.review_summary)}
    </dl>
    ${steps.length ? `<h3>${escapeHTML(t("next_steps"))}</h3><ul>${steps.map((step) => `<li>${escapeHTML(step)}</li>`).join("")}</ul>` : ""}
    ${files.length ? `<h3>${escapeHTML(t("generated_files"))}</h3><ul class="file-list">${files.map((file) => `<li>${escapeHTML(file)}</li>`).join("")}</ul>` : ""}
  `;
}

function field(label, value) {
  if (!value) {
    return "";
  }
  return `<dt>${escapeHTML(label)}</dt><dd>${escapeHTML(String(value))}</dd>`;
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
  loadSettings();
  loadProjects();
});
