/**
 * Native Voice Bridge for Misaka Desktop.
 *
 * Spawns the Python Vosk voice service as a child process,
 * reads JSON line-delimited events from stdout, and forwards
 * them to the Electron renderer via IPC.
 *
 * The service is NOT started automatically — the user must click
 * "Ativar escuta Misaka" to begin listening.
 */

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

// File-based logger — never touches stdout/stderr
function safeLog(...args) {
  try {
    const line = `[${new Date().toISOString()}] [INFO] [NativeVoice] ${args.map(String).join(" ")}\n`;
    fs.appendFileSync(path.join(__dirname, "..", "..", "misaka-desktop.log"), line, "utf8");
  } catch (_) {}
}
function safeError(...args) {
  try {
    const line = `[${new Date().toISOString()}] [ERROR] [NativeVoice] ${args.map(String).join(" ")}\n`;
    fs.appendFileSync(path.join(__dirname, "..", "..", "misaka-desktop.log"), line, "utf8");
  } catch (_) {}
}

const PYTHON_DIR = path.join(__dirname, "python");
const SERVICE_SCRIPT = path.join(PYTHON_DIR, "misaka_voice_service.py");
const DAEMON_SCRIPT = path.join(PYTHON_DIR, "misaka_voice_daemon.py");
const DEFAULT_MODEL_PATH = path.join(__dirname, "models", "pt");
const DEFAULT_DAEMON_PORT = 8765;

class NativeVoiceBridge {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.process = null;
    this.state = "stopped";
    this.lastError = "";
  }

  isAvailable() {
    try {
      const pythonCmd = process.platform === "win32" ? "python" : "python3";
      const { execSync } = require("child_process");
      execSync(`${pythonCmd} --version`, { stdio: "ignore" });
      return fs.existsSync(DAEMON_SCRIPT) || fs.existsSync(SERVICE_SCRIPT);
    } catch {
      return false;
    }
  }

  // --- Daemon management ---

  startDaemon(modelPath, port) {
    if (this.process) {
      return { success: true, message: "Daemon ja esta rodando.", port: this.daemonPort || DEFAULT_DAEMON_PORT };
    }

    if (!fs.existsSync(DAEMON_SCRIPT)) {
      const msg = "Script de daemon nao encontrado.";
      this.lastError = msg;
      return { success: false, error: msg };
    }

    const resolvedModel = modelPath || DEFAULT_MODEL_PATH;
    const resolvedPort = port || DEFAULT_DAEMON_PORT;
    const pythonCmd = process.platform === "win32" ? "python" : "python3";

    try {
      this.process = spawn(pythonCmd, [
        DAEMON_SCRIPT,
        "--model", resolvedModel,
        "--port", String(resolvedPort),
      ], {
        cwd: PYTHON_DIR,
        stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      });
    } catch (err) {
      const msg = `Falha ao iniciar daemon: ${err.message}`;
      this.lastError = msg;
      return { success: false, error: msg };
    }

    this.state = "starting";
    this.daemonPort = resolvedPort;

    this.process.stdout.on("data", (chunk) => {
      const lines = chunk.toString("utf-8").split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          this._handleEvent(event);
        } catch { /* ignore non-JSON */ }
      }
    });

    this.process.stderr.on("data", (chunk) => {
      const text = chunk.toString("utf-8").trim();
      if (text) safeError("[Daemon] stderr:", text);
    });

    this.process.on("error", (err) => {
      const msg = `Daemon falhou: ${err.message}`;
      this.state = "error";
      this.lastError = msg;
      this._send("native-voice:error", { error: "daemon_error", message: msg });
      this.process = null;
    });

    this.process.on("close", (code) => {
      if (this.state !== "stopped") {
        const msg = `Daemon encerrou com codigo ${code}`;
        this.state = "error";
        this.lastError = msg;
        this._send("native-voice:error", { error: "daemon_exited", message: msg });
      }
      this.process = null;
    });

    return { success: true, message: "Daemon de voz iniciado.", port: resolvedPort };
  }

  stopDaemon() {
    this.state = "stopped";
    if (this.process) {
      try { this.process.kill(); } catch { /* already dead */ }
      this.process = null;
    }
    this._send("native-voice:status", { state: "stopped", message: "Daemon parado." });
    return { success: true };
  }

  restartDaemon(modelPath, port) {
    this.stopDaemon();
    return this.startDaemon(modelPath, port);
  }

  // Legacy service methods (backward compat)
  start(modelPath) {
    return this.startDaemon(modelPath);
  }

  stop() {
    return this.stopDaemon();
  }

  restart(modelPath) {
    return this.restartDaemon(modelPath);
  }

  status() {
    return {
      state: this.state,
      lastError: this.lastError,
      running: this.process !== null,
    };
  }

  _handleEvent(event) {
    if (event.type === "status") {
      this.state = event.state || "unknown";
      this._send("native-voice:status", event);
    } else if (event.type === "transcript") {
      this._send("native-voice:transcript", event);
    } else if (event.type === "command") {
      this._send("native-voice:command", event);
    } else if (event.type === "error") {
      this.state = "error";
      this.lastError = event.message || event.error || "Erro desconhecido";
      this._send("native-voice:error", event);
    }
  }

  _send(channel, data) {
    try {
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        this.mainWindow.webContents.send(channel, data);
      }
    } catch (_) {}
  }
}

module.exports = { NativeVoiceBridge };
