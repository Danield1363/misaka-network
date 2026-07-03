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
const net = require("net");
const { app } = require("electron");

function getLogFile() {
  if (process.env.MISAKA_DESKTOP_LOG_FILE)
    return process.env.MISAKA_DESKTOP_LOG_FILE;
  try {
    return path.join(app.getPath("userData"), "misaka-desktop.log");
  } catch (_) {
    return path.join(__dirname, "..", "misaka-desktop.log");
  }
}

function serializeLogArg(arg) {
  if (arg instanceof Error) return arg.stack || arg.message;
  if (typeof arg === "object") {
    try {
      return JSON.stringify(arg);
    } catch (_) {
      return String(arg);
    }
  }
  return String(arg == null ? "" : arg);
}

// File-based logger — never touches stdout/stderr
function safeLog(...args) {
  try {
    const line = `[${new Date().toISOString()}] [INFO] [NativeVoice] ${args.map(serializeLogArg).join(" ")}\n`;
    fs.appendFileSync(getLogFile(), line, "utf8");
  } catch (_) {}
}
function safeError(...args) {
  try {
    const line = `[${new Date().toISOString()}] [ERROR] [NativeVoice] ${args.map(serializeLogArg).join(" ")}\n`;
    fs.appendFileSync(getLogFile(), line, "utf8");
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

  _probeDaemon(port) {
    const targetPort = port || this.daemonPort || DEFAULT_DAEMON_PORT;
    return new Promise((resolve) => {
      const socket = new net.Socket();
      const timeout = setTimeout(() => {
        socket.destroy();
        resolve({ running: false });
      }, 1000);
      socket.connect(targetPort, "127.0.0.1", () => {
        clearTimeout(timeout);
        socket.destroy();
        resolve({ running: true, port: targetPort });
      });
      socket.on("error", () => {
        clearTimeout(timeout);
        resolve({ running: false });
      });
    });
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

  async diagnostics() {
    const result = {
      success: true,
      python: { found: false, command: "", version: "" },
      requirements: { file_exists: false, installed: false, missing: [] },
      model: { exists: false, path: DEFAULT_MODEL_PATH },
      daemon: {
        running: this.process !== null,
        websocket: `ws://127.0.0.1:${this.daemonPort || DEFAULT_DAEMON_PORT}`,
      },
      next_step: "",
    };

    // Check Python
    try {
      const pythonCmd = process.platform === "win32" ? "python" : "python3";
      const { execSync } = require("child_process");
      const version = execSync(`${pythonCmd} --version`, {
        encoding: "utf8",
      }).trim();
      result.python = { found: true, command: pythonCmd, version };
    } catch {
      result.python = { found: false, command: "python", version: "" };
    }

    // Check requirements file
    result.requirements.file_exists = fs.existsSync(
      path.join(PYTHON_DIR, "requirements.txt"),
    );

    // Check installed packages
    if (result.python.found) {
      try {
        const { execSync } = require("child_process");
        const pythonCmd = result.python.command;
        for (const pkg of ["vosk", "sounddevice", "websockets"]) {
          execSync(`${pythonCmd} -c "import ${pkg}"`, { stdio: "ignore" });
        }
        result.requirements.installed = true;
      } catch {
        result.requirements.installed = false;
        result.requirements.missing = ["vosk", "sounddevice", "websockets"];
      }
    }

    // Check model
    result.model.exists =
      fs.existsSync(DEFAULT_MODEL_PATH) &&
      fs.readdirSync(DEFAULT_MODEL_PATH).length > 0;

    // Check daemon (child process or external)
    if (!result.daemon.running) {
      const probe = await this._probeDaemon();
      if (probe.running) {
        result.daemon.running = true;
        result.daemon.mode = "manual_or_external";
        result.daemon.websocket = `ws://127.0.0.1:${probe.port}`;
      }
    }

    // Determine next step
    if (!result.python.found) {
      result.next_step = "Instale Python e marque a opcao Add Python to PATH.";
    } else if (!result.requirements.installed) {
      const pkgs = result.requirements.missing.join(", ");
      result.next_step = `Rode: pip install -r desktop/voice/python/requirements.txt (faltando: ${pkgs})`;
    } else if (!result.model.exists) {
      result.next_step =
        "Baixe um modelo Vosk pt-BR e coloque em desktop/voice/models/pt.";
    } else if (!result.daemon.running) {
      result.next_step =
        "Daemon nao esta rodando. Execute: python desktop/voice/python/misaka_voice_daemon.py";
    } else {
      result.next_step = "Tudo pronto! O daemon esta rodando.";
    }

    return result;
  }

  openFolder(folderPath) {
    const { shell } = require("electron");
    const target = folderPath || DEFAULT_MODEL_PATH;
    if (fs.existsSync(target)) {
      shell.openPath(target);
      return { success: true };
    }
    // Create the folder if it doesn't exist
    try {
      fs.mkdirSync(target, { recursive: true });
      shell.openPath(target);
      return { success: true, created: true };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  openDocs() {
    const { shell } = require("electron");
    const docsPath = path.join(
      __dirname,
      "..",
      "..",
      "docs",
      "NATIVE_VOICE_DAEMON.md",
    );
    if (fs.existsSync(docsPath)) {
      shell.openPath(docsPath);
      return { success: true };
    }
    return { success: false, error: "Documentacao nao encontrada." };
  }

  // --- Daemon management ---

  async startDaemon(modelPath, port) {
    if (this.process) {
      return {
        success: true,
        message: "Daemon ja esta rodando.",
        port: this.daemonPort || DEFAULT_DAEMON_PORT,
      };
    }

    // Check if port is already in use by an external daemon
    const probe = await this._probeDaemon(port);
    if (probe.running) {
      safeLog(`Port ${probe.port} already in use by external daemon`);
      return {
        success: true,
        running: true,
        mode: "already_running",
        message: "Daemon de voz ja esta rodando.",
        port: probe.port,
      };
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
      this.process = spawn(
        pythonCmd,
        [
          DAEMON_SCRIPT,
          "--model",
          resolvedModel,
          "--port",
          String(resolvedPort),
        ],
        {
          cwd: PYTHON_DIR,
          stdio: ["ignore", "pipe", "pipe"],
          env: { ...process.env, PYTHONIOENCODING: "utf-8" },
        },
      );
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
        } catch {
          /* ignore non-JSON */
        }
      }
    });

    this.process.stderr.on("data", (chunk) => {
      const text = chunk.toString("utf-8").trim();
      if (text) safeError("[Daemon] stderr:", text);
    });

    this.process.stdout.on("error", (err) => {
      if (err && err.code === "EPIPE") return;
      safeError("[Daemon] stdout error:", err);
    });

    this.process.stderr.on("error", (err) => {
      if (err && err.code === "EPIPE") return;
      safeError("[Daemon] stderr error:", err);
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
        this._send("native-voice:error", {
          error: "daemon_exited",
          message: msg,
        });
      }
      this.process = null;
    });

    return {
      success: true,
      message: "Daemon de voz iniciado.",
      port: resolvedPort,
    };
  }

  stopDaemon() {
    this.state = "stopped";
    if (this.process) {
      try {
        this.process.kill();
      } catch {
        /* already dead */
      }
      this.process = null;
    }
    this._send("native-voice:status", {
      state: "stopped",
      message: "Daemon parado.",
    });
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

  async status() {
    const childRunning = this.process !== null;
    if (childRunning) {
      return {
        state: this.state,
        lastError: this.lastError,
        running: true,
        mode: "child",
      };
    }
    const probe = await this._probeDaemon();
    if (probe.running) {
      return {
        state: "running",
        lastError: "",
        running: true,
        mode: "manual_or_external",
        websocket: `ws://127.0.0.1:${probe.port}`,
      };
    }
    return { state: this.state, lastError: this.lastError, running: false };
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
