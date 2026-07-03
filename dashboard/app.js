const API_BASE = window.__MISAKA_API_BASE_URL__ || MISAKA_CONFIG.API_BASE_URL;

const $ = (id) => document.getElementById(id);

const chatMessages = $("chatMessages");
const messageInput = $("messageInput");
const btnSend = $("btnSend");
const btnClear = $("btnClear");
const btnVoice = $("btnVoice");
const btnHUD = $("btnHUD");
const btnSettings = $("btnSettings");
const btnCopyLast = $("btnCopyLast");
const btnSpeakLast = $("btnSpeakLast");
const typingIndicator = $("typingIndicator");
const coreVisualizer = $("coreVisualizer");
const voiceSelect = $("voiceSelect");
const voiceRateSlider = $("voiceRate");
const voicePitchSlider = $("voicePitch");
const rateValue = $("rateValue");
const pitchValue = $("pitchValue");
const voiceEnabledToggle = $("voiceEnabledToggle");
const autoSpeakToggle = $("autoSpeakToggle");
const btnTestVoice = $("btnTestVoice");
const btnStopVoice = $("btnStopVoice");
const btnWakeWord = $("btnWakeWord");
const voiceInputMode = $("voiceInputMode");
const voiceCommandMode = $("voiceCommandMode");
const voiceModeStatus = $("voiceModeStatus");
const btnTestMic = $("btnTestMic");
const btnTestTranscription = $("btnTestTranscription");
const settingsOverlay = $("settingsOverlay");
const settingsDrawer = $("settingsDrawer");
const btnCloseSettings = $("btnCloseSettings");
const toastContainer = $("toastContainer");
const approvalModal = $("approvalModal");
const wakeIndicator = $("wakeIndicator");
const wakeStatus = $("wakeStatus");
const wakeLastTranscript = $("wakeLastTranscript");
const wakeLastCommand = $("wakeLastCommand");
const wakeError = $("wakeError");
const wakeWordToggle = $("wakeWordToggle");

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
const lastToastByMessage = new Map();

const APP_DISPLAY_NAMES = {
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

function showToast(message, type = "info", duration = 4000) {
  if (!message || !toastContainer) return;
  const key = `${type}:${message}`;
  const lastAt = lastToastByMessage.get(key) || 0;
  if (Date.now() - lastAt < 2500) return;
  lastToastByMessage.set(key, Date.now());

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

function setText(id, value) {
  const element = $(id);
  if (element) element.textContent = value;
}

function setClass(id, value) {
  const element = $(id);
  if (element) element.className = value;
}

function setCoreState(state) {
  if (!coreVisualizer) return;
  coreVisualizer.className = "core-visualizer";
  if (state) coreVisualizer.classList.add(state);
}

function initVoiceControls() {
  if (voiceRateSlider) voiceRateSlider.value = voiceRate;
  if (voicePitchSlider) voicePitchSlider.value = voicePitch;
  if (rateValue) rateValue.textContent = voiceRate.toFixed(1);
  if (pitchValue) pitchValue.textContent = voicePitch.toFixed(1);
  if (voiceEnabledToggle) voiceEnabledToggle.checked = voiceEnabled;
  if (autoSpeakToggle) autoSpeakToggle.checked = autoSpeak;
  if (voiceInputMode) {
    voiceInputMode.value =
      localStorage.getItem("voice_input_mode") || "cloud_voice";
  }
  if (voiceCommandMode) {
    voiceCommandMode.value =
      localStorage.getItem("voice_command_mode") || "hybrid";
  }

  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = populateVoiceSelect;
    populateVoiceSelect();
  }
}

function populateVoiceSelect() {
  if (!voiceSelect || !("speechSynthesis" in window)) return;
  const voices = window.speechSynthesis.getVoices();
  voiceSelect.innerHTML = '<option value="">Default (pt-BR)</option>';
  const ordered = [
    ...voices.filter((voice) => voice.lang.includes("pt-BR")),
    ...voices.filter(
      (voice) => voice.lang.includes("pt") && !voice.lang.includes("pt-BR"),
    ),
    ...voices.filter((voice) => !voice.lang.includes("pt")),
  ];
  ordered.forEach((voice) => {
    const option = document.createElement("option");
    option.value = voice.name;
    option.textContent = `${voice.name}${voice.localService ? " (local)" : ""}`;
    option.selected = voice.name === selectedVoiceName;
    voiceSelect.appendChild(option);
  });
}

function getSelectedVoice() {
  if (!("speechSynthesis" in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (selectedVoiceName) {
    const found = voices.find((voice) => voice.name === selectedVoiceName);
    if (found) return found;
  }
  return (
    voices.find((voice) => voice.lang.includes("pt-BR")) ||
    voices.find((voice) => voice.lang.includes("pt")) ||
    voices[0] ||
    null
  );
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  if (!voiceEnabled && !autoSpeak) return;
  if (!text) return;

  window.speechSynthesis.cancel();
  speaking = false;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "pt-BR";
  utterance.rate = voiceRate;
  utterance.pitch = voicePitch;
  const voice = getSelectedVoice();
  if (voice) utterance.voice = voice;

  utterance.onstart = () => {
    speaking = true;
    setCoreState("speaking");
  };
  utterance.onend = () => {
    speaking = false;
    setCoreState(null);
  };
  utterance.onerror = (event) => {
    speaking = false;
    setCoreState(null);
    if (event.error !== "canceled") {
      showToast(`Erro de voz: ${event.error}`, "warning");
    }
  };

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

function stopVoice() {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  speaking = false;
  currentUtterance = null;
  setCoreState(null);
  showToast("Voz parada.", "info");
}

function testVoice() {
  speak(`Olá, eu sou a Misaka.\nEsta é minha voz.`);
}

function updateVoiceButton() {
  if (!btnVoice) return;
  btnVoice.style.color = voiceEnabled
    ? "var(--color-primary)"
    : "var(--color-muted)";
}

function updateHUDButton() {
  if (btnHUD) {
    btnHUD.style.color = hudMode
      ? "var(--color-primary)"
      : "var(--color-muted)";
  }
  document.body.classList.toggle("hud-mode", hudMode);
}

function showProviderStatus(provider, model, fallbackActive) {
  document
    .querySelectorAll(".mock-warning, .gemini-active, .gemini-fallback")
    .forEach((element) => element.remove());
  const chatSection = document.querySelector(".chat-section");
  if (!chatSection) return;

  const banner = document.createElement("div");
  if (provider === "mock") {
    banner.className = "mock-warning";
    banner.textContent = `Misaka está em modo simulação.\nConfigure GEMINI_API_KEY para respostas inteligentes.`;
  } else if (provider === "gemini" && fallbackActive) {
    banner.className = "gemini-fallback";
    banner.textContent = `Usando ${model} temporariamente (fallback ativo)`;
  } else if (provider === "gemini") {
    banner.className = "gemini-active";
    banner.textContent = `Gemini ativo - ${model}`;
  } else {
    return;
  }
  chatSection.prepend(banner);
}

async function loadStatus() {
  try {
    const response = await fetch(`${API_BASE}/overview`);
    const data = await response.json();
    currentProvider = data.llm_provider;
    currentModel = data.llm_model;

    setText("version", `v${data.version}`);
    setText("llmProvider", data.llm_provider);
    setText("llmModel", data.llm_model);
    setText("providerBadge", data.llm_provider);
    setText("memoryStatus", data.memory_enabled ? "Enabled" : "Disabled");
    setText("calendarStatus", data.calendar_enabled ? "Enabled" : "Disabled");
    setText("toolsStatus", data.tools_enabled ? "Enabled" : "Disabled");
    setText(
      "notificationsStatus",
      data.notifications_enabled ? "Enabled" : "Disabled",
    );
    setText("memoryModule", data.memory_enabled ? "Active" : "Disabled");
    setText("calendarModule", data.calendar_enabled ? "Active" : "Disabled");
    setText("llmStatus", data.llm_provider === "mock" ? "Mock" : "Active");
    setText(
      "desktopModule",
      window.misakaDesktop?.isAvailable ? "Online" : "Web",
    );
    setText(
      "androidModule",
      data.android_bridge_enabled ? "Online" : "Offline",
    );
    setClass(
      "memoryModule",
      `module-status ${data.memory_enabled ? "online" : ""}`,
    );
    setClass(
      "calendarModule",
      `module-status ${data.calendar_enabled ? "online" : ""}`,
    );
    setClass(
      "desktopModule",
      `module-status ${window.misakaDesktop?.isAvailable ? "online" : ""}`,
    );
    showProviderStatus(
      data.llm_provider,
      data.llm_model,
      data.llm_fallback_active,
    );
  } catch (error) {
    setText("statusIndicator", "Offline");
  }
}

function addMessage(text, type) {
  if (!chatMessages) return;
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
    type === "assistant" ? cleanAssistantText(text) : String(text || "");
  bodyDiv.appendChild(contentDiv);
  messageDiv.appendChild(bodyDiv);
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  lastResponse = text;
}

function cleanAssistantText(text) {
  return String(text || "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/__(.+?)__/g, "$1")
    .replace(/_(.+?)_/g, "$1")
    .replace(/`(.+?)`/g, "$1")
    .replace(/~~(.+?)~~/g, "$1")
    .replace(/#{1,6}\s*/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function safeUrl(url) {
  try {
    const parsed = new URL(url);
    if (!["http:", "https:"].includes(parsed.protocol)) return "";
    return parsed.toString();
  } catch (_) {
    return "";
  }
}

async function openUrlAction(url) {
  const targetUrl = safeUrl(url);
  if (!targetUrl) return { success: false, error: "URL inválida." };

  if (window.misakaDesktop?.openUrl) {
    return window.misakaDesktop.openUrl(targetUrl);
  }

  try {
    const opened = window.open(targetUrl, "_blank", "noopener,noreferrer");
    if (opened) return { success: true, method: "window.open", url: targetUrl };

    const anchor = document.createElement("a");
    anchor.href = targetUrl;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    return { success: true, method: "anchor-fallback", url: targetUrl };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function buildSearchUrl(query, provider = "google") {
  const encoded = encodeURIComponent(String(query || "").trim());
  const urls = {
    google: `https://www.google.com/search?q=${encoded}`,
    youtube: `https://www.youtube.com/results?search_query=${encoded}`,
    github: `https://github.com/search?q=${encoded}&type=repositories`,
    reddit: `https://www.reddit.com/search/?q=${encoded}`,
    modrinth: `https://modrinth.com/mods?q=${encoded}`,
    curseforge: `https://www.curseforge.com/minecraft/search?search=${encoded}`,
  };
  return urls[provider] || urls.google;
}

function actionResult(action, success, message, extra = {}) {
  return {
    success: Boolean(success),
    type: action?.type || "",
    message,
    error: extra.error || null,
    action,
    ...extra,
  };
}

async function handleClientAction(action) {
  if (!action || !action.type) {
    return actionResult(action, true, "");
  }

  if (action.type === "open_url") {
    const result = await openUrlAction(action.url);
    if (result?.success) {
      return actionResult(
        action,
        true,
        "Página aberta, diz Misaka Misaka.",
        result,
      );
    }
    const error = result?.error || "erro desconhecido";
    return actionResult(
      action,
      false,
      `Não consegui abrir a página. Motivo: ${error}, diz Misaka Misaka.`,
      { error },
    );
  }

  if (action.type === "open_app") {
    const appName = action.app || action.name || "";
    const appLabel = APP_DISPLAY_NAMES[appName] || appName || "aplicativo";
    if (!window.misakaDesktop?.openApp) {
      const error = "use o app desktop da Misaka para abrir aplicativos locais";
      return actionResult(
        action,
        false,
        `Não consegui abrir ${appLabel}. Motivo: ${error}, diz Misaka Misaka.`,
        { error },
      );
    }

    const result = await window.misakaDesktop.openApp(appName);
    if (result?.success) {
      return actionResult(
        action,
        true,
        `${appLabel} aberto no seu computador, diz Misaka Misaka.`,
        result,
      );
    }
    const error = result?.error || "app não encontrado";
    return actionResult(
      action,
      false,
      `Não consegui abrir ${appLabel}. Motivo: ${error}, diz Misaka Misaka.`,
      { error },
    );
  }

  if (action.type === "search_web" || action.type === "search_youtube") {
    const provider =
      action.type === "search_youtube"
        ? "youtube"
        : action.provider || "google";
    const url = action.url || buildSearchUrl(action.query, provider);
    const result = await openUrlAction(url);
    if (result?.success) {
      return actionResult(
        action,
        true,
        "Página aberta, diz Misaka Misaka.",
        result,
      );
    }
    const error = result?.error || "erro desconhecido";
    return actionResult(
      action,
      false,
      `Não consegui pesquisar. Motivo: ${error}, diz Misaka Misaka.`,
      { error },
    );
  }

  if (action.type === "show_notification") {
    const title = action.title || "Misaka";
    const body = action.message || action.body || "";
    if (window.misakaDesktop?.showNotification) {
      const result = await window.misakaDesktop.showNotification(title, body);
      return actionResult(
        action,
        result?.success,
        body || "Notificação enviada.",
        result || {},
      );
    }
    showToast(body || title, "info");
    return actionResult(action, true, body || "Notificação exibida.");
  }

  if (action.type === "set_hud") {
    hudMode = Boolean(action.enabled);
    localStorage.setItem("misaka_hud_mode", String(hudMode));
    updateHUDButton();
    if (window.misakaDesktop?.setHudMode) {
      await window.misakaDesktop.setHudMode(hudMode);
    }
    return actionResult(
      action,
      true,
      hudMode
        ? "HUD ativado, diz Misaka Misaka."
        : "HUD desativado, diz Misaka Misaka.",
    );
  }

  if (action.type === "open_settings") {
    openSettings();
    return actionResult(
      action,
      true,
      "Configurações abertas, diz Misaka Misaka.",
    );
  }

  if (action.type === "clear_chat") {
    clearChat();
    return actionResult(
      action,
      true,
      "Conversa reiniciada, diz Misaka Misaka.",
    );
  }

  if (action.type === "refresh_alerts") {
    await loadAlerts();
    return actionResult(
      action,
      true,
      "Alertas atualizados, diz Misaka Misaka.",
    );
  }

  if (action.type === "speak") {
    speak(action.text || action.message || "");
    return actionResult(action, true, "");
  }

  if (
    action.type === "get_system_status" &&
    window.misakaDesktop?.getSystemStatus
  ) {
    const status = await window.misakaDesktop.getSystemStatus();
    return actionResult(
      action,
      true,
      `PC: ${status.platform} | RAM: ${Math.round(status.memory?.heapUsed / 1024 / 1024 || 0)}MB`,
      status,
    );
  }

  if (action.type === "show_toast") {
    showToast(action.message || "Alerta da Misaka", "info");
    return actionResult(action, true, "");
  }

  return actionResult(action, false, "", { error: "Ação desconhecida." });
}

function processUiEffect(effect) {
  if (!effect || effect === "none") return;
  if (effect === "clear_chat") clearChat();
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
    if (voiceEnabledToggle) voiceEnabledToggle.checked = true;
    updateVoiceButton();
  }
  if (effect === "disable_voice") {
    voiceEnabled = false;
    localStorage.setItem("misaka_voice_enabled", "false");
    if (voiceEnabledToggle) voiceEnabledToggle.checked = false;
    updateVoiceButton();
  }
  if (effect === "refresh_alerts") loadAlerts();
  if (effect === "refresh_status") loadStatus();
  if (effect === "open_settings") openSettings();
}

async function sendMessage(messageOverride = null, options = {}) {
  const source = options.source || "text";
  const fromVoice = ["voice", "native_voice", "cloud_voice"].includes(source);
  const message =
    typeof messageOverride === "string"
      ? messageOverride.trim()
      : messageInput?.value.trim() || "";
  if (!message) return null;

  if (!options.silentUserMessage) addMessage(message, "user");
  if (!options.skipInputClear && !fromVoice && messageInput) {
    messageInput.value = "";
    messageInput.style.height = "auto";
  }

  setCoreState("thinking");
  typingIndicator?.classList.add("active");
  if (btnSend) btnSend.disabled = true;

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        metadata: { source },
      }),
    });

    const data = await response.json();
    conversationId = data.conversation_id;
    processUiEffect(data.metadata?.ui_effect);

    let assistantResponse = data.response || "";
    const clientAction = data.metadata?.client_action;
    if (clientAction) {
      const result = await handleClientAction(clientAction);
      assistantResponse = result.message || assistantResponse;
    }

    if (assistantResponse) {
      addMessage(assistantResponse, "assistant");
      if (voiceEnabled && (autoSpeak || fromVoice)) speak(assistantResponse);
    }

    setCoreState("speaking");
    setTimeout(() => setCoreState(null), 1200);
    return data;
  } catch (error) {
    const messageText = `Erro ao conectar com o servidor: ${error.message}`;
    addMessage(messageText, "system");
    showToast(messageText, "error");
    setCoreState(null);
    return { success: false, error: error.message };
  } finally {
    typingIndicator?.classList.remove("active");
    if (btnSend) btnSend.disabled = false;
    messageInput?.focus();
  }
}

function clearChat() {
  if (!chatMessages) return;
  chatMessages.innerHTML = "";
  conversationId = null;
  addMessage(`Conversa reiniciada.\nComo posso ajudar?`, "system");
}

function copyToClipboard(text) {
  navigator.clipboard
    ?.writeText(text)
    .then(() => showToast("Copiado!", "success"))
    .catch(() => showToast("Erro ao copiar.", "error"));
}

async function loadAlerts() {
  const alertsContainer = $("alertsContainer");
  const alertsCount = $("alertsCount");
  if (!alertsContainer) return;
  try {
    const response = await fetch(`${API_BASE}/notifications/alerts`);
    const data = await response.json();
    const alerts = Array.isArray(data.alerts) ? data.alerts : [];
    alertsCount && (alertsCount.textContent = String(alerts.length));
    alertsContainer.textContent = "";

    const filtered =
      currentAlertFilter === "all"
        ? alerts
        : alerts.filter(
            (alert) =>
              alert.status === currentAlertFilter ||
              alert.priority === currentAlertFilter,
          );

    if (filtered.length === 0) {
      const emptyDiv = document.createElement("div");
      emptyDiv.className = "alert-empty";
      emptyDiv.textContent = "No alerts";
      alertsContainer.appendChild(emptyDiv);
      return;
    }

    filtered.slice(0, 10).forEach((alert) => {
      const alertDiv = document.createElement("div");
      alertDiv.className = `alert-item alert-${alert.priority}`;
      const titleSpan = document.createElement("span");
      titleSpan.className = "alert-title";
      titleSpan.textContent = alert.title;
      const messageSpan = document.createElement("span");
      messageSpan.className = "alert-message";
      messageSpan.textContent = alert.message;
      alertDiv.appendChild(titleSpan);
      alertDiv.appendChild(messageSpan);
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
  } catch (error) {
    alertsContainer.textContent = "";
    const emptyDiv = document.createElement("div");
    emptyDiv.className = "alert-empty";
    emptyDiv.textContent = "Backend offline";
    alertsContainer.appendChild(emptyDiv);
  }
}

async function ackAllAlerts() {
  try {
    const response = await fetch(`${API_BASE}/notifications/alerts/ack-all`, {
      method: "POST",
    });
    const data = await response.json();
    showToast(data.message || "Alertas marcados como vistos.", "success");
    await loadAlerts();
  } catch (_) {
    showToast("Erro ao limpar alertas.", "error");
  }
}

function openSettings() {
  settingsOverlay?.classList.add("active");
  settingsDrawer?.classList.add("active");
  loadSettingsInfo();
}

function closeSettings() {
  settingsOverlay?.classList.remove("active");
  settingsDrawer?.classList.remove("active");
}

async function loadSettingsInfo() {
  try {
    const response = await fetch(`${API_BASE}/llm/status`);
    const data = await response.json();
    setText("settingsLlmStatus", data.provider || "-");
    setText("settingsVersion", currentModel || "-");
  } catch (_) {
    setText("settingsLlmStatus", "Offline");
  }
  setText(
    "settingsDesktopBridge",
    window.misakaDesktop?.isAvailable ? "Online" : "Web mode",
  );
  try {
    const response = await fetch(`${API_BASE}/android/status`);
    const data = await response.json();
    setText(
      "settingsAndroidBridge",
      data.connected ? "Connected" : "Disconnected",
    );
  } catch (_) {
    setText("settingsAndroidBridge", "-");
  }
}

async function initVoiceWake() {
  if (!window.VoiceWakeController) {
    updateWakeUI("unavailable", "Controlador de voz não carregado.");
    return;
  }

  voiceWakeController = new VoiceWakeController({
    apiBase: API_BASE,
    elements: {
      button: btnWakeWord,
      toggle: wakeWordToggle,
      mode: voiceInputMode,
      commandMode: voiceCommandMode,
      modeLabel: voiceModeStatus,
      status: wakeStatus,
      lastTranscript: wakeLastTranscript,
      lastCommand: wakeLastCommand,
      error: wakeError,
      indicator: wakeIndicator,
    },
    callbacks: {
      onCommand: sendVoiceCommand,
      onStateChange: updateWakeUI,
      onTranscript: updateWakeTranscript,
      onError: (_error, message) => {
        if (message) showToast(message, "warning");
      },
      onWakeDetected: () => showToast("Misaka detectada.", "info", 1600),
    },
  });

  const result = await voiceWakeController.init();
  if (!result.success && result.error) showToast(result.error, "warning");

  if (window.misakaDesktop?.onWakeWordSetEnabled) {
    window.misakaDesktop.onWakeWordSetEnabled((enabled) => {
      setWakeWordEnabled(Boolean(enabled));
    });
  }
}

function updateWakeUI(state, label) {
  const active = [
    "requesting_microphone",
    "microphone_ready",
    "recording",
    "transcribing",
    "processing_command",
    "listening",
    "listening_for_wake",
    "wake_detected",
    "listening_for_command",
  ].includes(state);
  if (btnWakeWord) {
    btnWakeWord.style.opacity = state === "unavailable" ? "0.6" : "1";
    btnWakeWord.style.color = active
      ? "var(--color-primary)"
      : "var(--color-muted)";
  }
  if (wakeStatus && label) wakeStatus.textContent = label;
}

function updateWakeTranscript(text) {
  if (wakeLastTranscript) {
    wakeLastTranscript.textContent = text
      ? `Último ouvido: ${text}`
      : "Último ouvido: -";
  }
}

function updateWakeCommand(command) {
  if (wakeLastCommand) {
    wakeLastCommand.textContent = command
      ? `Comando: ${command}`
      : "Comando: -";
  }
}

function sendVoiceCommand(command) {
  updateWakeCommand(command);
  return sendMessage(command, { source: "voice" });
}

async function setWakeWordEnabled(enabled) {
  if (!voiceWakeController)
    return { success: false, error: "Voz não inicializada." };
  const result = await voiceWakeController.setEnabled(Boolean(enabled));
  if (enabled && !result.success) {
    if (wakeWordToggle) wakeWordToggle.checked = false;
    showToast(result.error || "Não consegui ativar a escuta.", "warning");
  } else if (enabled) {
    showToast(`Escuta ativada.\nModo principal: Cloud Voice.`, "info");
  } else {
    showToast("Escuta desativada.", "info");
  }
  return result;
}

function toggleWakeWord() {
  if (!voiceWakeController) return;
  setWakeWordEnabled(!voiceWakeController.enabled);
}

async function testMicrophone() {
  if (!voiceWakeController) return;
  const result = await voiceWakeController.requestMicrophone();
  if (result.success) {
    voiceWakeController.stopMediaStream();
    showToast("Microfone permitido.", "success");
  } else {
    showToast(result.error, "warning");
  }
}

async function testTranscription() {
  if (!voiceWakeController) return;
  const result = await voiceWakeController.fetchVoiceStatus();
  if (!result.success) {
    showToast(result.error, "warning");
    return;
  }
  if (!result.data.ready) {
    showToast(
      result.data.last_error ||
        "Transcrição de voz não configurada no backend.",
      "warning",
    );
    return;
  }
  showToast(`Cloud Voice pronto (${result.data.provider}).`, "success");
}

function bindEvents() {
  messageInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
  messageInput?.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 120)}px`;
  });
  btnSend?.addEventListener("click", () => sendMessage());
  btnClear?.addEventListener("click", clearChat);
  btnVoice?.addEventListener("click", () => {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem("misaka_voice_enabled", String(voiceEnabled));
    if (voiceEnabledToggle) voiceEnabledToggle.checked = voiceEnabled;
    updateVoiceButton();
    showToast(voiceEnabled ? "Voz ativada." : "Voz desativada.", "info");
  });
  btnHUD?.addEventListener("click", async () => {
    hudMode = !hudMode;
    localStorage.setItem("misaka_hud_mode", String(hudMode));
    updateHUDButton();
    if (window.misakaDesktop?.setHudMode) {
      await window.misakaDesktop.setHudMode(hudMode);
    }
    showToast(hudMode ? "HUD ativado." : "HUD desativado.", "info");
  });
  btnCopyLast?.addEventListener("click", () => {
    if (lastResponse) copyToClipboard(lastResponse);
  });
  btnSpeakLast?.addEventListener("click", () => {
    if (lastResponse) speak(lastResponse);
  });
  btnTestVoice?.addEventListener("click", testVoice);
  btnStopVoice?.addEventListener("click", stopVoice);
  btnWakeWord?.addEventListener("click", toggleWakeWord);
  btnTestMic?.addEventListener("click", testMicrophone);
  btnTestTranscription?.addEventListener("click", testTranscription);

  voiceSelect?.addEventListener("change", (event) => {
    selectedVoiceName = event.target.value;
    localStorage.setItem("misaka_voice_name", selectedVoiceName);
  });
  voiceRateSlider?.addEventListener("input", (event) => {
    voiceRate = parseFloat(event.target.value);
    if (rateValue) rateValue.textContent = voiceRate.toFixed(1);
    localStorage.setItem("misaka_voice_rate", String(voiceRate));
  });
  voicePitchSlider?.addEventListener("input", (event) => {
    voicePitch = parseFloat(event.target.value);
    if (pitchValue) pitchValue.textContent = voicePitch.toFixed(1);
    localStorage.setItem("misaka_voice_pitch", String(voicePitch));
  });
  voiceEnabledToggle?.addEventListener("change", (event) => {
    voiceEnabled = event.target.checked;
    localStorage.setItem("misaka_voice_enabled", String(voiceEnabled));
    updateVoiceButton();
  });
  autoSpeakToggle?.addEventListener("change", (event) => {
    autoSpeak = event.target.checked;
    localStorage.setItem("misaka_auto_speak", String(autoSpeak));
  });
  voiceInputMode?.addEventListener("change", (event) => {
    voiceWakeController?.setMode(event.target.value);
  });
  voiceCommandMode?.addEventListener("change", (event) => {
    voiceWakeController?.setCommandMode(event.target.value);
  });
  wakeWordToggle?.addEventListener("change", (event) => {
    setWakeWordEnabled(event.target.checked);
  });

  btnSettings?.addEventListener("click", openSettings);
  btnCloseSettings?.addEventListener("click", closeSettings);
  settingsOverlay?.addEventListener("click", closeSettings);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeSettings();
  });

  document.querySelectorAll(".filter-btn").forEach((button) => {
    button.addEventListener("click", () => {
      document
        .querySelectorAll(".filter-btn")
        .forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      currentAlertFilter = button.dataset.filter;
      loadAlerts();
    });
  });

  $("btnAckAll")?.addEventListener("click", ackAllAlerts);
  $("btnRefreshAlerts")?.addEventListener("click", loadAlerts);
  $("settingsVoiceEnabled")?.addEventListener("change", (event) => {
    voiceEnabled = event.target.checked;
    localStorage.setItem("misaka_voice_enabled", String(voiceEnabled));
    if (voiceEnabledToggle) voiceEnabledToggle.checked = voiceEnabled;
    updateVoiceButton();
  });
  $("settingsAutoSpeak")?.addEventListener("change", (event) => {
    autoSpeak = event.target.checked;
    localStorage.setItem("misaka_auto_speak", String(autoSpeak));
    if (autoSpeakToggle) autoSpeakToggle.checked = autoSpeak;
  });
  $("settingsHudMode")?.addEventListener("change", (event) => {
    hudMode = event.target.checked;
    localStorage.setItem("misaka_hud_mode", String(hudMode));
    updateHUDButton();
  });
  $("settingsCompactMode")?.addEventListener("change", (event) => {
    compactMode = event.target.checked;
    localStorage.setItem("misaka_compact_mode", String(compactMode));
    document.body.classList.toggle("compact-mode", compactMode);
  });
  $("settingsDesktopNotifications")?.addEventListener("change", (event) => {
    desktopNotificationsEnabled = event.target.checked;
    localStorage.setItem(
      "misaka_desktop_notifications",
      String(desktopNotificationsEnabled),
    );
    if (desktopNotificationsEnabled && "Notification" in window) {
      Notification.requestPermission();
    }
  });
}

function hydrateSettings() {
  $("settingsVoiceEnabled") &&
    ($("settingsVoiceEnabled").checked = voiceEnabled);
  $("settingsAutoSpeak") && ($("settingsAutoSpeak").checked = autoSpeak);
  $("settingsHudMode") && ($("settingsHudMode").checked = hudMode);
  $("settingsCompactMode") && ($("settingsCompactMode").checked = compactMode);
  $("settingsDesktopNotifications") &&
    ($("settingsDesktopNotifications").checked = desktopNotificationsEnabled);
  if (wakeWordToggle) {
    wakeWordToggle.checked =
      localStorage.getItem("wake_word_enabled") === "true";
  }
  document.body.classList.toggle("compact-mode", compactMode);
  document.body.classList.toggle("hud-mode", hudMode);
}

if ("Notification" in window && Notification.permission === "default") {
  Notification.requestPermission();
}

bindEvents();
hydrateSettings();
loadStatus();
loadAlerts();
initVoiceControls();
updateVoiceButton();
updateHUDButton();
messageInput?.focus();
initVoiceWake();

setInterval(loadStatus, MISAKA_CONFIG.POLL_INTERVAL_MS || 15000);
setInterval(loadAlerts, MISAKA_CONFIG.ALERTS_POLL_INTERVAL_MS || 10000);
