const translations = {
  en: {
    eyebrow: "Godot prototype workflow",
    app_title: "AI Game Development Agent",
    header_note: "Create Godot prototypes, generate assets, and operate Godot through a local Hastur broker.",
    loading: "Loading",
    ready: "Ready",
    settings_error: "Settings error",
    settings_title: "Settings",
    checking_key: "Checking key",
    key_configured: "API key configured",
    key_missing: "API key not configured",
    llm_provider: "LLM Provider",
    llm_model: "Text Model",
    llm_base_url: "LLM Base URL",
    llm_key: "LLM API Key",
    save_settings: "Save Settings",
    test_connection: "Test Connection",
    saving_settings: "Saving settings...",
    settings_saved: "Settings saved.",
    testing_connection: "Testing connection...",
    connection_ok: "Connection test succeeded.",
    project_name: "Project Name",
    project_name_placeholder: "Example: Shadow Garden",
    godot_template: "Godot Project Template",
    template_2d: "2D Game Prototype",
    template_3d: "3D Game Prototype",
    game_type: "Game Type",
    engine_version: "Engine Version",
    enable_git: "Initialize Git",
    project_required: "Project name is required.",
    creating_project: "Creating Godot project...",
    godot_project_title: "Godot Project",
    godot_project_badge: "auto Hastur addon",
    godot_project_note: "Create a Godot project with Hastur copied, enabled, and committed to a fresh Git repository.",
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
    assets_badge: "image pipeline",
    assets_note: "Generate concept art, GDD references, 2D drafts, UI icons, texture references, or Blender reference images for an existing project.",
    asset_project: "Project",
    image_provider: "Image Provider",
    image_model: "Image Model",
    image_base_url: "Image Base URL",
    image_key: "Image API Key",
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
    save_asset_settings: "Save Image Defaults",
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
    status: "Status",
    project_slug: "Project slug",
    template: "Template",
    project_path: "Project path",
    generated_files: "Generated files",
  },
  zh: {
    eyebrow: "Godot 原型工作流",
    app_title: "AI 游戏开发 Agent",
    header_note: "创建 Godot 原型、生成资产，并通过本地 Hastur broker 操作 Godot。",
    loading: "加载中",
    ready: "就绪",
    settings_error: "设置错误",
    settings_title: "设置",
    checking_key: "检查密钥",
    key_configured: "API 密钥已配置",
    key_missing: "API 密钥未配置",
    llm_provider: "LLM 提供商",
    llm_model: "文本模型",
    llm_base_url: "LLM Base URL",
    llm_key: "LLM API 密钥",
    save_settings: "保存设置",
    test_connection: "测试连接",
    saving_settings: "正在保存设置...",
    settings_saved: "设置已保存。",
    testing_connection: "正在测试连接...",
    connection_ok: "连接测试成功。",
    project_name: "项目名称",
    project_name_placeholder: "例如：Shadow Garden",
    godot_template: "Godot 项目模板",
    template_2d: "2D 游戏原型",
    template_3d: "3D 游戏原型",
    game_type: "游戏类型",
    engine_version: "引擎版本",
    enable_git: "初始化 Git",
    project_required: "请输入项目名称。",
    creating_project: "正在创建 Godot 项目...",
    godot_project_title: "Godot 项目",
    godot_project_badge: "自动启用 Hastur 插件",
    godot_project_note: "创建带 Hastur 插件、自动启用并初始化 Git 的 Godot 项目。",
    broker_host: "Broker 主机",
    broker_http_port: "HTTP 端口",
    broker_tcp_port: "TCP 端口",
    create_godot_project: "创建 Godot 项目",
    godot_project_created: "Godot 项目已创建。",
    recent_projects: "最近项目",
    recent_note: "这里显示已生成的项目。启动页面不会自动创建新项目。",
    refresh: "刷新",
    details: "详情",
    no_projects: "还没有生成项目。",
    assets_title: "资产",
    assets_badge: "图像管线",
    assets_note: "为已有项目生成概念图、GDD 参考图、2D 草图、UI 图标、贴图参考或 Blender 参考图。",
    asset_project: "项目",
    image_provider: "生图提供商",
    image_model: "生图模型",
    image_base_url: "生图 Base URL",
    image_key: "生图 API 密钥",
    asset_purpose: "用途",
    purpose_concept: "概念图",
    purpose_gdd: "GDD 参考",
    purpose_sprite: "2D 角色草图",
    purpose_icon: "UI/图标",
    purpose_texture: "贴图参考",
    purpose_blender: "Blender/3D 参考",
    image_size: "尺寸",
    image_quality: "质量",
    asset_prompt: "图像提示词",
    asset_prompt_placeholder: "暗黑花园俯视角动作游戏概念图，剪影清晰，暗黑奇幻风格。",
    save_asset_settings: "保存生图默认值",
    generate_image: "生成图像",
    asset_project_required: "请选择项目并输入图像提示词。",
    generating_image: "正在生成图像...",
    image_generated: "图像已生成。",
    no_assets: "还没有生成图像资产。",
    attach_gdd: "附加到 GDD",
    mark_blender: "标记为 Blender 参考",
    asset_updated: "资产已更新。",
    hastur_title: "Hastur 桥接",
    hastur_badge: "Godot 编辑器操作",
    hastur_note: "启动本地 broker，连接 Godot，并用已绑定的 LLM 交换安全的结构化操作。",
    hastur_project: "项目",
    hastur_enabled: "启用 Hastur",
    hastur_base_url: "Broker URL",
    hastur_token: "认证 Token",
    save_hastur_settings: "保存 Hastur 设置",
    start_broker: "启动 Broker",
    stop_broker: "停止 Broker",
    broker_status: "Broker 状态",
    broker_logs: "Broker 日志",
    check_hastur: "检查状态",
    load_executors: "加载执行器",
    apply_sample_operation: "添加测试节点",
    ai_operation_title: "AI Godot 操作",
    ai_instruction: "指令",
    ai_instruction_placeholder: "向当前场景添加一个可见测试节点并保存。",
    plan_operation: "生成计划",
    execute_plan: "执行计划",
    plan_and_execute: "生成并执行",
    hastur_project_required: "执行操作前请选择项目。",
    instruction_required: "请先输入指令。",
    status: "状态",
    project_slug: "项目 slug",
    template: "模板",
    project_path: "项目路径",
    generated_files: "生成文件",
  },
};

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

async function loadSettings() {
  try {
    const data = await requestJSON("/api/settings");
    $("provider").value = data.llm_provider || "mock";
    $("model").value = data.llm_model || data.openai_model || "gpt-5.4-mini";
    $("llmBaseUrl").value = data.llm_base_url || "";
    $("apiKeyStatus").textContent = data.has_llm_api_key ? t("key_configured") : t("key_missing");
    $("settings_image_provider").value = data.image_provider || "mock";
    $("settings_image_model").value = data.openai_image_model || "gpt-image-2";
    $("imageBaseUrl").value = data.image_base_url || "";
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
    const llmModel = $("model").value.trim();
    const imageModel = $("settings_image_model").value.trim();
    const result = await requestJSON("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        llm_provider: $("provider").value,
        llm_model: llmModel,
        openai_model: llmModel,
        llm_base_url: $("llmBaseUrl").value.trim(),
        llm_api_key: $("apiKey").value || null,
        openai_api_key: $("provider").value === "openai" ? $("apiKey").value || null : null,
        image_provider: $("settings_image_provider").value,
        openai_image_model: imageModel,
        image_base_url: $("imageBaseUrl").value.trim(),
        image_api_key: $("imageApiKey").value || null,
        image_size: $("image_size").value,
        image_quality: $("image_quality").value,
      }),
    });
    $("apiKey").value = "";
    $("imageApiKey").value = "";
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
        openai_image_model: $("settings_image_model").value.trim() || "gpt-image-2",
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

async function createProject() {
  const projectName = $("project_name").value.trim();
  if (!projectName) {
    setMessage("projectMessage", t("project_required"), "error");
    return;
  }
  setMessage("projectMessage", t("creating_project"));
  renderProjectOutput({ status: "working", message: t("creating_project") });
  try {
    const result = await requestJSON("/api/godot-projects/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name: projectName,
        project_template: $("project_template").value,
        game_type: $("game_type").value,
        engine: $("engine").value,
        broker_host: $("godot_broker_host").value || "localhost",
        broker_port: Number($("godot_broker_port").value || 5301),
        enable_git: $("enable_git").checked,
      }),
    });
    setMessage("projectMessage", t("godot_project_created"), "success");
    renderProjectOutput(projectResultView(result));
    await loadProjects();
  } catch (error) {
    setMessage("projectMessage", error.message, "error");
    renderProjectOutput({ status: "error", message: error.message });
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
      select.value = selected && state.projects.some((project) => project.slug === selected) ? selected : state.projects[0].slug;
    }
  });
  if (state.projects.length) {
    loadAssetsForSelectedProject();
  }
}

async function showProjectDetails(slug) {
  try {
    const details = await requestJSON(`/api/projects/${encodeURIComponent(slug)}`);
    renderDetailsOutput("recent_project_details", {
      status: "details",
      project_slug: details.slug,
      project_path: details.path,
      generated_files: details.files || [],
    });
  } catch (error) {
    renderDetailsOutput("recent_project_details", { status: "error", message: error.message });
  }
}

function renderProjects() {
  const list = $("recent_projects");
  if (!state.projects.length) {
    list.innerHTML = `<li class="muted-row">${escapeHTML(t("no_projects"))}</li>`;
    $("recent_project_details").innerHTML = "";
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
        model: $("settings_image_model").value.trim() || "gpt-image-2",
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

function projectResultView(result) {
  return {
    status: "success",
    project_slug: result.project_slug,
    project_template: result.project_template,
    project_path: result.project_path,
    generated_files: result.generated_files || [],
  };
}

function renderProjectOutput(data) {
  renderDetailsOutput("project_output", data);
}

function renderDetailsOutput(id, data) {
  const output = $(id);
  if (data.status === "working") {
    output.innerHTML = `<p>${escapeHTML(data.message)}</p>`;
    return;
  }
  if (data.status === "error") {
    output.innerHTML = `<p class="error-text">${escapeHTML(data.message)}</p>`;
    return;
  }
  const files = data.generated_files || [];
  output.innerHTML = `
    <dl>
      ${field(t("status"), data.status || "success")}
      ${field(t("project_slug"), data.project_slug)}
      ${field(t("template"), data.project_template)}
      ${field(t("project_path"), data.project_path)}
    </dl>
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
