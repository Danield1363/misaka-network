(function (root) {
  const DEFAULT_WAKE_PHRASES = [
    "misaka",
    "ei misaka",
    "ok misaka",
    "acorda misaka",
  ];

  const STATES = {
    unavailable: "unavailable",
    off: "off",
    checking: "checking",
    permission_needed: "permission_needed",
    listening_for_wake: "listening_for_wake",
    wake_detected: "wake_detected",
    listening_for_command: "listening_for_command",
    processing: "processing",
    speaking: "speaking",
    error: "error",
  };

  const STATE_LABELS = {
    unavailable: "Wake: indisponivel",
    off: "Wake: desligado",
    checking: "Wake: verificando modos...",
    permission_needed: "Wake: permissao necessaria",
    listening_for_wake: 'Wake: ouvindo por "Misaka"',
    wake_detected: "Wake: palavra detectada",
    listening_for_command: "Wake: capturando comando",
    processing: "Wake: processando",
    speaking: "Wake: falando",
    error: "Wake: erro",
  };

  const FATAL_ERRORS = new Set([
    "not-allowed",
    "service-not-allowed",
    "audio-capture",
    "network",
    "language-not-supported",
  ]);

  function normalizeVoiceText(text) {
    return String(text || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^\w\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function extractCommandFromWakePhrase(
    text,
    wakePhrases = DEFAULT_WAKE_PHRASES,
  ) {
    const raw = String(text || "").trim();
    if (!raw) return null;

    const normalized = normalizeVoiceText(raw);
    const phrases = wakePhrases
      .map(normalizeVoiceText)
      .sort((a, b) => b.length - a.length);

    const matchedPhrase = phrases.find(
      (phrase) => normalized === phrase || normalized.startsWith(`${phrase} `),
    );
    if (!matchedPhrase) return null;

    const rawPattern = /^\s*(?:(?:ei|ok|acorda)\s+)?misaka\b[\s,.;:!?-]*/i;
    return raw.replace(rawPattern, "").trim();
  }

  // --- Direct Command Detection ---

  const DIRECT_VERBS = [
    "abrir", "abra", "abre", "iniciar", "inicia",
    "executar", "execute", "rodar", "roda", "rode",
    "pesquisar", "pesquise", "procurar", "procure",
    "buscar", "busque",
    "ative", "ativar", "desative", "desativar",
    "limpe", "limpar", "mostrar", "mostre",
    "atualizar", "atualize",
    "abra", "abrir",
  ];

  const DANGEROUS_PATTERNS = [
    "desligar\\s+(o\\s+)?computador",
    "desligar\\s+pc",
    "reiniciar\\s+(o\\s+)?computador",
    "reiniciar\\s+pc",
    "apagar\\s+arquivo",
    "deletar\\s+arquivo",
    "formatar",
    "executar\\s+comando",
    "rodar\\s+script",
    "enviar\\s+mensagem",
    "comprar",
    "pagar",
    "remover\\s+(o\\s+)?sistema",
  ];

  const SAFE_PREFIXES = [
    "abrir", "abra", "abre", "iniciar", "inicia",
    "executar", "execute", "rodar", "roda", "rode",
    "pesquisar", "pesquise", "procurar", "procure",
    "buscar", "busque",
    "ative", "ativar", "desative", "desativar",
    "limpe", "limpar", "mostrar", "mostre",
    "atualizar", "atualize",
  ];

  function isDirectVoiceCommand(text) {
    const normalized = normalizeVoiceText(text);
    if (!normalized) return false;

    for (const verb of SAFE_PREFIXES) {
      if (normalized.startsWith(verb + " ") || normalized === verb) {
        return true;
      }
    }
    return false;
  }

  function extractDirectVoiceCommand(text) {
    const normalized = normalizeVoiceText(text);
    if (!normalized) return null;

    for (const verb of SAFE_PREFIXES) {
      if (normalized.startsWith(verb + " ")) {
        return normalized;
      }
      if (normalized === verb) {
        return normalized;
      }
    }
    return null;
  }

  function classifyVoiceCommand(text) {
    const normalized = normalizeVoiceText(text);
    if (!normalized) return { matched: false };

    for (const pattern of DANGEROUS_PATTERNS) {
      if (new RegExp(pattern).test(normalized)) {
        return {
          matched: true,
          command: normalized,
          mode: "direct_command",
          risk: "dangerous",
          requires_confirmation: true,
        };
      }
    }

    for (const verb of SAFE_PREFIXES) {
      if (normalized.startsWith(verb + " ") || normalized === verb) {
        return {
          matched: true,
          command: normalized,
          mode: "direct_command",
          risk: "safe",
          requires_confirmation: false,
        };
      }
    }

    return { matched: false };
  }

  function isWebSpeechSupported(win) {
    const w = win || root;
    return Boolean(w.SpeechRecognition || w.webkitSpeechRecognition);
  }

  function isNativeDesktopSupported(win) {
    const w = win || root;
    const bridge = w.misakaDesktop;
    return Boolean(
      bridge &&
        bridge.isAvailable &&
        typeof bridge.nativeVoiceIsAvailable === "function" &&
        typeof bridge.nativeVoiceStart === "function" &&
        typeof bridge.nativeVoiceStop === "function",
    );
  }

  function chooseVoiceWakeMode(win) {
    if (isWebSpeechSupported(win)) return "web_speech";
    if (isNativeDesktopSupported(win)) return "native_desktop";
    return "unavailable";
  }

  class VoiceWakeController {
    constructor(options = {}) {
      this.elements = options.elements || {};
      this.storage = options.storage || root.localStorage;

      this.onStateChange =
        options.onStateChange ||
        options.callbacks?.onStateChange ||
        options.callbacks?.onStatusChange;
      this.onTranscript = options.onTranscript || options.callbacks?.onTranscript;
      this.onCommand = options.onCommand || options.callbacks?.onCommand;
      this.onError = options.onError || options.callbacks?.onError;
      this.onWakeDetected =
        options.onWakeDetected || options.callbacks?.onWakeDetected;
      this.onDebug = options.onDebug || options.callbacks?.onDebug;
      this.sendCommandCallback =
        options.sendVoiceCommand || options.callbacks?.sendVoiceCommand;

      this.recognition = null;
      this.enabled = false;
      this.active = false;
      this.starting = false;
      this.stoppedByUser = true;
      this.restartTimer = null;
      this.commandCaptureTimer = null;
      this.waitingForCommand = false;
      this.state = STATES.off;
      this.lastTranscript = "";
      this.lastCommand = "";
      this.lastError = "";
      this.voiceMode = "unavailable";
      this._nativeCleanups = [];
      this.voiceCommandMode = "hybrid";
      this.lastExecutedCommand = "";
      this.lastExecutedAt = 0;
      this._daemonWs = null;
      this._daemonUrl = "ws://127.0.0.1:8765";
      this._daemonConnected = false;

      this.settings = {
        wake_phrases: DEFAULT_WAKE_PHRASES.slice(),
        wake_language: "pt-BR",
        wake_auto_restart: true,
        wake_command_timeout_ms: 8000,
        wake_start_on_launch: false,
        voice_command_mode: "hybrid",
        voice_command_debounce_ms: 2500,
      };
    }

    // --- Initialization ---

    init() {
      this.loadSettings();
      this.voiceMode = chooseVoiceWakeMode();

      if (this.voiceMode === "unavailable") {
        this.enabled = false;
        this.persistSettings();
        this.updateState(STATES.unavailable, this._getUnavailableMessage());
        return false;
      }

      this.updateState(STATES.off);
      if (this.settings.wake_start_on_launch || this.enabled) {
        return this.start();
      }
      return true;
    }

    chooseMode() {
      return chooseVoiceWakeMode();
    }

    isWebSpeechSupported() {
      return isWebSpeechSupported();
    }

    isNativeDesktopSupported() {
      return isNativeDesktopSupported();
    }

    // --- Start / Stop ---

    async start() {
      if (this.active || this.starting) {
        return { success: true, mode: this.voiceMode, message: "Escuta ja ativa." };
      }

      this.voiceMode = chooseVoiceWakeMode();
      const isElectron = !!(root.misakaDesktop && root.misakaDesktop.isAvailable);
      this.debug(`start: mode=${this.voiceMode} electron=${isElectron}`);

      // Priority: daemon first (always), then Web Speech
      this.updateState(STATES.checking, "Conectando ao daemon de voz...");
      const daemonConnected = await this.connectDaemon();
      if (daemonConnected) {
        this.voiceMode = "daemon_websocket";
        this.enabled = true;
        this.active = true;
        this.persistSettings();
        this.updateState(STATES.listening_for_wake, "Wake: conectado ao daemon");
        return { success: true, mode: "daemon", message: "Escuta ativada via daemon local." };
      }

      // If in Electron and daemon failed, don't try Web Speech
      if (isElectron) {
        this.updateState(STATES.unavailable, "Modo nativo de voz nao disponivel. Configure o Misaka Voice Daemon.");
        return { success: false, mode: "unavailable", error: "Modo nativo de voz nao disponivel. Configure o Misaka Voice Daemon." };
      }

      // Web Speech only in browser
      if (this.voiceMode === "web_speech") {
        const webResult = this.startWebSpeech();
        if (webResult) {
          return { success: true, mode: "web_speech", message: "Escuta ativada via Web Speech." };
        }
        return { success: false, mode: "web_speech", error: this.lastError || "Web Speech nao iniciou." };
      }

      if (this.voiceMode === "native_desktop") {
        const nativeResult = await this.startNativeDesktop();
        if (nativeResult) {
          return { success: true, mode: "native_desktop", message: "Escuta ativada via modo nativo." };
        }
        return { success: false, mode: "native_desktop", error: this.lastError || "Modo nativo nao iniciou." };
      }

      this.updateState(STATES.unavailable, this._getUnavailableMessage());
      return { success: false, mode: "unavailable", error: this._getUnavailableMessage() };
    }

    stop() {
      this.enabled = false;
      this.active = false;
      this.starting = false;
      this.stoppedByUser = true;
      this.waitingForCommand = false;
      this.clearRestartTimer();
      this.clearCommandTimer();

      if (this.voiceMode === "web_speech") {
        this.stopRecognitionOnly();
      } else if (this.voiceMode === "native_desktop") {
        this.stopNativeDesktop();
      } else if (this.voiceMode === "daemon_websocket") {
        this.disconnectDaemon();
      }

      this.persistSettings();
      this.updateState(STATES.off);
    }

    async restart() {
      if (this.voiceMode === "web_speech") {
        this.stopRecognitionOnly();
      } else if (this.voiceMode === "native_desktop") {
        this.stopNativeDesktop();
      }
      this.active = false;
      this.starting = false;
      if (!this.enabled) return false;
      return await this.start();
    }

    async setEnabled(enabled) {
      this.debug(`setEnabled(${enabled})`);
      if (enabled) {
        this.updateState(STATES.checking, "Verificando reconhecimento de voz...");
        return await this.start();
      }
      this.stop();
      return { success: true, mode: "off", message: "Escuta desativada." };
    }

    // --- Web Speech Mode ---

    startWebSpeech() {
      if (!isWebSpeechSupported()) {
        this.updateState(STATES.unavailable, "Web Speech nao disponivel.");
        return false;
      }

      this.clearRestartTimer();
      this.stopRecognitionOnly();
      this.starting = true;
      this.stoppedByUser = false;

      const Recognition = root.SpeechRecognition || root.webkitSpeechRecognition;
      this.recognition = new Recognition();
      this.recognition.lang = this.settings.wake_language;
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;
      this.recognition.onresult = (event) => this.handleResult(event);
      this.recognition.onerror = (event) => this.handleError(event);
      this.recognition.onend = () => this.handleEnd();

      try {
        this.recognition.start();
        this.enabled = true;
        this.active = true;
        this.starting = false;
        this.persistSettings();
        this.updateState(STATES.listening_for_wake, "Wake: usando Web Speech");
        return true;
      } catch (error) {
        this.enabled = false;
        this.active = false;
        this.starting = false;
        this.persistSettings();
        this.updateState(
          STATES.error,
          `Wake word falhou ao iniciar: ${error.message}`,
        );
        return false;
      }
    }

    stopRecognitionOnly() {
      if (!this.recognition) return;
      this.recognition.onend = null;
      try {
        this.recognition.stop();
      } catch (error) {
        this.debug(`recognition.stop ignored: ${error.message}`);
      }
      this.recognition = null;
      this.active = false;
      this.starting = false;
    }

    handleResult(event) {
      const result = event.results[event.results.length - 1];
      if (!result || !result[0]) return;

      const transcript = result[0].transcript.trim();
      this.lastTranscript = transcript;
      this.updateTranscript(transcript);
      this.emitTranscript(transcript, Boolean(result.isFinal));

      if (result.isFinal) {
        this.processTranscript(transcript);
      }
    }

    handleError(event) {
      const error = event?.error || "unknown";
      const message = this.errorMessageFor(error);
      this.lastError = message;

      if (error === "no-speech") {
        this.updateState(STATES.listening_for_wake, message);
        if (this.enabled && this.settings.wake_auto_restart) {
          this.scheduleRestart();
        }
        return;
      }

      const state =
        error === "not-allowed" ? STATES.permission_needed : STATES.error;

      // Fatal errors: disable completely, no auto-restart
      this.enabled = false;
      this.active = false;
      this.starting = false;
      this.persistSettings();
      this.stopRecognitionOnly();

      this.updateState(state, message);
      this.emitError(error, message);
    }

    handleEnd() {
      this.active = false;
      this.starting = false;
      if (!this.enabled || this.stoppedByUser) {
        if (!this.enabled) this.updateState(STATES.off);
        return;
      }

      if (this.settings.wake_auto_restart) {
        this.scheduleRestart();
      }
    }

    // --- Native Desktop Mode ---

    async startNativeDesktop() {
      const bridge = root.misakaDesktop;
      if (
        !bridge ||
        !bridge.isAvailable ||
        typeof bridge.nativeVoiceStart !== "function"
      ) {
        this.updateState(
          STATES.unavailable,
          "Modo nativo de voz nao esta disponivel neste app.",
        );
        return false;
      }

      this._cleanupNativeListeners();
      this.starting = true;
      this.stoppedByUser = false;

      const cleanupTranscript = bridge.onNativeVoiceTranscript((data) => {
        const text = data.text || "";
        this.lastTranscript = text;
        this.updateTranscript(text);
        this.emitTranscript(text, true);
        this.processTranscript(text);
      });

      const cleanupCommand = bridge.onNativeVoiceCommand((data) => {
        const command = data.command || "";
        if (command) {
          this.sendVoiceCommand(command);
        }
      });

      const cleanupStatus = bridge.onNativeVoiceStatus((data) => {
        const nativeState = data.state || "unknown";
        if (nativeState === "listening_for_wake") {
          this.active = true;
          this.starting = false;
          this.updateState(STATES.listening_for_wake, "Wake: usando modo nativo");
        } else if (nativeState === "wake_detected") {
          this.updateState(STATES.wake_detected);
        } else if (nativeState === "stopped") {
          this.active = false;
          this.starting = false;
          if (this.enabled) this.updateState(STATES.off);
        }
      });

      const cleanupError = bridge.onNativeVoiceError((data) => {
        this.lastError = data.message || data.error || "Erro nativo";
        this.active = false;
        this.starting = false;
        this.updateState(STATES.error, this.lastError);
        this.emitError("native", this.lastError);
      });

      this._nativeCleanups = [
        cleanupTranscript,
        cleanupCommand,
        cleanupStatus,
        cleanupError,
      ];

      try {
        const result = await bridge.nativeVoiceStart();
        if (result && result.success) {
          this.enabled = true;
          this.active = true;
          this.starting = false;
          this.persistSettings();
          this.updateState(
            STATES.listening_for_wake,
            "Wake: usando modo nativo",
          );
          return true;
        }
        this.enabled = false;
        this.active = false;
        this.starting = false;
        this.persistSettings();
        const msg = (result && result.error) || "Falha ao iniciar voz nativa";
        this.lastError = msg;
        this.updateState(STATES.error, msg);
        this.emitError("native_start", msg);
        return false;
      } catch (err) {
        this.enabled = false;
        this.active = false;
        this.starting = false;
        this.persistSettings();
        const msg = `Erro ao iniciar voz nativa: ${err.message}`;
        this.lastError = msg;
        this.updateState(STATES.error, msg);
        this.emitError("native_start", msg);
        return false;
      }
    }

    stopNativeDesktop() {
      const bridge = root.misakaDesktop;
      if (bridge && typeof bridge.nativeVoiceStop === "function") {
        bridge.nativeVoiceStop().catch(() => {});
      }
      this._cleanupNativeListeners();
      this.active = false;
      this.starting = false;
    }

    _cleanupNativeListeners() {
      for (const cleanup of this._nativeCleanups) {
        if (typeof cleanup === "function") {
          try { cleanup(); } catch { /* ignore */ }
        }
      }
      this._nativeCleanups = [];
    }

    // --- Shared logic ---

    processTranscript(text) {
      const cleanText = String(text || "").trim();
      if (!cleanText) return null;

      // If waiting for command after wake word
      if (this.waitingForCommand) {
        const commandFromWake = this.extractCommandFromWakePhrase(cleanText);
        const command = commandFromWake === null ? cleanText : commandFromWake;
        this.sendVoiceCommand(command);
        return command;
      }

      // Try wake phrase first
      const wakeCommand = this.extractCommandFromWakePhrase(cleanText);
      if (wakeCommand !== null) {
        this.clearCommandTimer();
        this.waitingForCommand = true;
        this.updateState(STATES.wake_detected);
        this.emitWakeDetected(cleanText);

        if (wakeCommand) {
          this.sendVoiceCommand(wakeCommand);
          return wakeCommand;
        }

        this.updateState(STATES.listening_for_command, "Misaka ouvindo comando...");
        this.commandCaptureTimer = root.setTimeout(() => {
          this.waitingForCommand = false;
          this.updateState(STATES.listening_for_wake, "Nenhum comando capturado.");
        }, this.settings.wake_command_timeout_ms);
        return "";
      }

      // Direct command mode
      if (this.voiceCommandMode === "direct_command" || this.voiceCommandMode === "hybrid") {
        const classification = classifyVoiceCommand(cleanText);
        if (classification.matched) {
          this.debug(`direct command: ${classification.command} risk=${classification.risk}`);
          this.sendVoiceCommand(classification.command);
          return classification.command;
        }
      }

      return null;
    }

    extractCommandFromWakePhrase(text) {
      return extractCommandFromWakePhrase(text, this.settings.wake_phrases);
    }

    sendVoiceCommand(command) {
      const cleanCommand = String(command || "").trim();
      if (!cleanCommand) return Promise.resolve(null);

      // Debounce: ignore duplicate command within cooldown
      const now = Date.now();
      const debounceMs = this.settings.voice_command_debounce_ms || 2500;
      if (
        cleanCommand === this.lastExecutedCommand &&
        now - this.lastExecutedAt < debounceMs
      ) {
        this.debug(`debounced duplicate command: ${cleanCommand}`);
        return Promise.resolve(null);
      }
      this.lastExecutedCommand = cleanCommand;
      this.lastExecutedAt = now;

      this.clearCommandTimer();
      this.waitingForCommand = false;
      this.lastCommand = cleanCommand;
      this.updateCommand(cleanCommand);
      this.updateState(STATES.processing);
      this.emitCommand(cleanCommand);

      const sender = this.sendCommandCallback || this.onCommand;
      return Promise.resolve(sender ? sender(cleanCommand) : null)
        .then((result) => {
          this.updateState(STATES.speaking);
          root.setTimeout(() => {
            if (this.enabled) this.updateState(STATES.listening_for_wake);
          }, 800);
          return result;
        })
        .catch((error) => {
          const message = `Erro ao processar comando de voz: ${error.message}`;
          this.updateState(STATES.error, message);
          this.emitError("command", message);
          throw error;
        });
    }

    // --- State / UI ---

    updateState(state, message = "") {
      this.state = state;
      const label = message || STATE_LABELS[state] || state;
      const listening = [
        STATES.listening_for_wake,
        STATES.wake_detected,
        STATES.listening_for_command,
        STATES.processing,
        STATES.speaking,
      ].includes(state);

      if (this.elements.status) this.elements.status.textContent = label;
      if (this.elements.error) this.elements.error.textContent = message || "";
      if (this.elements.button) {
        this.elements.button.textContent = this.enabled
          ? "Desativar escuta"
          : "Ativar escuta Misaka";
        this.elements.button.dataset.state = state;
        this.elements.button.dataset.mode = this.voiceMode;
        this.elements.button.title = label;
        this.elements.button.classList.toggle("active", listening);
      }
      if (this.elements.toggle) this.elements.toggle.checked = this.enabled;
      if (this.elements.indicator) {
        this.elements.indicator.style.display = listening ? "flex" : "none";
        const indicatorLabel = this.elements.indicator.querySelector("span");
        if (indicatorLabel) indicatorLabel.textContent = label;
      }

      if (this.onStateChange) this.onStateChange(state, label);
      this.debug(`state=${state} mode=${this.voiceMode} message=${label}`);
    }

    dispose() {
      this.stop();
      this.elements = {};
      this.onStateChange = null;
      this.onTranscript = null;
      this.onCommand = null;
      this.onError = null;
      this.onWakeDetected = null;
      this.onDebug = null;
      this.sendCommandCallback = null;
    }

    // --- Settings ---

    loadSettings() {
      this.enabled =
        this.storage.getItem("wake_word_enabled") === "true" ||
        this.storage.getItem("misaka_wake_word") === "true";

      const phrases = this.storage.getItem("wake_phrases");
      if (phrases) {
        this.settings.wake_phrases = phrases
          .split(",")
          .map((phrase) => phrase.trim())
          .filter(Boolean);
      }
      this.settings.wake_language =
        this.storage.getItem("wake_language") || "pt-BR";
      this.settings.wake_auto_restart =
        this.storage.getItem("wake_auto_restart") !== "false";
      this.settings.wake_command_timeout_ms = Number(
        this.storage.getItem("wake_command_timeout_ms") || 8000,
      );
      this.settings.wake_start_on_launch =
        this.storage.getItem("wake_start_on_launch") === "true";

      const savedMode = this.storage.getItem("voice_command_mode");
      if (savedMode === "wake_word" || savedMode === "direct_command" || savedMode === "hybrid") {
        this.voiceCommandMode = savedMode;
        this.settings.voice_command_mode = savedMode;
      }

      this.persistSettings();
    }

    persistSettings() {
      this.storage.setItem("wake_word_enabled", String(this.enabled));
      this.storage.setItem("misaka_wake_word", String(this.enabled));
      this.storage.setItem(
        "wake_phrases",
        this.settings.wake_phrases.join(","),
      );
      this.storage.setItem("wake_language", this.settings.wake_language);
      this.storage.setItem(
        "wake_auto_restart",
        String(this.settings.wake_auto_restart),
      );
      this.storage.setItem(
        "wake_command_timeout_ms",
        String(this.settings.wake_command_timeout_ms),
      );
      this.storage.setItem(
        "wake_start_on_launch",
        String(this.settings.wake_start_on_launch),
      );
      this.storage.setItem("voice_command_mode", this.voiceCommandMode);
    }

    setVoiceCommandMode(mode) {
      if (mode === "wake_word" || mode === "direct_command" || mode === "hybrid") {
        this.voiceCommandMode = mode;
        this.settings.voice_command_mode = mode;
        this.persistSettings();
        this.debug(`voiceCommandMode set to ${mode}`);
      }
    }

    // --- Daemon WebSocket ---

    async connectDaemon(url) {
      const daemonUrl = url || this._daemonUrl;
      if (this._daemonWs && this._daemonConnected) {
        this.debug("daemon already connected");
        return true;
      }

      return new Promise((resolve) => {
        try {
          const ws = new root.WebSocket(daemonUrl);
          this._daemonWs = ws;
          this._daemonConnected = false;

          const timeout = root.setTimeout(() => {
            if (!this._daemonConnected) {
              ws.close();
              this._daemonWs = null;
              resolve(false);
            }
          }, 3000);

          ws.onopen = () => {
            this._daemonConnected = true;
            root.clearTimeout(timeout);
            this.debug("daemon connected");
            resolve(true);
          };

          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              this._handleDaemonMessage(data);
            } catch { /* ignore */ }
          };

          ws.onerror = () => {
            root.clearTimeout(timeout);
            this._daemonWs = null;
            this._daemonConnected = false;
            resolve(false);
          };

          ws.onclose = () => {
            this._daemonConnected = false;
            this._daemonWs = null;
            this.debug("daemon disconnected");
          };
        } catch {
          resolve(false);
        }
      });
    }

    disconnectDaemon() {
      if (this._daemonWs) {
        try { this._daemonWs.close(); } catch { /* ignore */ }
        this._daemonWs = null;
        this._daemonConnected = false;
      }
    }

    _handleDaemonMessage(data) {
      if (data.type === "transcript") {
        const text = data.text || "";
        this.lastTranscript = text;
        this.updateTranscript(text);
        this.emitTranscript(text, true);
        this.processTranscript(text);
      } else if (data.type === "command") {
        const command = data.command || "";
        if (command) {
          this.sendVoiceCommand(command);
        }
      } else if (data.type === "status") {
        this.debug(`daemon status: ${data.state}`);
      } else if (data.type === "error") {
        this.lastError = data.message || data.error || "Erro no daemon";
        this.updateState(STATES.error, this.lastError);
        this.emitError("daemon", this.lastError);
      }
    }

    // --- Helpers ---

    errorMessageFor(error) {
      const messages = {
        "not-allowed": "Permissao de microfone negada.",
        "service-not-allowed":
          "Servico de reconhecimento de voz bloqueado neste ambiente.",
        "audio-capture": "Microfone nao encontrado ou bloqueado.",
        "no-speech": "Nenhuma fala detectada.",
        network: "Reconhecimento de voz indisponivel por erro de rede ou servico.",
        aborted: "Reconhecimento de voz interrompido.",
        "language-not-supported": "Idioma pt-BR nao suportado neste ambiente.",
      };
      return messages[error] || `Erro no reconhecimento de voz: ${error}`;
    }

    _getUnavailableMessage() {
      if (root.misakaDesktop && root.misakaDesktop.isAvailable) {
        if (typeof root.misakaDesktop.nativeVoiceIsAvailable === "function") {
          return "Nenhum modo de reconhecimento de voz esta disponivel.";
        }
        return "Web Speech nao disponivel neste Electron. Modo nativo nao configurado.";
      }
      return "Nenhum modo de reconhecimento de voz esta disponivel.";
    }

    updateTranscript(text) {
      if (this.elements.lastTranscript) {
        this.elements.lastTranscript.textContent = text
          ? `Ultimo ouvido: ${text}`
          : "Ultimo ouvido: -";
      }
    }

    updateCommand(command) {
      if (this.elements.lastCommand) {
        this.elements.lastCommand.textContent = command
          ? `Comando: ${command}`
          : "Comando: -";
      }
    }

    scheduleRestart() {
      if (!this.enabled || this.restartTimer || this.stoppedByUser) return;
      this.restartTimer = root.setTimeout(() => {
        this.restartTimer = null;
        if (this.enabled && !this.active && !this.starting) {
          this.restart();
        }
      }, 500);
    }

    clearRestartTimer() {
      if (this.restartTimer) {
        root.clearTimeout(this.restartTimer);
        this.restartTimer = null;
      }
    }

    clearCommandTimer() {
      if (this.commandCaptureTimer) {
        root.clearTimeout(this.commandCaptureTimer);
        this.commandCaptureTimer = null;
      }
    }

    emitTranscript(transcript, isFinal) {
      if (this.onTranscript) this.onTranscript(transcript, isFinal);
    }

    emitCommand(command) {
      if (this.onCommand) this.onCommand(command);
    }

    emitError(error, message) {
      if (this.onError) this.onError(error, message);
    }

    emitWakeDetected(transcript) {
      if (this.onWakeDetected) this.onWakeDetected(transcript);
    }

    debug(message) {
      if (this.onDebug) this.onDebug(message);
    }
  }

  root.VoiceWakeController = VoiceWakeController;
  root.VoiceWakeUtils = {
    normalizeVoiceText,
    extractCommandFromWakePhrase,
    isDirectVoiceCommand,
    extractDirectVoiceCommand,
    classifyVoiceCommand,
    chooseVoiceWakeMode,
    isWebSpeechSupported,
    isNativeDesktopSupported,
    DEFAULT_WAKE_PHRASES,
    STATES,
  };

  if (typeof module !== "undefined") {
    module.exports = {
      VoiceWakeController,
      normalizeVoiceText,
      extractCommandFromWakePhrase,
      isDirectVoiceCommand,
      extractDirectVoiceCommand,
      classifyVoiceCommand,
      chooseVoiceWakeMode,
      isWebSpeechSupported,
      isNativeDesktopSupported,
      DEFAULT_WAKE_PHRASES,
      STATES,
    };
  }
})(typeof window !== "undefined" ? window : globalThis);
