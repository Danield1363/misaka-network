(function (root) {
  const DEFAULT_WAKE_PHRASES = [
    "misaka",
    "ei misaka",
    "ok misaka",
    "acorda misaka",
  ];
  const VOICE_INPUT_MODES = {
    cloud: "cloud_voice",
    webSpeech: "web_speech_fallback",
    nativeDaemon: "native_daemon_fallback",
    unavailable: "unavailable",
  };
  const COMMAND_MODES = {
    hybrid: "hybrid",
    wakeWord: "wake_word",
    direct: "direct_command",
  };
  const STATES = {
    unavailable: "unavailable",
    off: "off",
    checking: "checking",
    requesting_microphone: "requesting_microphone",
    microphone_ready: "microphone_ready",
    recording: "recording",
    transcribing: "transcribing",
    processing_command: "processing_command",
    listening: "listening",
    listening_for_wake: "listening_for_wake",
    wake_detected: "wake_detected",
    listening_for_command: "listening_for_command",
    processing: "processing",
    speaking: "speaking",
    permission_needed: "permission_needed",
    error: "error",
  };

  const STATE_LABELS = {
    unavailable: "Voz indisponivel",
    off: "Escuta desligada",
    checking: "Verificando voz",
    requesting_microphone: "Pedindo permissao do microfone",
    microphone_ready: "Microfone pronto",
    recording: "Gravando comando",
    transcribing: "Transcrevendo voz",
    processing_command: "Processando comando",
    listening: "Ouvindo comandos",
    listening_for_wake: 'Ouvindo por "Misaka"',
    wake_detected: "Misaka detectada",
    listening_for_command: "Aguardando comando",
    processing: "Processando comando",
    speaking: "Respondendo",
    permission_needed: "Permissao de microfone necessaria",
    error: "Erro de voz",
  };

  const SAFE_DIRECT_PATTERNS = [
    /\b(?:abrir|abra|abre|iniciar|inicia|execute|executar|roda|rodar)\b/,
    /\b(?:pesquisar|pesquise|procurar|procure|buscar|busque)\b/,
    /\b(?:limpar|limpe|ativar|ative|desativar|desative|mostrar|mostre|atualizar|atualize|ligue|desligue)\b/,
  ];

  const DANGEROUS_PATTERNS = [
    /\bdeslig(?:ar|ue|a)\s+(?:o\s+)?(?:computador|pc)\b/,
    /\breinici(?:ar|e|a)\s+(?:o\s+)?(?:computador|pc)\b/,
    /\b(?:apagar|deletar|remover)\s+(?:arquivo|pasta|diretorio)\b/,
    /\bformatar\b/,
    /\brodar\s+script\b/,
    /\bexecutar\s+terminal\b/,
    /\benviar\s+mensagem\b/,
    /\bcomprar\b/,
    /\bpagar\b/,
  ];

  function now() {
    return Date.now ? Date.now() : new Date().getTime();
  }

  function sleep(ms) {
    return new Promise((resolve) => root.setTimeout(resolve, ms));
  }

  function cloudLog(...args) {
    if (root.console && typeof root.console.log === "function") {
      root.console.log("[Cloud Voice]", ...args);
    }
  }

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

  function classifyVoiceCommand(text) {
    const normalized = normalizeVoiceText(text);
    if (!normalized) {
      return {
        matched: false,
        risk: "none",
        requires_confirmation: false,
        command: "",
      };
    }

    if (DANGEROUS_PATTERNS.some((pattern) => pattern.test(normalized))) {
      return {
        matched: true,
        risk: "dangerous",
        requires_confirmation: true,
        command: String(text || "").trim(),
      };
    }

    const safe = SAFE_DIRECT_PATTERNS.some((pattern) =>
      pattern.test(normalized),
    );
    return {
      matched: safe,
      risk: safe ? "safe" : "none",
      requires_confirmation: false,
      command: safe ? String(text || "").trim() : "",
    };
  }

  function isDirectVoiceCommand(text) {
    const classification = classifyVoiceCommand(text);
    return classification.matched && classification.risk === "safe";
  }

  function isCloudVoiceSupported() {
    return Boolean(
      root.navigator &&
      root.navigator.mediaDevices &&
      root.navigator.mediaDevices.getUserMedia &&
      root.MediaRecorder,
    );
  }

  function chooseSupportedAudioMimeType() {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/ogg",
      "audio/mp4",
    ];

    if (!root.MediaRecorder) return "";
    if (typeof root.MediaRecorder.isTypeSupported !== "function") return "";

    for (const type of candidates) {
      if (root.MediaRecorder.isTypeSupported(type)) return type;
    }

    return "";
  }

  function guessAudioExtension(mimeType = "") {
    if (mimeType.includes("ogg")) return "ogg";
    if (mimeType.includes("mp4")) return "m4a";
    if (mimeType.includes("wav")) return "wav";
    if (mimeType.includes("mpeg") || mimeType.includes("mp3")) return "mp3";
    return "webm";
  }

  function createVoiceSessionId() {
    return (
      root.crypto?.randomUUID?.() ||
      `voice-${Date.now()}-${Math.random().toString(36).slice(2)}`
    );
  }

  function isWebSpeechSupported() {
    return Boolean(root.SpeechRecognition || root.webkitSpeechRecognition);
  }

  function isNativeDesktopSupported() {
    return Boolean(root.misakaDesktop && root.misakaDesktop.isAvailable);
  }

  function chooseVoiceWakeMode(preferredMode) {
    if (preferredMode && preferredMode !== "auto") return preferredMode;
    if (isCloudVoiceSupported()) return VOICE_INPUT_MODES.cloud;
    if (isNativeDesktopSupported()) return VOICE_INPUT_MODES.nativeDaemon;
    if (isWebSpeechSupported()) return VOICE_INPUT_MODES.webSpeech;
    return VOICE_INPUT_MODES.unavailable;
  }

  function probeNativeVoiceDaemon(timeoutMs = 1500) {
    return new Promise((resolve) => {
      if (!root.WebSocket) {
        resolve({ success: false, error: "WebSocket indisponivel." });
        return;
      }

      let settled = false;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        try {
          if (socket && socket.readyState <= 1) socket.close();
        } catch (_) {}
        resolve(result);
      };

      let socket;
      try {
        socket = new root.WebSocket("ws://127.0.0.1:8765");
        const timer = root.setTimeout(() => {
          finish({ success: false, error: "Daemon nativo nao respondeu." });
        }, timeoutMs);
        socket.onopen = () => {
          root.clearTimeout(timer);
          finish({
            success: true,
            mode: VOICE_INPUT_MODES.nativeDaemon,
            url: "ws://127.0.0.1:8765",
          });
        };
        socket.onerror = () => {
          root.clearTimeout(timer);
          finish({ success: false, error: "Daemon nativo indisponivel." });
        };
      } catch (error) {
        finish({ success: false, error: error.message });
      }
    });
  }

  class CloudVoiceRecorder {
    constructor(options = {}) {
      this.elements = options.elements || {};
      this.storage = options.storage ||
        root.localStorage || {
          getItem: () => null,
          setItem: () => {},
        };
      this.apiBase =
        options.apiBase ||
        root.MISAKA_CONFIG?.API_BASE_URL ||
        root.__MISAKA_API_BASE_URL__ ||
        "http://127.0.0.1:8000/api";
      this.onStateChange =
        options.onStateChange || options.callbacks?.onStateChange;
      this.onTranscript =
        options.onTranscript || options.callbacks?.onTranscript;
      this.onCommand = options.onCommand || options.callbacks?.onCommand;
      this.onError = options.onError || options.callbacks?.onError;
      this.onWakeDetected =
        options.onWakeDetected || options.callbacks?.onWakeDetected;
      this.onDebug = options.onDebug || options.callbacks?.onDebug;
      this.sendCommandCallback =
        options.sendVoiceCommand || options.callbacks?.sendVoiceCommand;

      this.enabled = false;
      this.active = false;
      this.starting = false;
      this.stoppedByUser = true;
      this.state = STATES.off;
      this.inputMode =
        this.storage.getItem("voice_input_mode") || VOICE_INPUT_MODES.cloud;
      this.commandMode =
        this.storage.getItem("voice_command_mode") || COMMAND_MODES.hybrid;
      this.chunkMs = Number(this.storage.getItem("voice_chunk_ms") || 4000);
      this.debounceMs = Number(
        this.storage.getItem("voice_command_debounce_ms") || 2500,
      );
      this.language = this.storage.getItem("voice_language") || "pt";
      this.voiceSessionId = createVoiceSessionId();
      this.sessionId = this.voiceSessionId;
      this.stream = null;
      this.mediaStream = null;
      this.mediaRecorder = null;
      this.abortController = null;
      this.currentRecorder = null;
      this.currentStream = null;
      this.recording = false;
      this.listeningLoopActive = false;
      this.recordingTimer = null;
      this.hardTimeout = null;
      this.loopTimer = null;
      this.restartTimer = null;
      this.commandCaptureTimer = null;
      this.recognition = null;
      this.nativeUnsubscribers = [];
      this.lastTranscript = "";
      this.lastCommand = "";
      this.lastError = "";
      this.lastExecutedVoiceCommand = null;
      this.lastExecutedVoiceCommandAt = 0;
      this.lastExecutedVoiceCommandId = null;
      this.lastTranscriptionText = null;
      this.lastTranscriptionAt = 0;
      this.lastVoiceCommandBlockReason = "";
      this.commandCooldownMs = Number(
        this.storage.getItem("voice_command_cooldown_ms") || 15000,
      );
      this.postCommandPauseMs = Number(
        this.storage.getItem("voice_post_command_pause_ms") || 5000,
      );
      this.transcribing = false;
      this.processingCommand = false;
      this.waitingForCommand = false;
      this.mockOneShotConsumed = false;
      this.onCommandIgnored =
        options.onCommandIgnored || options.callbacks?.onCommandIgnored;
      this.voiceStatus = null;
    }

    async init() {
      this.bindNativeEvents();
      this.setMode(this.inputMode);
      this.setCommandMode(this.commandMode);
      if (!this.isSupported()) {
        this.updateState(STATES.unavailable, this.unsupportedMessage());
        return { success: false, error: this.unsupportedMessage() };
      }
      this.updateState(STATES.off);
      return { success: true, mode: this.inputMode };
    }

    isSupported() {
      if (this.inputMode === VOICE_INPUT_MODES.cloud)
        return isCloudVoiceSupported();
      if (this.inputMode === VOICE_INPUT_MODES.webSpeech)
        return isWebSpeechSupported();
      if (this.inputMode === VOICE_INPUT_MODES.nativeDaemon)
        return isNativeDesktopSupported();
      return false;
    }

    async start() {
      if (this.active || this.starting) {
        return {
          success: true,
          alreadyActive: true,
          mode: this.inputMode,
          message: "Escuta ja esta ativa.",
        };
      }

      this.clearTimers();
      this.resetVoiceSession();
      this.starting = true;
      this.stoppedByUser = false;

      let result;
      if (this.inputMode === VOICE_INPUT_MODES.cloud) {
        result = await this.startCloudVoice();
      } else if (this.inputMode === VOICE_INPUT_MODES.nativeDaemon) {
        result = await this.startNativeVoice();
      } else if (this.inputMode === VOICE_INPUT_MODES.webSpeech) {
        result = this.startWebSpeech();
      } else {
        result = { success: false, error: this.unsupportedMessage() };
      }

      this.starting = false;
      if (!result.success) {
        this.enabled = false;
        this.active = false;
        this.persistSettings();
        this.updateState(
          result.state || STATES.error,
          result.error || "Falha ao iniciar voz.",
        );
        return result;
      }

      this.enabled = true;
      this.active = true;
      this.persistSettings();
      return result;
    }

    async startCloudVoice() {
      if (!isCloudVoiceSupported()) {
        return {
          success: false,
          state: STATES.unavailable,
          error: this.unsupportedMessage(),
        };
      }

      const consent = await this.ensureCaptureConsent();
      if (!consent) {
        return {
          success: false,
          state: STATES.off,
          error: "Escuta nao ativada sem consentimento.",
        };
      }

      this.updateState(STATES.checking);
      const status = await this.fetchVoiceStatus();
      if (!status.success) {
        return {
          success: false,
          state: STATES.error,
          error: status.error || "Backend de voz indisponivel.",
        };
      }
      if (!status.data.ready) {
        return {
          success: false,
          state: STATES.error,
          error:
            status.data.last_error ||
            "Transcricao de voz nao configurada no backend.",
        };
      }

      const microphone = await this.requestMicrophone();
      if (!microphone.success) return microphone;

      this.updateState(STATES.listening, "Cloud Voice ouvindo comandos.");
      this.startListeningLoop();
      return { success: true, mode: VOICE_INPUT_MODES.cloud };
    }

    async requestMicrophone() {
      this.updateState(STATES.requesting_microphone);
      if (!root.navigator?.mediaDevices?.getUserMedia) {
        return {
          success: false,
          state: STATES.unavailable,
          error: "getUserMedia nao disponivel neste ambiente.",
        };
      }
      try {
        this.mediaStream = await root.navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        this.stream = this.mediaStream;
        this.currentStream = this.mediaStream;
        this.updateState(STATES.microphone_ready);
        return { success: true };
      } catch (error) {
        const message = this.microphoneErrorMessage(error);
        return {
          success: false,
          state: STATES.permission_needed,
          error: message,
        };
      }
    }

    async startListeningLoop() {
      if (this.listeningLoopActive) {
        this.debug("Listening loop already active");
        return;
      }
      this.listeningLoopActive = true;
      this.enabled = true;
      this.active = true;

      while (this.enabled && this.listeningLoopActive) {
        try {
          if (this.processingCommand) {
            await sleep(500);
            continue;
          }

          const blob = await this.recordChunk();
          if (!this.enabled || !this.listeningLoopActive) break;

          if (!blob || blob.size === 0) {
            this.updateState(
              STATES.listening,
              "Nenhuma fala capturada. Aguardando comando...",
            );
            await sleep(300);
            continue;
          }

          this.updateState(STATES.transcribing, "Transcrevendo comando...");
          cloudLog("sending transcription");
          const transcription = await this.sendAudioForTranscription(blob);
          cloudLog("transcription result", transcription);

          if (!this.enabled || !this.listeningLoopActive) break;

          const text = String(transcription?.text || "").trim();
          if (!text) {
            this.updateState(
              STATES.listening,
              "Nenhum comando identificado. Aguardando comando...",
            );
            await sleep(300);
            continue;
          }

          this.lastTranscriptionText = normalizeVoiceText(text);
          this.lastTranscriptionAt = now();
          this.updateState(STATES.processing_command, `Processando: ${text}`);
          const result = await this.processVoiceText(text, transcription);

          if (this.enabled && this.listeningLoopActive) {
            if (result?.executed) {
              this.updateState(
                STATES.listening,
                "Comando executado. Aguardando novo comando...",
              );
              await sleep(this.postCommandPauseMs);
            } else if (result?.reason === "duplicate_cooldown") {
              this.updateState(
                STATES.listening,
                "Comando repetido ignorado por alguns segundos.",
              );
              await sleep(300);
            } else if (result?.reason === "processing") {
              this.updateState(
                STATES.listening,
                "Comando ignorado enquanto outro comando termina.",
              );
              await sleep(300);
            } else {
              this.updateState(STATES.listening, "Ouvindo comandos...");
              await sleep(300);
            }
          }
        } catch (error) {
          this.lastError = error?.message || String(error);
          this.enabled = false;
          this.active = false;
          this.listeningLoopActive = false;
          this.recording = false;
          this.transcribing = false;
          this.persistSettings();
          this.stopListeningLoop();
          this.stopMediaStream();
          this.updateState(STATES.error, this.lastError);
          this.emitError("cloud_voice", this.lastError);
          break;
        }
      }

      this.listeningLoopActive = false;
      this.recording = false;
      this.transcribing = false;
      if (!this.enabled && this.state !== STATES.error) {
        this.updateState(STATES.off, "Escuta desligada.");
      }
    }

    stopListeningLoop() {
      this.listeningLoopActive = false;
      if (this.recordingTimer) {
        root.clearTimeout(this.recordingTimer);
        this.recordingTimer = null;
      }
      if (this.hardTimeout) {
        root.clearTimeout(this.hardTimeout);
        this.hardTimeout = null;
      }
      if (this.mediaRecorder && this.mediaRecorder.state === "recording") {
        try {
          this.mediaRecorder.stop();
        } catch (_) {}
      }
      if (
        this.currentRecorder &&
        this.currentRecorder !== this.mediaRecorder &&
        this.currentRecorder.state === "recording"
      ) {
        try {
          this.currentRecorder.stop();
        } catch (_) {}
      }
      this.currentRecorder = null;
    }

    async recordChunk() {
      const stream = this.currentStream || this.stream || this.mediaStream;
      if (!stream) {
        throw new Error("Microfone nao inicializado.");
      }

      if (this.recording || this.transcribing || this.processingCommand) {
        return null;
      }

      this.recording = true;
      this.updateState(STATES.recording, "Gravando comando...");
      cloudLog("recording chunk started");

      const chunks = [];
      const mimeType = chooseSupportedAudioMimeType();

      return new Promise((resolve, reject) => {
        let recorder;
        let finished = false;
        let forceStopTimer = null;
        let hardTimeout = null;

        const clearLocalTimers = () => {
          if (forceStopTimer) root.clearTimeout(forceStopTimer);
          if (hardTimeout) root.clearTimeout(hardTimeout);
          if (this.recordingTimer === forceStopTimer)
            this.recordingTimer = null;
          if (this.hardTimeout === hardTimeout) this.hardTimeout = null;
          forceStopTimer = null;
          hardTimeout = null;
        };

        const finish = (result) => {
          if (finished) return;
          finished = true;
          this.recording = false;
          clearLocalTimers();
          if (this.mediaRecorder === recorder) this.mediaRecorder = null;
          if (this.currentRecorder === recorder) this.currentRecorder = null;
          resolve(result);
        };

        const fail = (error) => {
          if (finished) return;
          finished = true;
          this.recording = false;
          clearLocalTimers();
          if (this.mediaRecorder === recorder) this.mediaRecorder = null;
          if (this.currentRecorder === recorder) this.currentRecorder = null;
          reject(error);
        };

        try {
          recorder = mimeType
            ? new root.MediaRecorder(stream, { mimeType })
            : new root.MediaRecorder(stream);
          this.mediaRecorder = recorder;
          this.currentRecorder = recorder;
        } catch (error) {
          fail(
            new Error(
              "Formato de gravacao de audio nao suportado neste ambiente.",
            ),
          );
          return;
        }

        recorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            chunks.push(event.data);
          }
        };

        recorder.onerror = (event) => {
          fail(new Error(event.error?.message || "Erro no MediaRecorder."));
        };

        recorder.onstop = () => {
          try {
            const blob = new root.Blob(chunks, {
              type: recorder.mimeType || mimeType || "audio/webm",
            });

            cloudLog("chunk stopped", blob.size, blob.type);

            if (!blob || blob.size === 0) {
              finish(null);
              return;
            }

            finish(blob);
          } catch (error) {
            fail(error);
          }
        };

        try {
          recorder.start();
        } catch (error) {
          fail(error);
          return;
        }

        forceStopTimer = root.setTimeout(() => {
          try {
            if (
              recorder.state === "recording" &&
              typeof recorder.requestData === "function"
            ) {
              recorder.requestData();
            }
            if (recorder.state === "recording") {
              recorder.stop();
            }
          } catch (error) {
            fail(error);
          }
        }, this.chunkMs || 4000);
        this.recordingTimer = forceStopTimer;

        hardTimeout = root.setTimeout(
          () => {
            if (!this.enabled || !this.listeningLoopActive) {
              finish(null);
              return;
            }
            try {
              if (recorder.state === "recording") {
                recorder.stop();
              }
            } catch (_) {}
            fail(new Error("Timeout ao gravar audio."));
          },
          (this.chunkMs || 4000) + 3000,
        );
        this.hardTimeout = hardTimeout;
      });
    }

    scheduleNextChunk() {
      try {
        if (this.enabled && !this.listeningLoopActive) {
          this.startListeningLoop();
        }
      } catch (_) {}
    }

    async sendAudioForTranscription(blob) {
      if (this.transcribing) {
        throw new Error("Transcricao em andamento.");
      }
      this.transcribing = true;
      this.abortController = new root.AbortController();
      this.updateState(STATES.transcribing);
      try {
        const form = new root.FormData();
        const extension = guessAudioExtension(blob.type || "");
        form.append("audio", blob, `misaka-command.${extension}`);
        form.append("language", this.language);
        form.append("source", "cloud_voice");
        form.append("session_id", this.voiceSessionId);

        const response = await root.fetch(`${this.apiBase}/voice/transcribe`, {
          method: "POST",
          body: form,
          signal: this.abortController.signal,
        });
        const data = await response.json().catch(() => null);
        if (!response.ok || !data?.success) {
          throw new Error(
            data?.safe_message ||
              data?.error ||
              `Falha na transcricao: HTTP ${response.status}`,
          );
        }

        return data;
      } catch (error) {
        this.lastError = error?.message || "Backend de voz indisponivel.";
        throw error;
      } finally {
        this.transcribing = false;
        this.abortController = null;
      }
    }

    handleTranscription(text) {
      const transcript = String(text || "").trim();
      if (!transcript) return null;
      this.lastTranscript = transcript;
      this.updateTranscript(transcript);
      this.emitTranscript(transcript, true);
      return this.processVoiceText(transcript);
    }

    processTranscript(text) {
      return this.processVoiceText(text);
    }

    async processVoiceText(text, transcription = null) {
      const raw = String(text || "").trim();
      if (!raw) return { executed: false, reason: "empty" };
      this.lastTranscript = raw;
      this.updateTranscript(raw);
      this.emitTranscript(raw, true);

      const wakeCommand = this.extractCommandFromWakePhrase(raw);
      let command = null;

      if (this.commandMode === COMMAND_MODES.wakeWord) {
        if (wakeCommand === null) {
          this.updateState(STATES.listening, "Ouvindo comandos...");
          return { executed: false, reason: "no_wake_word" };
        }
        this.emitWakeDetected(raw);
        if (!wakeCommand) {
          this.updateState(STATES.listening_for_command);
          return { executed: false, reason: "wake_without_command" };
        }
        command = wakeCommand;
      } else if (this.commandMode === COMMAND_MODES.direct) {
        command = this.commandFromDirectText(raw);
      } else {
        if (wakeCommand !== null) {
          this.emitWakeDetected(raw);
          if (!wakeCommand) {
            this.updateState(STATES.listening_for_command);
            return { executed: false, reason: "wake_without_command" };
          }
          command = wakeCommand;
        } else {
          command = this.commandFromDirectText(raw);
        }
      }

      if (!command) {
        this.updateState(STATES.listening, "Ouvindo comandos...");
        return { executed: false, reason: "no_command" };
      }

      return this.sendVoiceCommand(command, transcription);
    }

    commandFromDirectText(text) {
      const classification = classifyVoiceCommand(text);
      if (!classification.matched) return null;
      if (classification.requires_confirmation) {
        this.debug(
          `Dangerous voice command delegated to command router: ${classification.command}`,
        );
      }
      return classification.command;
    }

    extractCommandFromWakePhrase(text) {
      return extractCommandFromWakePhrase(text, DEFAULT_WAKE_PHRASES);
    }

    async sendVoiceCommand(command, transcription = null) {
      const cleanCommand = String(command || "").trim();
      if (!cleanCommand) return { executed: false, reason: "empty" };

      this.lastCommand = cleanCommand;
      this.updateCommand(cleanCommand);

      if (!this.shouldExecuteVoiceCommand(cleanCommand)) {
        const reason = this.lastVoiceCommandBlockReason || "blocked";
        this.onCommandIgnored?.(cleanCommand, reason);
        this.updateState(
          STATES.listening,
          reason === "processing"
            ? "Comando ignorado enquanto outro comando termina."
            : "Comando repetido ignorado por alguns segundos.",
        );
        return { executed: false, reason, command: cleanCommand };
      }

      this.processingCommand = true;
      cloudLog("command detected", cleanCommand);
      this.updateState(STATES.processing_command);

      const sender = this.sendCommandCallback || this.onCommand;
      try {
        const result = await Promise.resolve(
          sender
            ? sender(cleanCommand, {
                source: "voice",
                transcription,
                sessionId: this.voiceSessionId,
              })
            : cleanCommand,
        );
        this.markVoiceCommandExecuted(cleanCommand);
        if (this.enabled && !this.listeningLoopActive) {
          this.updateState(STATES.listening, "Cloud Voice ouvindo comandos.");
        }
        return { executed: true, command: cleanCommand, result };
      } catch (error) {
        const message = `Erro ao processar comando de voz: ${error.message}`;
        this.lastError = message;
        this.updateState(STATES.error, message);
        this.emitError("command", message);
        return { executed: false, reason: "command_error", error: message };
      } finally {
        this.processingCommand = false;
      }
    }

    shouldExecuteVoiceCommand(command) {
      const normalized = this.normalizeCommandForDedup(command);
      const currentTime = now();
      this.lastVoiceCommandBlockReason = "";

      if (!normalized) return false;

      if (this.processingCommand) {
        this.lastVoiceCommandBlockReason = "processing";
        this.debug(
          `Ignoring command while another command is processing: ${normalized}`,
        );
        return false;
      }

      if (
        normalized === this.lastExecutedVoiceCommand &&
        currentTime - this.lastExecutedVoiceCommandAt < this.commandCooldownMs
      ) {
        this.lastVoiceCommandBlockReason = "duplicate_cooldown";
        this.debug(
          `Ignoring duplicated voice command during cooldown: ${normalized}`,
        );
        return false;
      }

      return true;
    }

    markVoiceCommandExecuted(command) {
      this.lastExecutedVoiceCommand = this.normalizeCommandForDedup(command);
      this.lastExecutedVoiceCommandAt = now();
      this.lastExecutedVoiceCommandId = `${this.lastExecutedVoiceCommand}:${this.lastExecutedVoiceCommandAt}`;
    }

    isDuplicateCommand(command) {
      return !this.shouldExecuteVoiceCommand(command);
    }

    normalizeCommandForDedup(command) {
      return normalizeVoiceText(command || "")
        .replace(/\s+/g, " ")
        .trim();
    }

    setMode(mode) {
      this.inputMode = mode || VOICE_INPUT_MODES.cloud;
      this.storage.setItem("voice_input_mode", this.inputMode);
      if (this.elements.mode) this.elements.mode.value = this.inputMode;
      this.updateModeLabel();
    }

    setCommandMode(commandMode) {
      this.commandMode = commandMode || COMMAND_MODES.hybrid;
      this.storage.setItem("voice_command_mode", this.commandMode);
      if (this.elements.commandMode)
        this.elements.commandMode.value = this.commandMode;
    }

    async setEnabled(enabled) {
      if (!enabled) {
        return await this.stop();
      }

      if (this.enabled || this.listeningLoopActive || this.starting) {
        return {
          success: true,
          alreadyActive: true,
          mode: this.inputMode,
          message: "Escuta ja esta ativa.",
        };
      }

      this.updateState(STATES.checking, "Preparando escuta...");
      const result = await this.start();
      if (!result?.success) {
        await this.stop();
        this.updateState(
          result?.state || STATES.error,
          result?.error || "Nao foi possivel iniciar escuta.",
        );
      }
      return result;
    }

    async restart() {
      await this.stop();
      return this.start();
    }

    async stop() {
      this.enabled = false;
      this.active = false;
      this.starting = false;
      this.stoppedByUser = true;
      this.processingCommand = false;
      this.transcribing = false;
      this.recording = false;
      this.listeningLoopActive = false;
      this.waitingForCommand = false;

      if (this.abortController) {
        try {
          this.abortController.abort();
        } catch (_) {}
        this.abortController = null;
      }

      this.stopListeningLoop();
      this.stopWebSpeech();
      this.stopNativeVoice();
      this.stopMediaStream();
      this.clearTimers();
      this.persistSettings();
      this.updateState(STATES.off, "Escuta desligada.");
      return { success: true, stopped: true };
    }

    dispose() {
      this.stop();
      this.nativeUnsubscribers.forEach((unsubscribe) => {
        try {
          unsubscribe();
        } catch (_) {}
      });
      this.nativeUnsubscribers = [];
      this.elements = {};
    }

    async fetchVoiceStatus() {
      try {
        const response = await root.fetch(`${this.apiBase}/voice/status`);
        const data = await response.json();
        this.voiceStatus = data;
        this.updateModeLabel(data);
        return { success: true, data };
      } catch (error) {
        return { success: false, error: "Backend de voz indisponivel." };
      }
    }

    async ensureCaptureConsent() {
      if (this.storage.getItem("voice_capture_consent") === "true") return true;
      const message =
        "Com a escuta ativa, a Misaka capturara audio do microfone para transcrever comandos. O audio sera enviado ao backend configurado apenas para gerar texto de comando. Deseja ativar?";
      const accepted =
        typeof root.confirm === "function" ? root.confirm(message) : true;
      if (accepted) this.storage.setItem("voice_capture_consent", "true");
      return accepted;
    }

    bestRecorderOptions() {
      if (!root.MediaRecorder || !root.MediaRecorder.isTypeSupported)
        return null;
      const candidates = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg",
      ];
      const mimeType = candidates.find((candidate) =>
        root.MediaRecorder.isTypeSupported(candidate),
      );
      return mimeType ? { mimeType } : null;
    }

    audioFileName(blob) {
      const type = blob.type || "audio/webm";
      if (type.includes("ogg")) return "command.ogg";
      if (type.includes("wav")) return "command.wav";
      if (type.includes("mpeg") || type.includes("mp3")) return "command.mp3";
      if (type.includes("mp4") || type.includes("m4a")) return "command.m4a";
      return "command.webm";
    }

    startWebSpeech() {
      if (!isWebSpeechSupported()) {
        return {
          success: false,
          state: STATES.unavailable,
          error:
            "Reconhecimento de voz nao disponivel neste ambiente. Use Cloud Voice.",
        };
      }

      const Recognition =
        root.SpeechRecognition || root.webkitSpeechRecognition;
      this.recognition = new Recognition();
      this.recognition.lang = "pt-BR";
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;
      this.recognition.onresult = (event) => this.handleResult(event);
      this.recognition.onerror = (event) => this.handleError(event);
      this.recognition.onend = () => this.handleEnd();

      try {
        this.recognition.start();
        this.updateState(STATES.listening_for_wake);
        return { success: true, mode: VOICE_INPUT_MODES.webSpeech };
      } catch (error) {
        this.stopWebSpeech();
        return { success: false, state: STATES.error, error: error.message };
      }
    }

    handleResult(event) {
      const result = event.results[event.results.length - 1];
      if (!result || !result[0]) return;
      const transcript = result[0].transcript.trim();
      this.lastTranscript = transcript;
      this.updateTranscript(transcript);
      this.emitTranscript(transcript, Boolean(result.isFinal));
      if (result.isFinal) this.processVoiceText(transcript);
    }

    handleError(event) {
      const error = event?.error || "unknown";
      const message = this.webSpeechErrorMessage(error);
      const state =
        error === "not-allowed" ? STATES.permission_needed : STATES.error;
      this.lastError = message;
      this.enabled = false;
      this.active = false;
      this.updateState(state, message);
      this.emitError(error, message);
    }

    handleEnd() {
      this.active = false;
      if (
        !this.enabled ||
        this.stoppedByUser ||
        this.inputMode !== VOICE_INPUT_MODES.webSpeech
      ) {
        return;
      }
      this.restartTimer = root.setTimeout(() => {
        this.restartTimer = null;
        if (this.enabled) this.startWebSpeech();
      }, 500);
    }

    stopWebSpeech() {
      if (!this.recognition) return;
      this.recognition.onend = null;
      try {
        this.recognition.stop();
      } catch (_) {}
      this.recognition = null;
    }

    async startNativeVoice() {
      if (!root.misakaDesktop?.nativeVoiceStart) {
        return {
          success: false,
          state: STATES.unavailable,
          error: "Modo nativo de voz indisponivel neste desktop.",
        };
      }
      const result = await root.misakaDesktop.nativeVoiceStart();
      if (!result || result.success === false) {
        return {
          success: false,
          state: STATES.error,
          error: result?.error || "Daemon nativo de voz nao iniciou.",
        };
      }
      this.updateState(STATES.listening, "Native Daemon ouvindo comandos.");
      return { success: true, mode: VOICE_INPUT_MODES.nativeDaemon };
    }

    stopNativeVoice() {
      if (
        this.inputMode === VOICE_INPUT_MODES.nativeDaemon &&
        root.misakaDesktop?.nativeVoiceStop
      ) {
        root.misakaDesktop.nativeVoiceStop().catch(() => {});
      }
    }

    bindNativeEvents() {
      if (!root.misakaDesktop || this.nativeUnsubscribers.length > 0) return;
      if (root.misakaDesktop.onNativeVoiceTranscript) {
        this.nativeUnsubscribers.push(
          root.misakaDesktop.onNativeVoiceTranscript((event) => {
            const text = event?.text || event?.transcript || "";
            if (text) this.handleTranscription(text);
          }),
        );
      }
      if (root.misakaDesktop.onNativeVoiceCommand) {
        this.nativeUnsubscribers.push(
          root.misakaDesktop.onNativeVoiceCommand((event) => {
            const command = event?.command || event?.text || "";
            if (command) this.processVoiceText(command);
          }),
        );
      }
      if (root.misakaDesktop.onNativeVoiceError) {
        this.nativeUnsubscribers.push(
          root.misakaDesktop.onNativeVoiceError((event) => {
            const message =
              event?.message || event?.error || "Erro no daemon nativo.";
            this.updateState(STATES.error, message);
            this.emitError("native_voice", message);
          }),
        );
      }
    }

    stopMediaStream() {
      const stream = this.currentStream || this.stream || this.mediaStream;
      if (!stream) return;
      stream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (_) {}
      });
      this.currentStream = null;
      this.mediaStream = null;
      this.stream = null;
    }

    clearTimers() {
      if (this.recordingTimer) root.clearTimeout(this.recordingTimer);
      if (this.hardTimeout) root.clearTimeout(this.hardTimeout);
      if (this.loopTimer) root.clearTimeout(this.loopTimer);
      if (this.restartTimer) root.clearTimeout(this.restartTimer);
      if (this.commandCaptureTimer) root.clearTimeout(this.commandCaptureTimer);
      this.recordingTimer = null;
      this.hardTimeout = null;
      this.loopTimer = null;
      this.restartTimer = null;
      this.commandCaptureTimer = null;
    }

    resetVoiceSession() {
      this.voiceSessionId = createVoiceSessionId();
      this.sessionId = this.voiceSessionId;
      this.mockOneShotConsumed = false;
      this.lastTranscriptionText = null;
      this.lastTranscriptionAt = 0;
      this.lastExecutedVoiceCommandId = null;
    }

    persistSettings() {
      this.storage.setItem("wake_word_enabled", String(this.enabled));
      this.storage.setItem("misaka_wake_word", String(this.enabled));
      this.storage.setItem("voice_input_mode", this.inputMode);
      this.storage.setItem("voice_command_mode", this.commandMode);
    }

    updateState(state, message = "") {
      this.state = state;
      const label = message || STATE_LABELS[state] || state;
      const activeStates = new Set([
        STATES.requesting_microphone,
        STATES.microphone_ready,
        STATES.recording,
        STATES.transcribing,
        STATES.processing_command,
        STATES.listening,
        STATES.listening_for_wake,
        STATES.wake_detected,
        STATES.listening_for_command,
        STATES.processing,
        STATES.speaking,
      ]);
      const active = activeStates.has(state);

      if (this.elements.status) this.elements.status.textContent = label;
      if (this.elements.error) {
        this.elements.error.textContent =
          state === STATES.error ||
          state === STATES.permission_needed ||
          state === STATES.unavailable
            ? label
            : "";
      }
      if (this.elements.button) {
        this.elements.button.textContent = this.enabled
          ? "Desativar escuta"
          : "Ativar escuta";
        this.elements.button.dataset.state = state;
        this.elements.button.classList.toggle("active", active);
        this.elements.button.disabled = this.starting;
        this.elements.button.title = label;
      }
      if (this.elements.toggle) this.elements.toggle.checked = this.enabled;
      if (this.elements.indicator) {
        this.elements.indicator.style.display = active ? "flex" : "none";
        const indicatorLabel = this.elements.indicator.querySelector("span");
        if (indicatorLabel) indicatorLabel.textContent = label;
      }
      if (this.onStateChange) this.onStateChange(state, label);
      this.debug(`state=${state} message=${label}`);
    }

    updateModeLabel(status = this.voiceStatus) {
      const label = this.modeLabel(status);
      if (this.elements.modeLabel) this.elements.modeLabel.textContent = label;
    }

    modeLabel(status = this.voiceStatus) {
      if (this.inputMode === VOICE_INPUT_MODES.cloud) {
        const provider = status?.provider ? ` (${status.provider})` : "";
        return `Modo: Cloud Voice${provider}`;
      }
      if (this.inputMode === VOICE_INPUT_MODES.webSpeech) {
        return "Modo: Web Speech Fallback";
      }
      if (this.inputMode === VOICE_INPUT_MODES.nativeDaemon) {
        return "Modo: Native Daemon";
      }
      return "Modo: Indisponivel";
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

    microphoneErrorMessage(error) {
      if (
        error?.name === "NotAllowedError" ||
        error?.name === "SecurityError"
      ) {
        return "Permissao de microfone negada.";
      }
      if (
        error?.name === "NotFoundError" ||
        error?.name === "DevicesNotFoundError"
      ) {
        return "Microfone nao encontrado.";
      }
      return error?.message || "Nao consegui acessar o microfone.";
    }

    webSpeechErrorMessage(error) {
      const messages = {
        "not-allowed": "Permissao de microfone negada.",
        "service-not-allowed": "Servico de reconhecimento de voz bloqueado.",
        "audio-capture": "Microfone nao encontrado ou bloqueado.",
        "no-speech": "Nenhuma fala detectada.",
        network: "Reconhecimento de voz indisponivel por erro de rede.",
        aborted: "Reconhecimento de voz interrompido.",
        "language-not-supported": "Idioma pt-BR nao suportado.",
      };
      return messages[error] || `Erro no reconhecimento de voz: ${error}`;
    }

    unsupportedMessage() {
      if (this.inputMode === VOICE_INPUT_MODES.cloud) {
        return "MediaRecorder nao disponivel neste ambiente.";
      }
      if (this.inputMode === VOICE_INPUT_MODES.webSpeech) {
        return "Reconhecimento de voz nao disponivel neste ambiente. Use Chrome/Edge ou Cloud Voice.";
      }
      if (this.inputMode === VOICE_INPUT_MODES.nativeDaemon) {
        return "Modo nativo de wake word ainda nao configurado.";
      }
      return "Voz indisponivel neste ambiente.";
    }

    emitTranscript(transcript, isFinal) {
      if (this.onTranscript) this.onTranscript(transcript, isFinal);
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

  const VoiceWakeController = CloudVoiceRecorder;

  root.CloudVoiceRecorder = CloudVoiceRecorder;
  root.VoiceWakeController = VoiceWakeController;
  root.VoiceWakeUtils = {
    normalizeVoiceText,
    extractCommandFromWakePhrase,
    isDirectVoiceCommand,
    classifyVoiceCommand,
    isCloudVoiceSupported,
    chooseSupportedAudioMimeType,
    guessAudioExtension,
    isWebSpeechSupported,
    isNativeDesktopSupported,
    chooseVoiceWakeMode,
    probeNativeVoiceDaemon,
    DEFAULT_WAKE_PHRASES,
    VOICE_INPUT_MODES,
    COMMAND_MODES,
    STATES,
  };

  if (typeof module !== "undefined") {
    module.exports = {
      CloudVoiceRecorder,
      VoiceWakeController,
      normalizeVoiceText,
      extractCommandFromWakePhrase,
      isDirectVoiceCommand,
      classifyVoiceCommand,
      isCloudVoiceSupported,
      chooseSupportedAudioMimeType,
      guessAudioExtension,
      isWebSpeechSupported,
      isNativeDesktopSupported,
      chooseVoiceWakeMode,
      probeNativeVoiceDaemon,
      DEFAULT_WAKE_PHRASES,
      VOICE_INPUT_MODES,
      COMMAND_MODES,
      STATES,
    };
  }
})(typeof window !== "undefined" ? window : globalThis);
