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

      this.settings = {
        wake_phrases: DEFAULT_WAKE_PHRASES.slice(),
        wake_language: "pt-BR",
        wake_auto_restart: true,
        wake_command_timeout_ms: 8000,
        wake_start_on_launch: false,
      };
    }

    init() {
      this.loadSettings();
      if (!this.isSupported()) {
        this.enabled = false;
        this.persistSettings();
        this.updateState(STATES.unavailable, this.getUnsupportedMessage());
        return false;
      }

      this.updateState(STATES.off);
      if (this.settings.wake_start_on_launch || this.enabled) {
        return this.start();
      }
      return true;
    }

    isSupported() {
      return Boolean(root.SpeechRecognition || root.webkitSpeechRecognition);
    }

    start() {
      if (this.active || this.starting) {
        return true;
      }

      if (!this.isSupported()) {
        this.enabled = false;
        this.active = false;
        this.starting = false;
        this.persistSettings();
        this.updateState(STATES.unavailable, this.getUnsupportedMessage());
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
        this.updateState(STATES.listening_for_wake);
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

    stop() {
      this.enabled = false;
      this.active = false;
      this.starting = false;
      this.stoppedByUser = true;
      this.waitingForCommand = false;
      this.clearRestartTimer();
      this.clearCommandTimer();
      this.stopRecognitionOnly();
      this.persistSettings();
      this.updateState(STATES.off);
    }

    restart() {
      this.stopRecognitionOnly();
      this.active = false;
      this.starting = false;
      if (!this.enabled) return false;
      return this.start();
    }

    setEnabled(enabled) {
      if (enabled) return this.start();
      this.stop();
      return true;
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
      this.updateState(state, message);
      this.emitError(error, message);

      if (FATAL_ERRORS.has(error)) {
        this.enabled = false;
        this.active = false;
        this.starting = false;
        this.persistSettings();
        this.stopRecognitionOnly();
        return;
      }

      if (this.enabled && this.settings.wake_auto_restart) {
        this.scheduleRestart();
      }
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

    processTranscript(text) {
      const cleanText = String(text || "").trim();
      if (!cleanText) return null;

      if (this.waitingForCommand) {
        const commandFromWake = this.extractCommandFromWakePhrase(cleanText);
        const command = commandFromWake === null ? cleanText : commandFromWake;
        this.sendVoiceCommand(command);
        return command;
      }

      const command = this.extractCommandFromWakePhrase(cleanText);
      if (command === null) return null;

      this.clearCommandTimer();
      this.waitingForCommand = true;
      this.updateState(STATES.wake_detected);
      this.emitWakeDetected(cleanText);

      if (command) {
        this.sendVoiceCommand(command);
        return command;
      }

      this.updateState(STATES.listening_for_command, "Misaka ouvindo comando...");
      this.commandCaptureTimer = root.setTimeout(() => {
        this.waitingForCommand = false;
        this.updateState(STATES.listening_for_wake, "Nenhum comando capturado.");
      }, this.settings.wake_command_timeout_ms);
      return "";
    }

    extractCommandFromWakePhrase(text) {
      return extractCommandFromWakePhrase(text, this.settings.wake_phrases);
    }

    sendVoiceCommand(command) {
      const cleanCommand = String(command || "").trim();
      if (!cleanCommand) return Promise.resolve(null);

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
      this.debug(`state=${state} message=${label}`);
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
    }

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

    getUnsupportedMessage() {
      if (root.misakaDesktop && root.misakaDesktop.isAvailable) {
        return "Reconhecimento de voz nao disponivel neste Electron. Use Chrome/Edge por enquanto ou ative o futuro modo nativo de voz.\nModo nativo de wake word ainda nao configurado.";
      }
      return "Reconhecimento de voz nao disponivel neste ambiente.";
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
    DEFAULT_WAKE_PHRASES,
    STATES,
  };

  if (typeof module !== "undefined") {
    module.exports = {
      VoiceWakeController,
      normalizeVoiceText,
      extractCommandFromWakePhrase,
      DEFAULT_WAKE_PHRASES,
      STATES,
    };
  }
})(typeof window !== "undefined" ? window : globalThis);
