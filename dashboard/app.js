// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const btnSend = document.getElementById("btnSend");
const btnClear = document.getElementById("btnClear");
const btnVoice = document.getElementById("btnVoice");
const btnHUD = document.getElementById("btnHUD");
const btnSettings = document.getElementById("btnSettings");
const btnCopyLast = document.getElementById("btnCopyLast");
const btnSpeakLast = document.getElementById("btnSpeakLast");
const typingIndicator = document.getElementById("typingIndicator");
const coreVisualizer = document.getElementById("coreVisualizer");
const voiceSelect = document.getElementById("voiceSelect");
const voiceRateSlider = document.getElementById("voiceRate");
const voicePitchSlider = document.getElementById("voicePitch");
const rateValue = document.getElementById("rateValue");
const pitchValue = document.getElementById("pitchValue");
const voiceEnabledToggle = document.getElementById("voiceEnabledToggle");
const autoSpeakToggle = document.getElementById("autoSpeakToggle");
const btnTestVoice = document.getElementById("btnTestVoice");
const btnStopVoice = document.getElementById("btnStopVoice");
const btnWakeWord = document.getElementById("btnWakeWord");
const settingsOverlay = document.getElementById("settingsOverlay");
const settingsDrawer = document.getElementById("settingsDrawer");
const btnCloseSettings = document.getElementById("btnCloseSettings");
const toastContainer = document.getElementById("toastContainer");
const modalOverlay = document.getElementById("modalOverlay");
const wakeIndicator = document.getElementById("wakeIndicator");
const wakeStatus = document.getElementById("wakeStatus");
const wakeLastTranscript = document.getElementById("wakeLastTranscript");
const wakeLastCommand = document.getElementById("wakeLastCommand");
const wakeError = document.getElementById("wakeError");
const wakeWordToggle = document.getElementById("wakeWordToggle");

// State
let conversationId = null;
let lastResponse = "";
let voiceEnabled = localStorage.getItem("misaka_voice_enabled") !== "false";
let hudMode = localStorage.getItem("misaka_hud_mode") === "true";
let autoSpeak = localStorage.getItem("misaka_auto_speak") === "true";
let selectedVoiceName = localStorage.getItem("misaka_voice_name") || "";
let voiceRate = parseFloat(localStorage.getItem("misaka_voice_rate") || "1.0");
let voicePitch = parseFloat(
  localStorage.getItem("misaka_voice_pitch") || "1.1",
);
let pendingAlertIds = JSON.parse(
  localStorage.getItem("misaka_pending_alerts") || "[]",
);
let currentProvider = "mock";
let currentModel = "mock";
let currentAlertFilter = "all";
let speaking = false;
let currentUtterance = null;
let pendingConfirmation = null;
let voiceWakeController = null;
let compactMode = localStorage.getItem("misaka_compact_mode") === "true";
let desktopNotificationsEnabled =
  localStorage.getItem("misaka_desktop_notifications") === "true";

const APP_LABELS = {
  notepad: "Bloco de Notas",
  explorer: "Explorador de Arquivos",
  calculator: "Calculadora",
  vscode: "VS Code",
  discord: "Discord",
  chrome: "Chrome",
  edge: "Edge",
  browser: "Navegador",
  cmd: "Prompt de Comando",
  powershell: "PowerShell",
};

let desktopBridgeState = {
  status: "Checking",
  detail: "",
  bridge: null,
};

function isSafeHttpUrl(url) {
  if (typeof url !== "string") return false;
  const lower = url.trim().toLowerCase();
  if (
    lower.startsWith("javascript:") ||
    lower.startsWith("data:") ||
    lower.startsWith("file:") ||
    lower.startsWith("about:")
  ) {
    return false;
  }
  return lower.startsWith("http://") || lower.startsWith("https://");
}

async function detectDesktopBridge() {
  const bridge = window.misakaDesktop;
  if (!bridge || bridge.isAvailable !== true) {
    desktopBridgeState = {
      status: "Offline",
      detail: "Bridge Electron nao detectado (modo navegador).",
      bridge: null,
    };
    console.log("[Misaka] Desktop Bridge: Offline");
    return desktopBridgeState;
  }

  if (
    typeof bridge.openApp !== "function" ||
    typeof bridge.openUrl !== "function"
  ) {
    desktopBridgeState = {
      status: "Error",
      detail: "Bridge incompleto: openApp/openUrl ausentes.",
      bridge,
    };
    console.log("[Misaka] Desktop Bridge: Error (incomplete)");
    return desktopBridgeState;
  }

  if (typeof bridge.getSystemStatus === "function") {
    try {
      const status = await bridge.getSystemStatus();
      if (status && status.success === false) {
        desktopBridgeState = {
          status: "Error",
          detail: status.error || "Falha ao consultar status do sistema.",
          bridge,
        };
        console.log("[Misaka] Desktop Bridge: Error (system status)");
        return desktopBridgeState;
      }
    } catch (error) {
      desktopBridgeState = {
        status: "Error",
        detail: error.message,
        bridge,
      };
      console.log("[Misaka] Desktop Bridge: Error", error.message);
      return desktopBridgeState;
    }
  }

  desktopBridgeState = {
    status: "Online",
    detail: "Bridge Electron ativo.",
    bridge,
  };
  console.log("[Misaka] Desktop Bridge: Online");
  return desktopBridgeState;
}

function updateDesktopBridgeUI() {
  const desktopModule = document.getElementById("desktopModule");
  if (!desktopModule) return;

  const label = desktopBridgeState.status;
  desktopModule.textContent = label;
  desktopModule.className = `module-status ${
    label === "Online" ? "online" : label === "Error" ? "error" : ""
  }`;
  desktopModule.title = desktopBridgeState.detail || label;
}

// ==================== Toast System ====================
function showToast(message, type = "info", duration = 4000) {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("toast-show"));
  setTimeout(() => {
    toast.classList.remove("toast-show");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ==================== Voice System ====================
function initVoiceControls() {
  voiceRateSlider.value = voiceRate;
  voicePitchSlider.value = voicePitch;
  rateValue.textContent = voiceRate;
  pitchValue.textContent = voicePitch;
  voiceEnabledToggle.checked = voiceEnabled;
  autoSpeakToggle.checked = autoSpeak;

  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = populateVoiceSelect;
    populateVoiceSelect();
  }
}

function populateVoiceSelect() {
  const voices = window.speechSynthesis.getVoices();
  voiceSelect.innerHTML = '<option value="">Default (pt-BR)</option>';

  const ptBrVoices = voices.filter((v) => v.lang.includes("pt-BR"));
  const femaleVoices = voices.filter(
    (v) =>
      v.name.toLowerCase().includes("female") ||
      v.name.toLowerCase().includes("feminina") ||
      v.name.toLowerCase().includes("helena") ||
      v.name.toLowerCase().includes("francisca"),
  );
  const ptVoices = voices.filter(
    (v) => v.lang.includes("pt") && !v.lang.includes("pt-BR"),
  );

  if (ptBrVoices.length > 0) {
    const og = document.createElement("optgroup");
    og.label = "Portuguese (Brazil)";
    ptBrVoices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.name;
      o.textContent = `${v.name}${v.localService ? " (local)" : ""}`;
      if (v.name === selectedVoiceName) o.selected = true;
      og.appendChild(o);
    });
    voiceSelect.appendChild(og);
  }

  if (ptVoices.length > 0) {
    const og = document.createElement("optgroup");
    og.label = "Portuguese";
    ptVoices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.name;
      o.textContent = `${v.name}${v.localService ? " (local)" : ""}`;
      if (v.name === selectedVoiceName) o.selected = true;
      og.appendChild(o);
    });
    voiceSelect.appendChild(og);
  }

  if (femaleVoices.length > 0 && ptBrVoices.length === 0) {
    const og = document.createElement("optgroup");
    og.label = "Female voices";
    femaleVoices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.name;
      o.textContent = `${v.name}${v.localService ? " (local)" : ""}`;
      if (v.name === selectedVoiceName) o.selected = true;
      og.appendChild(o);
    });
    voiceSelect.appendChild(og);
  }
}

function getSelectedVoice() {
  const voices = window.speechSynthesis.getVoices();
  if (selectedVoiceName) {
    const found = voices.find((v) => v.name === selectedVoiceName);
    if (found) return found;
  }
  const ptBrFemale = voices.find(
    (v) =>
      v.lang.includes("pt-BR") &&
      (v.name.toLowerCase().includes("female") ||
        v.name.toLowerCase().includes("feminina") ||
        v.name.toLowerCase().includes("helena") ||
        v.name.toLowerCase().includes("francisca")),
  );
  if (ptBrFemale) return ptBrFemale;
  const ptBr = voices.find((v) => v.lang.includes("pt-BR"));
  if (ptBr) return ptBr;
  const female = voices.find(
    (v) =>
      v.name.toLowerCase().includes("female") ||
      v.name.toLowerCase().includes("feminina"),
  );
  return female || voices[0];
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  if (!voiceEnabled && !autoSpeak) return;

  window.speechSynthesis.cancel();
  speaking = false;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "pt-BR";
  utterance.rate = voiceRate;
  utterance.pitch = voicePitch;

  const voice = getSelectedVoice();
  if (voice) {
    utterance.voice = voice;
  }

  utterance.onstart = () => {
    speaking = true;
    setCoreState("speaking");
  };
  utterance.onend = () => {
    speaking = false;
    setCoreState(null);
  };
  utterance.onerror = (e) => {
    speaking = false;
    setCoreState(null);
    if (e.error !== "canceled") {
      console.error("Speech error:", e.error);
    }
  };

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

function stopVoice() {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    speaking = false;
    currentUtterance = null;
    setCoreState(null);
    showToast("Voz parada.", "info");
  }
}

function testVoice() {
  speak(`Olá, eu sou a Misaka.\nEsta é minha voz.`);
}

// ==================== UI Functions ====================
function updateVoiceButton() {
  btnVoice.style.color = voiceEnabled
    ? "var(--color-primary)"
    : "var(--color-muted)";
}

function updateHUDButton() {
  btnHUD.style.color = hudMode ? "var(--color-primary)" : "var(--color-muted)";
  document.body.classList.toggle("hud-mode", hudMode);
}

function showProviderStatus(provider, model, fallbackActive) {
  const existing = document.querySelector(
    ".mock-warning, .gemini-active, .gemini-fallback",
  );
  if (existing) existing.remove();

  const chatSection = document.querySelector(".chat-section");

  if (provider === "mock") {
    const warning = document.createElement("div");
    warning.className = "mock-warning";
    warning.textContent = `Misaka está em modo simulação.\nConfigure GEMINI_API_KEY para respostas inteligentes.`;
    chatSection.prepend(warning);
  } else if (provider === "gemini" && fallbackActive) {
    const fb = document.createElement("div");
    fb.className = "gemini-fallback";
    fb.textContent = `Usando ${model} temporariamente (fallback ativo)`;
    chatSection.prepend(fb);
  } else if (provider === "gemini") {
    const active = document.createElement("div");
    active.className = "gemini-active";
    active.textContent = `Gemini Pro ativo — ${model}`;
    chatSection.prepend(active);
  }
}

async function loadStatus() {
  try {
    const response = await fetch(`${MISAKA_CONFIG.API_BASE_URL}/overview`);
    const data = await response.json();

    currentProvider = data.llm_provider;
    currentModel = data.llm_model;

    document.getElementById("version").textContent = `v${data.version}`;
    document.getElementById("llmProvider").textContent = data.llm_provider;
    document.getElementById("llmModel").textContent = data.llm_model;
    document.getElementById("providerBadge").textContent = data.llm_provider;
    document.getElementById("memoryStatus").textContent = data.memory_enabled
      ? "Enabled"
      : "Disabled";
    document.getElementById("calendarStatus").textContent =
      data.calendar_enabled ? "Enabled" : "Disabled";
    document.getElementById("toolsStatus").textContent = data.tools_enabled
      ? "Enabled"
      : "Disabled";
    document.getElementById("notificationsStatus").textContent =
      data.notifications_enabled ? "Enabled" : "Disabled";

    const androidModule = document.getElementById("androidModule");
    if (androidModule) {
      androidModule.textContent = data.android_bridge_enabled
        ? "Online"
        : "Offline";
      androidModule.className = `module-status ${data.android_bridge_enabled ? "online" : ""}`;
    }

    document.getElementById("memoryModule").textContent = data.memory_enabled
      ? "Active"
      : "Disabled";
    document.getElementById("memoryModule").className =
      `module-status ${data.memory_enabled ? "online" : ""}`;
    document.getElementById("calendarModule").textContent =
      data.calendar_enabled ? "Active" : "Disabled";
    document.getElementById("calendarModule").className =
      `module-status ${data.calendar_enabled ? "online" : ""}`;
    document.getElementById("llmStatus").textContent =
      data.llm_provider === "mock" ? "Mock" : "Active";

    await detectDesktopBridge();
    updateDesktopBridgeUI();

    // Fallback status
    const fallbackItem = document.getElementById("fallbackStatusItem");
    if (data.llm_fallback_active) {
      fallbackItem.style.display = "flex";
      document.getElementById("fallbackStatus").textContent =
        `Active (${data.llm_model})`;
    } else {
      fallbackItem.style.display = "none";
    }

    showProviderStatus(
      data.llm_provider,
      data.llm_model,
      data.llm_fallback_active,
    );
  } catch (error) {
    console.error("Failed to load status:", error);
  }
}

function setCoreState(state) {
  coreVisualizer.className = "core-visualizer";
  if (state) {
    coreVisualizer.classList.add(state);
  }
}

function addMessage(text, type) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${type}`;

  const avatarDiv = document.createElement("div");
  avatarDiv.className = "message-avatar";
  avatarDiv.textContent = type === "user" ? "D" : "M";
  messageDiv.appendChild(avatarDiv);

  const bodyDiv = document.createElement("div");
  bodyDiv.className = "message-body";

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";
  contentDiv.textContent =
    type === "assistant" ? cleanAssistantText(text) : text;
  bodyDiv.appendChild(contentDiv);

  messageDiv.appendChild(bodyDiv);
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  lastResponse = text;
}

function cleanAssistantText(text) {
  if (!text) return "";
  let cleaned = text;
  cleaned = cleaned.replace(/\*\*(.+?)\*\*/g, "$1");
  cleaned = cleaned.replace(/\*(.+?)\*/g, "$1");
  cleaned = cleaned.replace(/__(.+?)__/g, "$1");
  cleaned = cleaned.replace(/_(.+?)_/g, "$1");
  cleaned = cleaned.replace(/`(.+?)`/g, "$1");
  cleaned = cleaned.replace(/~~(.+?)~~/g, "$1");
  cleaned = cleaned.replace(/#{1,6}\s*/g, "");
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n");
  cleaned = cleaned.trim();
  return cleaned;
}

// ==================== Client Action Handler ====================
async function handleClientAction(action) {
  if (!action || !action.type) {
    return { success: false, type: "", message: "", error: "Acao invalida.", action };
  }

  const bridgeInfo = await detectDesktopBridge();
  const bridge = bridgeInfo.bridge;
  const appLabel = APP_LABELS[action.app] || action.app || "aplicativo";

  if (action.type === "open_url") {
    const url = action.url;
    if (!isSafeHttpUrl(url)) {
      return {
        success: false,
        type: "open_url",
        message: "",
        error: "URL invalida. Use apenas http:// ou https://.",
        action,
      };
    }

    if (bridge && typeof bridge.openUrl === "function") {
      const result = await bridge.openUrl(url);
      console.log("[Misaka] client_action open_url result:", result);
      if (result && result.success) {
        return {
          success: true,
          type: "open_url",
          message: "Pagina aberta, diz Misaka Misaka.",
          error: "",
          action,
        };
      }
      return {
        success: false,
        type: "open_url",
        message: "",
        error: (result && result.error) || "erro desconhecido",
        action,
      };
    }

    try {
      const opened = window.open(url, "_blank", "noopener,noreferrer");
      if (opened) {
        return {
          success: true,
          type: "open_url",
          message: "Pagina aberta, diz Misaka Misaka.",
          error: "",
          action,
        };
      }
      return {
        success: false,
        type: "open_url",
        message: "",
        error: "popup bloqueado",
        action,
      };
    } catch (error) {
      return {
        success: false,
        type: "open_url",
        message: "",
        error: error.message,
        action,
      };
    }
  }

  if (action.type === "open_app") {
    if (bridge && typeof bridge.openApp === "function") {
      const result = await bridge.openApp(action.app);
      console.log("[Misaka] client_action open_app result:", result);
      if (result && result.success) {
        return {
          success: true,
          type: "open_app",
          message: `${appLabel} aberto no seu computador, diz Misaka Misaka.`,
          error: "",
          action,
        };
      }
      return {
        success: false,
        type: "open_app",
        message: "",
        error: (result && result.error) || "app nao encontrado",
        action,
      };
    }
    return {
      success: false,
      type: "open_app",
      message: "",
      error: "Para abrir aplicativos locais, use o app desktop da Misaka.",
      action,
    };
  }

  if (action.type === "search_web") {
    const provider = action.provider || "google";
    if (bridge && typeof bridge.searchWeb === "function") {
      const result = await bridge.searchWeb(action.query, provider);
      console.log("[Misaka] client_action search_web result:", result);
      if (result && result.success) {
        return {
          success: true,
          type: "search_web",
          message: "Pesquisa aberta, diz Misaka Misaka.",
          error: "",
          action,
        };
      }
      return {
        success: false,
        type: "search_web",
        message: "",
        error: (result && result.error) || "erro desconhecido",
        action,
      };
    }

    const urls = {
      google: `https://www.google.com/search?q=${encodeURIComponent(action.query)}`,
      youtube: `https://www.youtube.com/results?search_query=${encodeURIComponent(action.query)}`,
      github: `https://github.com/search?q=${encodeURIComponent(action.query)}&type=repositories`,
      reddit: `https://www.reddit.com/search/?q=${encodeURIComponent(action.query)}`,
      modrinth: `https://modrinth.com/mods?q=${encodeURIComponent(action.query)}`,
      curseforge: `https://www.curseforge.com/minecraft/search?search=${encodeURIComponent(action.query)}`,
    };
    const url = action.url || urls[provider] || urls.google;
    if (!isSafeHttpUrl(url)) {
      return {
        success: false,
        type: "search_web",
        message: "",
        error: "URL de pesquisa invalida.",
        action,
      };
    }
    try {
      const opened = window.open(url, "_blank", "noopener,noreferrer");
      if (opened) {
        return {
          success: true,
          type: "search_web",
          message: "Pesquisa aberta, diz Misaka Misaka.",
          error: "",
          action,
        };
      }
      return {
        success: false,
        type: "search_web",
        message: "",
        error: "popup bloqueado",
        action,
      };
    } catch (error) {
      return {
        success: false,
        type: "search_web",
        message: "",
        error: error.message,
        action,
      };
    }
  }

  if (action.type === "get_system_status") {
    if (bridge && typeof bridge.getSystemStatus === "function") {
      const status = await bridge.getSystemStatus();
      return {
        success: true,
        type: "get_system_status",
        message: `PC: ${status.platform} | RAM: ${Math.round(status.memory?.heapUsed / 1024 / 1024 || 0)}MB`,
        error: "",
        action,
      };
    }
    return {
      success: false,
      type: "get_system_status",
      message: "",
      error: "Status do PC indisponivel fora do app desktop.",
      action,
    };
  }

  if (action.type === "show_toast") {
    showToast(action.message || "Alerta do Misaka", "info");
    return { success: true, type: "show_toast", message: "", error: "", action };
  }

  return { success: false, type: action.type, message: "", error: "Acao nao suportada.", action };
}

function formatActionResult(result) {
  if (!result) return "";
  if (result.success) return result.message;
  if (result.type === "open_app") {
    const appLabel =
      APP_LABELS[result.action?.app] || result.action?.app || "aplicativo";
    return `Nao consegui abrir ${appLabel}. Motivo: ${result.error}, diz Misaka Misaka.`;
  }
  if (result.type === "open_url") {
    return `Nao consegui abrir a pagina. Motivo: ${result.error}, diz Misaka Misaka.`;
  }
  if (result.type === "search_web") {
    return `Nao consegui pesquisar. Motivo: ${result.error}, diz Misaka Misaka.`;
  }
  if (result.error) {
    return `Nao consegui executar a acao. Motivo: ${result.error}, diz Misaka Misaka.`;
  }
  return result.message || "";
}
// ==================== Chat Functions ====================
async function sendMessage(messageOverride = null, options = {}) {
  const fromVoice = options.source === "voice";
  const silentUserMessage = options.silentUserMessage === true;
  const skipInputClear = options.skipInputClear === true;
  const message =
    typeof messageOverride === "string"
      ? messageOverride.trim()
      : messageInput.value.trim();
  if (!message) return { success: false, error: "empty_message" };

  if (!silentUserMessage) {
    addMessage(message, "user");
  }
  if (!fromVoice && !skipInputClear) {
    messageInput.value = "";
    messageInput.style.height = "auto";
  }
  messageInput.style.height = "auto";

  setCoreState("thinking");
  typingIndicator.classList.add("active");
  btnSend.disabled = true;

  let actionOutcome = { success: true };

  try {
    const response = await fetch(`${MISAKA_CONFIG.API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId,
      }),
    });

    const data = await response.json();
    conversationId = data.conversation_id;

    const clientAction = data.metadata && data.metadata.client_action;
    const assistantResponse = data.response;

    if (clientAction) {
      console.log("[Misaka] client_action received:", clientAction);
    }

    setCoreState("speaking");
    if (assistantResponse) {
      addMessage(assistantResponse, "assistant");
    }

    // Show command-specific UI effects
    if (data.metadata && data.metadata.ui_effect) {
      const effect = data.metadata.ui_effect;
      if (effect === "clear_chat") {
        setTimeout(clearChat, 500);
      }
      if (effect === "enable_hud") {
        hudMode = true;
        localStorage.setItem("misaka_hud_mode", "true");
        updateHUDButton();
      }
      if (effect === "disable_hud") {
        hudMode = false;
        localStorage.setItem("misaka_hud_mode", "false");
        updateHUDButton();
      }
      if (effect === "enable_voice") {
        voiceEnabled = true;
        localStorage.setItem("misaka_voice_enabled", "true");
        voiceEnabledToggle.checked = true;
        updateVoiceButton();
      }
      if (effect === "disable_voice") {
        voiceEnabled = false;
        localStorage.setItem("misaka_voice_enabled", "false");
        voiceEnabledToggle.checked = false;
        updateVoiceButton();
      }
      if (effect === "refresh_alerts") {
        loadAlerts();
      }
      if (effect === "refresh_status") {
        loadStatus();
      }
      if (effect === "open_settings") {
        openSettings();
      }
    }

    let actionResult = null;
    if (clientAction) {
      try {
        actionResult = await handleClientAction(clientAction);
        actionOutcome = actionResult;
      } catch (actionError) {
        actionResult = {
          success: false,
          type: clientAction.type,
          message: "",
          error: actionError.message,
          action: clientAction,
        };
        actionOutcome = actionResult;
      }
      const actionMessage = formatActionResult(actionResult);
      if (actionMessage) {
        addMessage(actionMessage, "assistant");
      }
    }

    const speakText =
      (actionResult && (actionResult.message || formatActionResult(actionResult))) ||
      assistantResponse;
    if (voiceEnabled && speakText && (autoSpeak || fromVoice)) {
      speak(speakText);
    }

    setTimeout(() => setCoreState(null), 3000);
    return {
      success: actionOutcome.success !== false,
      response: assistantResponse,
      action: actionOutcome,
      metadata: data.metadata || {},
    };
  } catch (error) {
    addMessage("Erro ao conectar com o servidor.", "system");
    setCoreState(null);
    return { success: false, error: error.message };
  } finally {
    typingIndicator.classList.remove("active");
    btnSend.disabled = false;
    messageInput.focus();
  }
}

function clearChat() {
  chatMessages.innerHTML = "";
  conversationId = null;
  addMessage(`Conversa reiniciada.\nComo posso ajudar?`, "system");
}

function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      showToast("Copiado!", "success");
    })
    .catch(() => {
      showToast("Erro ao copiar.", "error");
    });
}

// ==================== Alert Functions ====================
async function loadAlerts() {
  try {
    const response = await fetch(`${MISAKA_CONFIG.API_BASE_URL}/notifications/alerts`);
    const data = await response.json();

    const alertsContainer = document.getElementById("alertsContainer");
    const alertsCount = document.getElementById("alertsCount");
    if (!alertsContainer) return;

    alertsContainer.textContent = "";

    if (data.alerts && data.alerts.length > 0) {
      alertsCount.textContent = data.alerts.length;

      let filtered = data.alerts;
      if (currentAlertFilter !== "all") {
        if (currentAlertFilter === "pending") {
          filtered = data.alerts.filter((a) => a.status === "pending");
        } else {
          filtered = data.alerts.filter(
            (a) => a.priority === currentAlertFilter,
          );
        }
      }

      filtered.slice(0, 10).forEach((alert) => {
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert-item alert-${alert.priority}`;

        const titleSpan = document.createElement("span");
        titleSpan.className = "alert-title";
        titleSpan.textContent = alert.title;
        alertDiv.appendChild(titleSpan);

        const messageSpan = document.createElement("span");
        messageSpan.className = "alert-message";
        messageSpan.textContent = alert.message;
        alertDiv.appendChild(messageSpan);

        if (alert.status === "pending") {
          const ackBtn = document.createElement("button");
          ackBtn.className = "btn-alert-ack";
          ackBtn.textContent = "✓";
          ackBtn.title = "Mark as seen";
          ackBtn.onclick = async (e) => {
            e.stopPropagation();
            try {
              await fetch(`${MISAKA_CONFIG.API_BASE_URL}/notifications/alerts/${alert.id}/ack`, {
                method: "POST",
              });
              loadAlerts();
              showToast("Alerta marcado como visto.", "success");
            } catch (err) {
              showToast("Erro ao marcar alerta.", "error");
            }
          };
          alertDiv.appendChild(ackBtn);
        }

        alertsContainer.appendChild(alertDiv);

        if (!pendingAlertIds.includes(alert.id)) {
          pendingAlertIds.push(alert.id);
          if (
            desktopNotificationsEnabled &&
            Notification.permission === "granted"
          ) {
            new Notification(alert.title, { body: alert.message });
          }
        }
      });

      localStorage.setItem(
        "misaka_pending_alerts",
        JSON.stringify(pendingAlertIds),
      );
    } else {
      alertsCount.textContent = "0";
      const emptyDiv = document.createElement("div");
      emptyDiv.className = "alert-empty";
      emptyDiv.textContent = "No alerts";
      alertsContainer.appendChild(emptyDiv);
    }
  } catch (error) {
    console.error("Failed to load alerts:", error);
  }
}

async function ackAllAlerts() {
  try {
    const response = await fetch(`${MISAKA_CONFIG.API_BASE_URL}/notifications/alerts/ack-all`, {
      method: "POST",
    });
    const data = await response.json();
    showToast(data.message || "Alertas marcados como vistos.", "success");
    loadAlerts();
  } catch (error) {
    showToast("Erro ao limpar alertas.", "error");
  }
}

// ==================== Settings ====================
function openSettings() {
  settingsOverlay.classList.add("active");
  settingsDrawer.classList.add("active");
  loadSettingsInfo();
}

function closeSettings() {
  settingsOverlay.classList.remove("active");
  settingsDrawer.classList.remove("active");
}

async function loadSettingsInfo() {
  try {
    const response = await fetch(`${MISAKA_CONFIG.API_BASE_URL}/llm/status`);
    const data = await response.json();
    const info = document.getElementById("settingsLLMInfo");
    info.innerHTML = `
            <div class="settings-info-row"><span>Provider:</span><span>${data.provider}</span></div>
            <div class="settings-info-row"><span>Active model:</span><span>${data.active_model || "-"}</span></div>
            <div class="settings-info-row"><span>Primary:</span><span>${data.primary_model || "-"}</span></div>
            <div class="settings-info-row"><span>Fallback:</span><span>${data.fallback_model || "-"}</span></div>
            <div class="settings-info-row"><span>Configured:</span><span>${data.gemini_configured ? "Yes" : "No"}</span></div>
            ${data.last_error_type ? `<div class="settings-info-row warning"><span>Last error:</span><span>${data.last_error_type}</span></div>` : ""}
        `;
  } catch (e) {
    document.getElementById("settingsLLMInfo").textContent = "Failed to load";
  }

  // Desktop info
  const desktopInfo = document.getElementById("settingsDesktopInfo");
  if (window.misakaDesktop && window.misakaDesktop.isAvailable) {
    desktopInfo.innerHTML =
      '<span class="online">Desktop bridge available</span>';
  } else {
    desktopInfo.innerHTML = "<span>Web mode (no desktop bridge)</span>";
  }

  // Android info
  try {
    const response = await fetch(`${MISAKA_CONFIG.API_BASE_URL}/android/status`);
    const data = await response.json();
    const androidInfo = document.getElementById("settingsAndroidInfo");
    if (data.enabled) {
      androidInfo.innerHTML = `
                <span class="${data.connected ? "online" : ""}">${data.connected ? "Connected" : "Disconnected"}</span>
                <span>${data.pending_actions} pending actions</span>
            `;
    } else {
      androidInfo.innerHTML = "<span>Not configured</span>";
    }
  } catch (e) {
    document.getElementById("settingsAndroidInfo").textContent =
      "Failed to load";
  }
}

// ==================== Wake Word ====================
function initVoiceWakeController() {
  console.log("[Misaka Wake] initVoiceWakeController()");

  if (typeof VoiceWakeController === "undefined") {
    console.error("[Misaka Wake] VoiceWakeController not loaded from voiceWake.js");
    return;
  }

  voiceWakeController = new VoiceWakeController({
    elements: {
      button: btnWakeWord,
      toggle: wakeWordToggle,
      status: wakeStatus,
      lastTranscript: wakeLastTranscript,
      lastCommand: wakeLastCommand,
      error: wakeError,
      indicator: wakeIndicator,
    },
    callbacks: {
      sendVoiceCommand: (command) => sendMessage(command, { source: "voice" }),
      onStateChange: (state, label) => {
        console.log("[Misaka Wake] state:", state, label);
        const active = [
          "listening_for_wake",
          "wake_detected",
          "listening_for_command",
          "processing",
          "speaking",
        ].includes(state);
        btnWakeWord.style.opacity = state === "unavailable" ? "0.5" : "1";
        btnWakeWord.style.color = active
          ? "var(--color-primary)"
          : "var(--color-muted)";
        if (
          state === "error" ||
          state === "permission_needed" ||
          state === "unavailable"
        ) {
          showToast(label, "warning");
        }
      },
    },
  });

  const initResult = voiceWakeController.init();
  console.log("[Misaka Wake] init result:", initResult, "mode:", voiceWakeController.voiceMode);

  if (window.misakaDesktop && window.misakaDesktop.onWakeWordSetEnabled) {
    window.misakaDesktop.onWakeWordSetEnabled(async (enabled) => {
      console.log("[Misaka Wake] onWakeWordSetEnabled:", enabled);
      try {
        const started = await voiceWakeController.setEnabled(Boolean(enabled));
        if (enabled && !started) {
          showToast("Nao consegui ativar a escuta Misaka.", "warning");
        }
      } catch (err) {
        console.error("[Misaka Wake] setEnabled failed:", err);
        showToast(`Erro ao ativar escuta: ${err.message}`, "error");
      }
    });
  }

  if (window.misakaDesktop && window.misakaDesktop.onNativeVoiceCommand) {
    window.misakaDesktop.onNativeVoiceCommand((data) => {
      const command = data && data.command;
      if (command) {
        console.log("[Misaka] native voice command:", command);
        sendMessage(command, { source: "voice" });
      }
    });
  }
}
// ==================== Confirmation Modal ====================
function showConfirmation(title, message, payload) {
  modalOverlay.style.display = "flex";
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalMessage").textContent = message;
  pendingConfirmation = payload;
}

function hideConfirmation() {
  modalOverlay.style.display = "none";
  pendingConfirmation = null;
}

// ==================== Event Listeners ====================
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

messageInput.addEventListener("input", () => {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
});

btnSend.addEventListener("click", sendMessage);
btnClear.addEventListener("click", clearChat);

btnVoice.addEventListener("click", () => {
  voiceEnabled = !voiceEnabled;
  localStorage.setItem("misaka_voice_enabled", voiceEnabled);
  voiceEnabledToggle.checked = voiceEnabled;
  updateVoiceButton();
  showToast(voiceEnabled ? "Voz ativada." : "Voz desativada.", "info");
});

btnHUD.addEventListener("click", () => {
  hudMode = !hudMode;
  localStorage.setItem("misaka_hud_mode", hudMode);
  updateHUDButton();
  showToast(hudMode ? "HUD ativado." : "HUD desativado.", "info");
});

btnCopyLast.addEventListener("click", () => {
  if (lastResponse) copyToClipboard(lastResponse);
});

btnSpeakLast.addEventListener("click", () => {
  if (lastResponse) speak(lastResponse);
});

btnTestVoice.addEventListener("click", testVoice);
btnStopVoice.addEventListener("click", stopVoice);

// Voice Control Listeners
voiceSelect.addEventListener("change", (e) => {
  selectedVoiceName = e.target.value;
  localStorage.setItem("misaka_voice_name", selectedVoiceName);
});

voiceRateSlider.addEventListener("input", (e) => {
  voiceRate = parseFloat(e.target.value);
  rateValue.textContent = voiceRate.toFixed(1);
  localStorage.setItem("misaka_voice_rate", voiceRate);
});

voicePitchSlider.addEventListener("input", (e) => {
  voicePitch = parseFloat(e.target.value);
  pitchValue.textContent = voicePitch.toFixed(1);
  localStorage.setItem("misaka_voice_pitch", voicePitch);
});

voiceEnabledToggle.addEventListener("change", (e) => {
  voiceEnabled = e.target.checked;
  localStorage.setItem("misaka_voice_enabled", voiceEnabled);
  updateVoiceButton();
});

autoSpeakToggle.addEventListener("change", (e) => {
  autoSpeak = e.target.checked;
  localStorage.setItem("misaka_auto_speak", autoSpeak);
});

// Settings listeners
btnSettings.addEventListener("click", openSettings);
btnCloseSettings.addEventListener("click", closeSettings);
settingsOverlay.addEventListener("click", closeSettings);

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeSettings();
    hideConfirmation();
  }
});

// Alert filters
document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll(".filter-btn")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentAlertFilter = btn.dataset.filter;
    loadAlerts();
  });
});

document.getElementById("btnAckAll").addEventListener("click", ackAllAlerts);
document
  .getElementById("btnRefreshAlerts")
  .addEventListener("click", loadAlerts);

// Wake word
btnWakeWord.addEventListener("click", async () => {
  console.log("[Misaka Wake] button clicked");
  if (!voiceWakeController) {
    console.error("[Misaka Wake] voiceWakeController not initialized");
    showToast("Voice Wake nao inicializado.", "error");
    return;
  }
  const enabled = !voiceWakeController.enabled;
  console.log("[Misaka Wake] toggling to:", enabled);
  try {
    const started = await voiceWakeController.setEnabled(enabled);
    console.log("[Misaka Wake] setEnabled result:", started);
    if (enabled && started) {
      showToast('Wake word ativado.\nDiga "Misaka" para acionar.', "info");
    } else if (!enabled) {
      showToast("Wake word desativado.", "info");
    } else if (enabled && !started) {
      showToast(
        voiceWakeController.lastError ||
          voiceWakeController.elements.error?.textContent ||
          "Nao consegui ativar a escuta Misaka.",
        "warning",
      );
    }
  } catch (err) {
    console.error("[Misaka Wake] toggle failed:", err);
    showToast(`Erro ao ativar escuta: ${err.message}`, "error");
  }
});
// Settings toggles
document.getElementById("speakSuffixToggle").addEventListener("change", (e) => {
  localStorage.setItem("misaka_speak_suffix", e.target.checked);
});

document
  .getElementById("desktopNotificationsToggle")
  .addEventListener("change", (e) => {
    desktopNotificationsEnabled = e.target.checked;
    localStorage.setItem(
      "misaka_desktop_notifications",
      desktopNotificationsEnabled,
    );
    if (desktopNotificationsEnabled && "Notification" in window) {
      Notification.requestPermission();
    }
  });

document.getElementById("settingsHUDToggle").addEventListener("change", (e) => {
  hudMode = e.target.checked;
  localStorage.setItem("misaka_hud_mode", hudMode);
  updateHUDButton();
});

document.getElementById("compactModeToggle").addEventListener("change", (e) => {
  compactMode = e.target.checked;
  localStorage.setItem("misaka_compact_mode", compactMode);
  document.body.classList.toggle("compact-mode", compactMode);
});

document.getElementById("wakeWordToggle").addEventListener("change", (e) => {
  if (!voiceWakeController) return;
  const started = voiceWakeController.setEnabled(e.target.checked);
  if (e.target.checked && !started) {
    e.target.checked = false;
  }
});
document.getElementById("btnClearAllData").addEventListener("click", () => {
  if (confirm("Tem certeza? Isso vai limpar todos os dados locais.")) {
    localStorage.clear();
    showToast("Dados locais limpos.", "success");
    location.reload();
  }
});

// Modal listeners
document.getElementById("btnModalApprove").addEventListener("click", () => {
  if (pendingConfirmation) {
    showToast("Ação aprovada.", "success");
  }
  hideConfirmation();
});

document.getElementById("btnModalDeny").addEventListener("click", () => {
  hideConfirmation();
  showToast("Ação negada.", "info");
});

modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) hideConfirmation();
});

// ==================== Initialize ====================
console.log("[Misaka] app.js loaded");
console.log("[Misaka] misakaDesktop:", window.misakaDesktop ? "available" : "not available");

if ("Notification" in window && Notification.permission === "default") {
  Notification.requestPermission();
}

// Load saved settings
document.getElementById("speakSuffixToggle").checked =
  localStorage.getItem("misaka_speak_suffix") !== "false";
document.getElementById("desktopNotificationsToggle").checked =
  desktopNotificationsEnabled;
document.getElementById("settingsHUDToggle").checked = hudMode;
document.getElementById("compactModeToggle").checked = compactMode;
document.getElementById("wakeWordToggle").checked =
  localStorage.getItem("wake_word_enabled") === "true";
if (compactMode) document.body.classList.add("compact-mode");
if (hudMode) document.body.classList.add("hud-mode");

loadStatus();
detectDesktopBridge().then(updateDesktopBridgeUI);
loadAlerts();
initVoiceControls();
updateVoiceButton();
updateHUDButton();
messageInput.focus();
initVoiceWakeController();

setInterval(loadStatus, MISAKA_CONFIG.POLL_INTERVAL_MS || 15000);
setInterval(loadAlerts, MISAKA_CONFIG.ALERTS_POLL_INTERVAL_MS || 10000);
