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
const DEFAULT_MODEL_PATH = path.join(__dirname, "models", "pt");

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
      return fs.existsSync(SERVICE_SCRIPT);
    } catch {
      return false;
    }
  }

  start(modelPath) {
    if (this.process) {
      return { success: true, message: "Serviço já está rodando." };
    }

    if (!fs.existsSync(SERVICE_SCRIPT)) {
      const msg = "Script de voz nativo não encontrado.";
      this.lastError = msg;
      this._send("native-voice:error", { error: "script_not_found", message: msg });
      return { success: false, error: msg };
    }

    const resolvedModel = modelPath || DEFAULT_MODEL_PATH;
    const pythonCmd = process.platform === "win32" ? "python" : "python3";

    try {
      this.process = spawn(pythonCmd, [SERVICE_SCRIPT, "--model", resolvedModel], {
        cwd: PYTHON_DIR,
        stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      });
    } catch (err) {
      const msg = `Falha ao iniciar serviço Python: ${err.message}`;
      this.lastError = msg;
      this._send("native-voice:error", { error: "spawn_failed", message: msg });
      return { success: false, error: msg };
    }

    this.state = "starting";

    this.process.stdout.on("data", (chunk) => {
      const lines = chunk.toString("utf-8").split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          this._handleEvent(event);
        } catch {
          // Non-JSON output from Python (e.g. warning) — ignore
        }
      }
    });

    this.process.stderr.on("data", (chunk) => {
      const text = chunk.toString("utf-8").trim();
      if (text) {
        safeError("[NativeVoice] stderr:", text);
      }
    });

    this.process.on("error", (err) => {
      const msg = `Processo Python falhou: ${err.message}`;
      this.state = "error";
      this.lastError = msg;
      this._send("native-voice:error", { error: "process_error", message: msg });
      this.process = null;
    });

    this.process.on("close", (code) => {
      if (this.state !== "stopped") {
        const msg = `Serviço encerrou com código ${code}`;
        this.state = "error";
        this.lastError = msg;
        this._send("native-voice:error", { error: "process_exited", message: msg });
      }
      this.process = null;
    });

    return { success: true, message: "Serviço de voz nativo iniciado." };
  }

  stop() {
    this.state = "stopped";
    if (this.process) {
      try {
        this.process.kill();
      } catch {
        // Process may already be dead
      }
      this.process = null;
    }
    this._send("native-voice:status", { state: "stopped", message: "Serviço de voz parado." });
    return { success: true };
  }

  restart(modelPath) {
    this.stop();
    return this.start(modelPath);
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
