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
    unavailable: "Wake: indisponível",
    off: "Wake: desligado",
    permission_needed: "Wake: permissão necessária",
    listening_for_wake: 'Wake: ouvindo por "Misaka"',
    wake_detected: "Wake: palavra detectada",
    listening_for_command: "Wake: capturando comando",
    processing: "Wake: processando",
    speaking: "Wake: falando",
    error: "Wake: erro",
  };

  function normalizeText(text) {
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

    const normalized = normalizeText(raw);
    const normalizedPhrases = wakePhrases
      .map(normalizeText)
      .sort((a, b) => b.length - a.length);
    const hasWakePhrase = normalizedPhrases.some(
      (phrase) => normalized === phrase || normalized.startsWith(`${phrase} `),
    );

    if (!hasWakePhrase) return null;

    const wakePattern = /^\s*(?:(?:ei|ok|acorda)\s+)?misaka\b[\s,.;:!?-]*/i;
    const command = raw.replace(wakePattern, "").trim();
    return command;
  }

  class VoiceWakeController {
    constructor(options = {}) {
      this.elements = options.elements || {};
      this.callbacks = options.callbacks || {};
      this.storage = options.storage || root.localStorage;
      this.recognition = null;
      this.enabled = false;
      this.started = false;
      this.state = STATES.off;
      this.lastTranscript = "";
      this.lastCommand = "";
      this.commandTimer = null;
      this.waitingForCommand = false;
      this.settings = {
        wake_phrases: DEFAULT_WAKE_PHRASES,
        wake_language: "pt-BR",
        wake_auto_restart: true,
        wake_command_timeout_ms: 8000,
        wake_start_on_launch: false,
      };
    }

    init() {
      this.loadSettings();
      this.updateWakeStatus(
        this.isSupported() ? STATES.off : STATES.unavailable,
      );

      if (!this.isSupported()) {
        this.setEnabled(false);
        this.updateWakeStatus(STATES.unavailable, this.getUnsupportedMessage());
        return;
      }

      if (this.settings.wake_start_on_launch || this.enabled) {
        this.start();
      }
    }

    isSupported() {
      return Boolean(root.SpeechRecognition || root.webkitSpeechRecognition);
    }

    loadSettings() {
      this.enabled = this.storage.getItem("wake_word_enabled") === "true";
      if (this.storage.getItem("misaka_wake_word") === "true") {
        this.enabled = true;
      }

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

    start() {
      if (!this.isSupported()) {
        this.enabled = false;
        this.persistSettings();
        this.updateWakeStatus(STATES.unavailable, this.getUnsupportedMessage());
        return false;
      }

      if (this.recognition) {
        this.stopRecognitionOnly();
      }

      const Recognition =
        root.SpeechRecognition || root.webkitSpeechRecognition;
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
        this.started = true;
        this.persistSettings();
        this.updateWakeStatus(STATES.listening_for_wake);
        return true;
      } catch (error) {
        this.enabled = false;
        this.started = false;
        this.persistSettings();
        this.updateWakeStatus(
          STATES.error,
          `Wake word falhou ao iniciar: ${error.message}`,
        );
        return false;
      }
    }

    stop() {
      this.enabled = false;
      this.persistSettings();
      this.clearCommandTimer();
      this.stopRecognitionOnly();
      this.updateWakeStatus(STATES.off);
    }

    restart() {
      this.stopRecognitionOnly();
      if (this.enabled) {
        return this.start();
      }
      return false;
    }

    setEnabled(enabled) {
      if (enabled) {
        return this.start();
      }
      this.stop();
      return true;
    }

    handleResult(event) {
      const result = event.results[event.results.length - 1];
      if (!result || !result[0]) return;

      const transcript = result[0].transcript.trim();
      this.processTranscript(transcript, result.isFinal);
    }

    handleError(event) {
      const error = event.error || "unknown";

      if (error === "no-speech") {
        if (this.enabled && this.settings.wake_auto_restart) {
          this.updateWakeStatus(STATES.listening_for_wake);
        }
        return;
      }

      const messages = {
        "not-allowed": "Permissão de microfone negada.",
        "service-not-allowed": "Permissão de microfone negada.",
        "audio-capture": "Microfone não encontrado ou bloqueado.",
        network: "Reconhecimento de voz indisponível neste ambiente.",
      };
      const state =
        error === "not-allowed" || error === "service-not-allowed"
          ? STATES.permission_needed
          : STATES.error;

      this.enabled = false;
      this.started = false;
      this.persistSettings();
      this.updateWakeStatus(
        state,
        messages[error] || `Wake word falhou: ${error}`,
      );
    }

    handleEnd() {
      this.started = false;
      if (this.enabled && this.settings.wake_auto_restart) {
        try {
          this.recognition.start();
          this.started = true;
          this.updateWakeStatus(
            this.waitingForCommand
              ? STATES.listening_for_command
              : STATES.listening_for_wake,
          );
        } catch (error) {
          this.enabled = false;
          this.persistSettings();
          this.updateWakeStatus(
            STATES.error,
            `Wake word falhou ao reiniciar: ${error.message}`,
          );
        }
        return;
      }

      if (!this.enabled) {
        this.updateWakeStatus(STATES.off);
      }
    }

    processTranscript(text, isFinal = true) {
      this.lastTranscript = text;
      this.updateTranscript(text);

      if (this.waitingForCommand && isFinal) {
        const command = this.extractCommandFromWakePhrase(text);
        this.sendVoiceCommand(command === null ? text : command);
        return;
      }

      const command = this.extractCommandFromWakePhrase(text);
      if (command === null) return;

      this.clearCommandTimer();
      this.waitingForCommand = true;
      this.updateWakeStatus(STATES.wake_detected);

      if (command) {
        this.sendVoiceCommand(command);
        return;
      }

      this.updateWakeStatus(
        STATES.listening_for_command,
        "Misaka ouvindo comando...",
      );
      this.commandTimer = root.setTimeout(() => {
        this.waitingForCommand = false;
        this.updateWakeStatus(
          STATES.listening_for_wake,
          "Nenhum comando capturado.",
        );
      }, this.settings.wake_command_timeout_ms);
    }

    extractCommandFromWakePhrase(text) {
      return extractCommandFromWakePhrase(text, this.settings.wake_phrases);
    }

    sendVoiceCommand(command) {
      const cleanCommand = String(command || "").trim();
      if (!cleanCommand) return;

      this.clearCommandTimer();
      this.waitingForCommand = false;
      this.lastCommand = cleanCommand;
      this.updateCommand(cleanCommand);
      this.updateWakeStatus(STATES.processing);

      Promise.resolve(this.callbacks.sendVoiceCommand(cleanCommand))
        .then(() => {
          this.updateWakeStatus(STATES.speaking);
          root.setTimeout(() => {
            if (this.enabled) this.updateWakeStatus(STATES.listening_for_wake);
          }, 800);
        })
        .catch((error) => {
          this.updateWakeStatus(
            STATES.error,
            `Erro ao processar comando de voz: ${error.message}`,
          );
        });
    }

    updateWakeStatus(state, message = "") {
      this.state = state;
      const label = message || STATE_LABELS[state] || state;
      const listening =
        state === STATES.listening_for_wake ||
        state === STATES.wake_detected ||
        state === STATES.listening_for_command ||
        state === STATES.processing ||
        state === STATES.speaking;

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
      if (this.callbacks.onStatusChange) {
        this.callbacks.onStatusChange(state, label);
      }
    }

    updateTranscript(text) {
      if (this.elements.lastTranscript) {
        this.elements.lastTranscript.textContent = text
          ? `Último ouvido: ${text}`
          : "Último ouvido: -";
      }
    }

    updateCommand(command) {
      if (this.elements.lastCommand) {
        this.elements.lastCommand.textContent = command
          ? `Comando: ${command}`
          : "Comando: -";
      }
    }

    clearCommandTimer() {
      if (this.commandTimer) {
        root.clearTimeout(this.commandTimer);
        this.commandTimer = null;
      }
    }

    stopRecognitionOnly() {
      if (!this.recognition) return;
      this.recognition.onend = null;
      try {
        this.recognition.stop();
      } catch (error) {
        // Recognition can throw when already stopped.
      }
      this.recognition = null;
      this.started = false;
    }

    getUnsupportedMessage() {
      if (root.misakaDesktop && root.misakaDesktop.isAvailable) {
        return "Reconhecimento de voz não disponível neste Electron. Use Chrome/Edge por enquanto ou ative o futuro modo nativo de voz. Modo nativo de wake word ainda não configurado.";
      }
      return "Reconhecimento de voz não disponível neste ambiente.";
    }
  }

  root.VoiceWakeController = VoiceWakeController;
  root.VoiceWakeUtils = {
    normalizeText,
    extractCommandFromWakePhrase,
    DEFAULT_WAKE_PHRASES,
    STATES,
  };

  if (typeof module !== "undefined") {
    module.exports = {
      VoiceWakeController,
      normalizeText,
      extractCommandFromWakePhrase,
      DEFAULT_WAKE_PHRASES,
      STATES,
    };
  }
})(typeof window !== "undefined" ? window : globalThis);
