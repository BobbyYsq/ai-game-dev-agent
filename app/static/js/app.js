const translations = {
  en: {
    eyebrow: "Godot prototype workflow",
    header_note: "Startup only opens this dashboard. The agent creates projects only after you submit a workflow.",
    loading: "Loading",
    ready: "Ready",
    settings_error: "Settings error",
    settings_title: "Settings",
    checking_key: "Checking key",
    key_configured: "API key configured",
    key_missing: "API key not configured",
    llm_provider: "LLM Provider",
    openai_model: "OpenAI Text Model",
    openai_key: "OpenAI API Key",
    save_settings: "Save Settings",
    test_connection: "Test Connection",
    saving_settings: "Saving settings...",
    settings_saved: "Settings saved.",
    testing_connection: "Testing connection...",
    connection_ok: "Connection test succeeded.",
    create_project: "Create Project",
    templates_badge: "v0.3 workflow",
    project_note: "This form starts the AI workflow: LLM planning, documentation, and optional Godot prototype generation.",
    project_name: "Project Name",
    project_name_placeholder: "Example: Shadow Garden",
    game_idea: "Game Idea / GDD",
    game_idea_placeholder: "Describe the game you want the AI agent to build...",
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
    godot_project_title: "Godot Project",
    godot_project_badge: "auto Hastur addon",
    godot_project_note: "Create a Godot project with the Hastur editor plugin copied and enabled automatically.",
    broker_host: "Broker Host",
    broker_http_port: "HTTP Port",
    broker_tcp_port: "TCP Port",
    create_godot_project: "Create Godot Project",
    godot_project_created: "Godot project created.",
    recent_projects: "Recent Projects",
    recent_note: "These are existing generated projects. Startup does not create new projects.",
    refresh: "Refresh",
    details: "Details",
    no_projects: "No generated projects yet.",
    assets_title: "Assets",
    assets_badge: "Image-2 pipeline",
    assets_note: "Generate concept art, GDD references, 2D drafts, UI icons, texture references, or Blender reference images for an existing project.",
    asset_project: "Project",
    image_provider: "Image Provider",
    image_model: "Image Model",
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
    asset_prompt_placeholder: "A haunted garden top-down action game concept art, readable silhouettes, dark fantasy.",
    save_asset_settings: "Save Image Settings",
    generate_image: "Generate Image",
    asset_project_required: "Select a project and enter an image prompt.",
    generating_image: "Generating image...",
    image_generated: "Image generated.",
    no_assets: "No generated image assets yet.",
    attach_gdd: "Attach to GDD",
    mark_blender: "Mark Blender Reference",
    asset_updated: "Asset updated.",
    hastur_title: "Hastur Bridge",
    hastur_badge: "Godot editor operations",
    hastur_note: "Start the local broker, connect Godot, and exchange safe structured operations with the bound LLM.",
    hastur_project: "Project",
    hastur_enabled: "Enable Hastur",
    hastur_base_url: "Broker URL",
    hastur_token: "Auth Token",
    save_hastur_settings: "Save Hastur Settings",
    start_broker: "Start Broker",
    stop_broker: "Stop Broker",
    broker_status: "Broker Status",
    broker_logs: "Broker Logs",
    check_hastur: "Check Status",
    load_executors: "Load Executors",
    apply_sample_operation: "Apply Test Node",
    ai_operation_title: "AI Godot Operation",
    ai_instruction: "Instruction",
    ai_instruction_placeholder: "Add a visible test node to the current scene and save it.",
    plan_operation: "Generate Plan",
    execute_plan: "Execute Plan",
    plan_and_execute: "Plan and Execute",
    hastur_project_required: "Select a project before applying an operation.",
    instruction_required: "Enter an instruction first.",
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
  zh: {},
};

translations.zh = translations.en;

const state = {
  language: localStorage.getItem("language") || "en",
  projects: [],
  assets: [],
  lastPlan: null,
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
  if (!el) return;
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
  if (!select || !value) return;
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
    $("image_provider").value = data.image_provider || "mock";
    ensureSelectValue($("image_model"), data.openai_image_model || "gpt-image-2");
    $("image_size").value = data.image_size || "1024x1024";
    $("image_quality").value = data.image_quality || "medium";
    $("hastur_enabled").checked = Boolean(data.hastur_enabled);
    $("hastur_base_url").value = data.hastur_base_url || "http://localhost:5302";
    $("hastur_auth_token").value = "";
    $("broker_host").value = data.hastur_broker_host || "localhost";
    $("broker_http_port").value = data.hastur_broker_http_port || 5302;
    $("broker_tcp_port").value = data.hastur_broker_tcp_port || 5301;
    $("godot_broker_host").value = data.hastur_broker_host || "localhost";
    $("godot_broker_port").value = data.hastur_broker_tcp_port || 5301;
    setConnectionStatus(t("ready"), "success");
  } catch (error) {
    setConnectionStatus(t("settings_error"), "error");
    setMessage("settingsMessage", error.message, "error");
  }
}

async function saveSettings() {
  setMessage("settingsMessage", t("saving_settings"));
  try {
    const result = await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        llm_provider: $("provider").value,
        openai_model: $("model").value,
        openai_api_key: $("apiKey").value || null,
      }),
    });
    $("apiKey").value = "";
    setMessage("settingsMessage", result.message || t("settings_saved"), "success");
    await loadSettings();
  } catch (error) {
    setMessage("settingsMessage", error.message, "error");
  }
}

async function saveAssetSettings() {
  setMessage("assetMessage", t("saving_settings"));
  try {
    await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_provider: $("image_provider").value,
        openai_image_model: $("image_model").value,
        image_size: $("image_size").value,
        image_quality: $("image_quality").value,
      }),
    });
    setMessage("assetMessage", t("settings_saved"), "success");
  } catch (error) {
    setMessage("assetMessage", error.message, "error");
  }
}

async function saveHasturSettings() {
  setMessage("hasturMessage", t("saving_settings"));
  try {
    const host = $("broker_host").value || "localhost";
    const httpPort = Number($("broker_http_port").value || 5302);
    const tcpPort = Number($("broker_tcp_port").value || 5301);
    await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        hastur_enabled: $("hastur_enabled").checked,
        hastur_base_url: $("hastur_base_url").value || `http://${host}:${httpPort}`,
        hastur_auth_token: $("hastur_auth_token").value || null,
        hastur_target_mode: "project_path",
        hastur_broker_host: host,
        hastur_broker_http_port: httpPort,
        hastur_broker_tcp_port: tcpPort,
      }),
    });
    $("hastur_auth_token").value = "";
    setMessage("hasturMessage", t("settings_saved"), "success");
    await loadSettings();
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
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
    game_type: $("game_type").value,
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

async function createGodotProject() {
  const projectName = $("godot_project_name").value.trim();
  if (!projectName) {
    setMessage("godotProjectMessage", t("project_required"), "error");
    return;
  }
  setMessage("godotProjectMessage", t("creating_project"));
  try {
    const result = await requestJSON("/api/godot-projects/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name: projectName,
        project_template: $("godot_project_template").value,
        game_type: $("godot_game_type").value,
        engine: $("godot_engine").value,
        broker_host: $("godot_broker_host").value || "localhost",
        broker_port: Number($("godot_broker_port").value || 5301),
      }),
    });
    setMessage("godotProjectMessage", t("godot_project_created"), "success");
    renderProjectResult(result);
    await loadProjects();
  } catch (error) {
    setMessage("godotProjectMessage", error.message, "error");
  }
}

async function loadProjects() {
  try {
    const data = await requestJSON("/api/projects");
    state.projects = data.projects || [];
    renderProjects();
    renderProjectSelectors();
  } catch (error) {
    $("recent_projects").innerHTML = `<li class="error-row">${escapeHTML(error.message)}</li>`;
  }
}

function renderProjectSelectors() {
  const selects = [$("asset_project_slug"), $("hastur_project_slug")];
  selects.forEach((select) => {
    const selected = select.value;
    select.innerHTML = state.projects
      .map((project) => `<option value="${escapeAttr(project.slug)}">${escapeHTML(project.slug)}</option>`)
      .join("");
    if (!state.projects.length) {
      select.innerHTML = `<option value="">${escapeHTML(t("no_projects"))}</option>`;
    } else {
      ensureSelectValue(select, selected || state.projects[0].slug);
    }
  });
  if (state.projects.length) {
    loadAssetsForSelectedProject();
  }
}

async function showProjectDetails(slug) {
  try {
    const details = await requestJSON(`/api/projects/${encodeURIComponent(slug)}`);
    renderOutput({ status: "details", slug: details.slug, path: details.path, generated_files: details.files });
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
    await requestJSON(`/api/projects/${encodeURIComponent(slug)}/assets/images/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        purpose: $("asset_purpose").value,
        model: $("image_model").value,
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

async function attachAssetToGDD(assetId) {
  await updateAsset("/attach-to-gdd", assetId);
}

async function markAssetBlenderReference(assetId) {
  await updateAsset("/mark-blender-reference", assetId);
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
            <div class="button-row">
              <button type="button" class="secondary compact" onclick="attachAssetToGDD('${escapeAttr(asset.id)}')">${escapeHTML(t("attach_gdd"))}</button>
              <button type="button" class="secondary compact" onclick="markAssetBlenderReference('${escapeAttr(asset.id)}')">${escapeHTML(t("mark_blender"))}</button>
            </div>
          </div>
        </article>
      `,
    )
    .join("");
}

async function startBroker() {
  setMessage("hasturMessage", t("loading"));
  try {
    const data = await requestJSON("/api/hastur/broker/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        host: $("broker_host").value || "localhost",
        http_port: Number($("broker_http_port").value || 5302),
        tcp_port: Number($("broker_tcp_port").value || 5301),
      }),
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
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function loadBrokerStatus() {
  try {
    const data = await requestJSON("/api/hastur/broker/status");
    renderMiniOutput("broker_output", data);
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

async function checkHasturStatus() {
  setMessage("hasturMessage", t("loading"));
  try {
    const data = await requestJSON("/api/hastur/status");
    renderMiniOutput("hastur_output", data);
    setMessage("hasturMessage", data.available ? t("connection_ok") : data.message, data.available ? "success" : "error");
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function loadHasturExecutors() {
  setMessage("hasturMessage", t("loading"));
  try {
    const data = await requestJSON("/api/hastur/executors");
    renderMiniOutput("hastur_output", data);
    setMessage("hasturMessage", data.available ? t("connection_ok") : data.message, data.available ? "success" : "error");
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function applySampleHasturOperation() {
  const slug = $("hastur_project_slug").value;
  if (!slug) {
    setMessage("hasturMessage", t("hastur_project_required"), "error");
    return;
  }
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/apply-operation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        operation: { operation: "create_node", node_type: "Node2D", node_name: "AgentGeneratedNode", parent_path: "." },
      }),
    });
    renderMiniOutput("hastur_output", data);
    setMessage("hasturMessage", data.message, data.success ? "success" : "error");
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function planGodotOperation() {
  const slug = $("hastur_project_slug").value;
  const instruction = $("ai_operation_instruction").value.trim();
  if (!slug) {
    setMessage("hasturMessage", t("hastur_project_required"), "error");
    return null;
  }
  if (!instruction) {
    setMessage("hasturMessage", t("instruction_required"), "error");
    return null;
  }
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instruction }),
    });
    state.lastPlan = data.plan;
    renderMiniOutput("hastur_output", data);
    setMessage("hasturMessage", "Plan generated.", "success");
    return data.plan;
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
    return null;
  }
}

async function executeGodotPlan() {
  const slug = $("hastur_project_slug").value;
  if (!slug || !state.lastPlan) {
    setMessage("hasturMessage", "Generate a plan first.", "error");
    return;
  }
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/execute-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ operations: state.lastPlan.operations || [] }),
    });
    renderMiniOutput("hastur_output", data);
    setMessage("hasturMessage", data.success ? "Plan executed." : "Plan execution failed.", data.success ? "success" : "error");
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
}

async function planAndExecuteGodotOperation() {
  const slug = $("hastur_project_slug").value;
  const instruction = $("ai_operation_instruction").value.trim();
  if (!slug || !instruction) {
    setMessage("hasturMessage", !slug ? t("hastur_project_required") : t("instruction_required"), "error");
    return;
  }
  try {
    const data = await requestJSON(`/api/projects/${encodeURIComponent(slug)}/hastur/plan-and-execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instruction }),
    });
    state.lastPlan = data.plan;
    renderMiniOutput("hastur_output", data);
    setMessage("hasturMessage", data.success ? "Plan executed." : "Plan execution failed.", data.success ? "success" : "error");
  } catch (error) {
    setMessage("hasturMessage", error.message, "error");
  }
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

function renderMiniOutput(id, data) {
  $(id).textContent = JSON.stringify(data, null, 2);
}

function field(label, value) {
  if (!value) return "";
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
  $("asset_project_slug").addEventListener("change", loadAssetsForSelectedProject);
  loadSettings();
  loadProjects();
  loadBrokerStatus();
});
