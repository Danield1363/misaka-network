const {
  app,
  BrowserWindow,
  Tray,
  Menu,
  nativeImage,
  Notification,
  ipcMain,
  session,
  shell,
} = require("electron");
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");

// --- File-based logger (never touches stdout/stderr — prevents EPIPE) ---
let LOG_FILE = "";
try {
  const userData = app.getPath("userData");
  LOG_FILE = path.join(userData, "misaka-desktop.log");
} catch (_) {
  LOG_FILE = path.join(__dirname, "misaka-desktop.log");
}

function writeLog(level, args) {
  try {
    const line = `[${new Date().toISOString()}] [${level}] ${args
      .map((a) => {
        if (a instanceof Error) return a.stack || a.message;
        if (typeof a === "object") {
          try {
            return JSON.stringify(a);
          } catch {
            return String(a);
          }
        }
        return String(a == null ? "" : a);
      })
      .join(" ")}\n`;
    fs.appendFileSync(LOG_FILE, line, "utf8");
  } catch (_) {}
}

function safeLog(...args) {
  writeLog("INFO", args);
}
function safeWarn(...args) {
  writeLog("WARN", args);
}
function safeError(...args) {
  writeLog("ERROR", args);
}

// --- Monkey-patch console so no direct console.* can EPIPE-crash ---
console.log = (...args) => safeLog(...args);
console.warn = (...args) => safeWarn(...args);
console.error = (...args) => safeError(...args);

// --- EPIPE handling (catches everything the monkey-patch misses) ---
process.stdout?.on?.("error", (err) => {
  if (err && err.code === "EPIPE") return;
  writeLog("ERROR", ["[stdout error]", err]);
});
process.stderr?.on?.("error", (err) => {
  if (err && err.code === "EPIPE") return;
  writeLog("ERROR", ["[stderr error]", err]);
});
process.on("uncaughtException", (error) => {
  if (error && error.code === "EPIPE") return;
  writeLog("ERROR", ["[Misaka Desktop] uncaughtException:", error]);
});
process.on("unhandledRejection", (reason) => {
  writeLog("ERROR", ["[Misaka Desktop] unhandledRejection:", reason]);
});

let mainWindow;
let tray;
let isQuitting = false;
let notifiedAlertIds = new Set();
let nativeVoiceBridge = null;
let pendingWakeWordEnabled = null;

process.env.MISAKA_DESKTOP_LOG_FILE = LOG_FILE;

const isPackaged = app.isPackaged;

function getDashboardDir() {
  if (isPackaged) {
    const resourcePath = path.join(process.resourcesPath, "dashboard");
    if (fs.existsSync(resourcePath)) return resourcePath;
    return path.join(process.resourcesPath, "app", "dashboard");
  }
  return path.join(__dirname, "..", "dashboard");
}

const DASHBOARD_DIR = getDashboardDir();

const CONFIG = {
  API_BASE_URL: process.env.MISAKA_API_BASE_URL || "http://127.0.0.1:8000/api",
  DASHBOARD_URL: process.env.MISAKA_DASHBOARD_URL || "",
  START_MINIMIZED: process.env.START_MINIMIZED === "true",
  ALWAYS_ON_TOP_DEFAULT: process.env.ALWAYS_ON_TOP_DEFAULT === "true",
  TRANSPARENT_MODE_DEFAULT: process.env.TRANSPARENT_MODE_DEFAULT === "true",
};

const NOTIFIED_IDS_FILE = path.join(
  app.getPath("userData"),
  "notified_alerts.json",
);

function loadNotifiedIds() {
  try {
    if (fs.existsSync(NOTIFIED_IDS_FILE)) {
      const data = JSON.parse(fs.readFileSync(NOTIFIED_IDS_FILE, "utf-8"));
      notifiedAlertIds = new Set(data.ids || []);
    }
  } catch (error) {
    safeError("Failed to load notified IDs:", error);
  }
}

function saveNotifiedIds() {
  try {
    fs.writeFileSync(
      NOTIFIED_IDS_FILE,
      JSON.stringify({
        ids: Array.from(notifiedAlertIds),
      }),
    );
  } catch (error) {
    safeError("Failed to save notified IDs:", error);
  }
}

function getDashboardUrl() {
  if (CONFIG.DASHBOARD_URL && !CONFIG.DASHBOARD_URL.includes("/docs")) {
    return CONFIG.DASHBOARD_URL;
  }

  const localIndex = path.join(DASHBOARD_DIR, "index.html");
  if (fs.existsSync(localIndex)) {
    return `file://${localIndex}`;
  }

  return "https://misaka-dashboard.pages.dev";
}

function isValidDashboardUrl(url) {
  if (url.includes("/docs") || url.includes("/redoc")) {
    return false;
  }
  return true;
}

function showErrorWindow(message) {
  const errorWindow = new BrowserWindow({
    width: 500,
    height: 300,
    title: "Misaka - Configuration Error",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  errorWindow.loadURL(
    `data:text/html;charset=utf-8,${encodeURIComponent(`
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    background: #081018;
                    color: #eaf6ff;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    padding: 2rem;
                    text-align: center;
                }
                .error-box {
                    background: rgba(18, 30, 48, 0.72);
                    border: 1px solid rgba(255, 107, 129, 0.3);
                    border-radius: 12px;
                    padding: 2rem;
                    max-width: 400px;
                }
                h1 { color: #68d5ff; margin-bottom: 1rem; }
                p { color: #8faec5; line-height: 1.6; }
                code {
                    background: rgba(104, 213, 255, 0.1);
                    padding: 0.2rem 0.5rem;
                    border-radius: 4px;
                    color: #68d5ff;
                }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>Misaka Desktop</h1>
                <p>${message}</p>
                <p>Configure a variável de ambiente:</p>
                <code>MISAKA_DASHBOARD_URL</code>
            </div>
        </body>
        </html>
    `)}`,
  );
}

function createWindow() {
  const dashboardUrl = getDashboardUrl();

  if (!isValidDashboardUrl(dashboardUrl)) {
    showErrorWindow(
      "Dashboard URL inválida.\nConfigure MISAKA_DASHBOARD_URL para a interface da Misaka.",
    );
    return;
  }

  const preloadPath = path.join(__dirname, "preload.js");
  safeLog("[Misaka Desktop] preload path:", preloadPath);

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "Misaka Network",
    icon: fs.existsSync(path.join(__dirname, "assets", "icon.ico"))
      ? path.join(__dirname, "assets", "icon.ico")
      : undefined,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
      preload: preloadPath,
    },
    alwaysOnTop: CONFIG.ALWAYS_ON_TOP_DEFAULT,
    transparent: CONFIG.TRANSPARENT_MODE_DEFAULT,
    frame: !CONFIG.TRANSPARENT_MODE_DEFAULT,
    show: !CONFIG.START_MINIMIZED,
  });

  mainWindow.loadURL(dashboardUrl);

  mainWindow.webContents.on("did-finish-load", () => {
    mainWindow.webContents
      .executeJavaScript(
        `
            window.__MISAKA_API_BASE_URL__ = '${CONFIG.API_BASE_URL}';
            if (typeof MISAKA_CONFIG !== 'undefined') {
                Object.defineProperty(MISAKA_CONFIG, 'API_BASE_URL', {
                    get: function() { return window.__MISAKA_API_BASE_URL__; }
                });
            }
        `,
      )
      .catch(() => {});
    if (pendingWakeWordEnabled !== null) {
      sendWakeWordState(pendingWakeWordEnabled);
      pendingWakeWordEnabled = null;
    }
  });

  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  createTray();
  setupIPC();
}

function createTray() {
  let icon;
  try {
    icon = nativeImage.createFromPath(
      path.join(__dirname, "assets", "icon.ico"),
    );
  } catch (e) {
    icon = nativeImage.createEmpty();
  }

  tray = new Tray(icon);
  tray.setToolTip("Misaka Network");

  const contextMenu = Menu.buildFromTemplate([
    { label: "Abrir Misaka", click: () => mainWindow.show() },
    {
      label: "Always on top",
      type: "checkbox",
      checked: CONFIG.ALWAYS_ON_TOP_DEFAULT,
      click: (item) => mainWindow.setAlwaysOnTop(item.checked),
    },
    {
      label: "HUD Mode",
      type: "checkbox",
      checked: false,
      click: (item) => {
        mainWindow.webContents
          .executeJavaScript(
            `
                document.body.classList.toggle('hud-mode', ${item.checked});
                localStorage.setItem('misaka_hud_mode', ${item.checked});
            `,
          )
          .catch(() => {});
      },
    },
    {
      label: "Ativar escuta Misaka",
      click: () => setWakeWordFromTray(true),
    },
    {
      label: "Desativar escuta Misaka",
      click: () => setWakeWordFromTray(false),
    },
    { type: "separator" },
    {
      label: "Sair",
      click: () => {
        isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
  tray.on("double-click", () => mainWindow.show());
}

function setWakeWordFromTray(enabled) {
  safeLog("[Misaka Desktop] tray wake-word:set-enabled", enabled);
  if (!mainWindow) return;
  if (mainWindow.isMinimized()) mainWindow.restore();
  mainWindow.show();
  sendWakeWordState(enabled);
}

function sendWakeWordState(enabled) {
  pendingWakeWordEnabled = Boolean(enabled);
  if (
    !mainWindow ||
    mainWindow.isDestroyed() ||
    mainWindow.webContents.isLoading()
  ) {
    return;
  }
  mainWindow.webContents.send("wake-word:set-enabled", {
    enabled: Boolean(enabled),
  });
  pendingWakeWordEnabled = null;
}

function setupMediaPermissions() {
  session.defaultSession.setPermissionRequestHandler(
    (webContents, permission, callback) => {
      if (permission === "media" || permission === "microphone") {
        safeLog("[Misaka Desktop] permission granted:", permission);
        callback(true);
        return;
      }
      safeWarn("[Misaka Desktop] permission denied:", permission);
      callback(false);
    },
  );
}

function findWindowsApp(name) {
  const localAppData = process.env.LOCALAPPDATA || "";
  const programFiles = process.env["PROGRAMFILES"] || "C:\\Program Files";
  const programFilesX86 =
    process.env["PROGRAMFILES(X86)"] || "C:\\Program Files (x86)";

  const searchPaths = [
    path.join(localAppData, "Programs", name),
    path.join(programFiles, name),
    path.join(programFilesX86, name),
    path.join(programFiles, `${name}\\${name}.exe`),
    path.join(programFilesX86, `${name}\\${name}.exe`),
  ];

  for (const p of searchPaths) {
    if (fs.existsSync(p)) return p;
    if (fs.existsSync(`${p}.exe`)) return `${p}.exe`;
  }
  return null;
}

const WINDOWS_APP_LAUNCHERS = {
  browser: () => shell.openExternal("https://www.google.com"),
  chrome: () => {
    const localAppData = process.env.LOCALAPPDATA || "";
    const programFiles = process.env["PROGRAMFILES"] || "C:\\Program Files";
    const programFilesX86 =
      process.env["PROGRAMFILES(X86)"] || "C:\\Program Files (x86)";
    const paths = [
      path.join(programFiles, "Google", "Chrome", "Application", "chrome.exe"),
      path.join(
        programFilesX86,
        "Google",
        "Chrome",
        "Application",
        "chrome.exe",
      ),
      path.join(localAppData, "Google", "Chrome", "Application", "chrome.exe"),
    ];
    const found = paths.find((p) => fs.existsSync(p));
    if (!found)
      throw new Error("Chrome nao encontrado nos caminhos permitidos.");
    spawn(found, [], { detached: true, stdio: "ignore" }).unref();
  },
  edge: () => {
    const localAppData = process.env.LOCALAPPDATA || "";
    const programFiles = process.env["PROGRAMFILES"] || "C:\\Program Files";
    const paths = [
      path.join(localAppData, "Microsoft", "Edge", "Application", "msedge.exe"),
      path.join(programFiles, "Microsoft", "Edge", "Application", "msedge.exe"),
    ];
    const found = paths.find((p) => fs.existsSync(p));
    if (!found) throw new Error("Edge nao encontrado nos caminhos permitidos.");
    spawn(found, [], { detached: true, stdio: "ignore" }).unref();
  },
  vscode: () => {
    const localAppData = process.env.LOCALAPPDATA || "";
    const programFiles = process.env["PROGRAMFILES"] || "C:\\Program Files";
    const paths = [
      path.join(localAppData, "Programs", "Microsoft VS Code", "Code.exe"),
      path.join(programFiles, "Microsoft VS Code", "Code.exe"),
    ];
    const found = paths.find((p) => fs.existsSync(p));
    if (!found)
      throw new Error("VS Code nao encontrado nos caminhos permitidos.");
    spawn(found, [], { detached: true, stdio: "ignore" }).unref();
  },
  explorer: () =>
    spawn("explorer.exe", [], { detached: true, stdio: "ignore" }).unref(),
  discord: () => {
    const localAppData = process.env.LOCALAPPDATA || "";
    const paths = [
      path.join(localAppData, "Discord", "Update.exe"),
      path.join(localAppData, "DiscordCanary", "Update.exe"),
      path.join(localAppData, "DiscordPTB", "Update.exe"),
    ];
    const found = paths.find((p) => fs.existsSync(p));
    if (!found)
      throw new Error("Discord nao encontrado nos caminhos conhecidos.");
    spawn(found, ["--processStart", "Discord.exe"], {
      detached: true,
      stdio: "ignore",
    }).unref();
  },
  notepad: () =>
    spawn("notepad.exe", [], { detached: true, stdio: "ignore" }).unref(),
  calculator: () =>
    spawn("calc.exe", [], { detached: true, stdio: "ignore" }).unref(),
  cmd: () => spawn("cmd.exe", [], { detached: true, stdio: "ignore" }).unref(),
  powershell: () =>
    spawn("powershell.exe", [], { detached: true, stdio: "ignore" }).unref(),
};

function launchApp(appName) {
  safeLog("[Misaka Desktop] openApp requested:", appName);

  if (!appName || typeof appName !== "string") {
    return { success: false, error: "Nome do app obrigatorio." };
  }

  const normalizedApp = appName.toLowerCase().trim();

  if (process.platform !== "win32") {
    return {
      success: false,
      app: normalizedApp,
      error: `Plataforma nao suportada: ${process.platform}`,
    };
  }

  const launcher = WINDOWS_APP_LAUNCHERS[normalizedApp];
  if (!launcher) {
    return {
      success: false,
      app: normalizedApp,
      error: `App "${normalizedApp}" nao esta na allowlist.`,
    };
  }

  try {
    launcher();
    safeLog("[Misaka Desktop] openApp success:", normalizedApp);
    return { success: true, app: normalizedApp, method: "allowlist" };
  } catch (e) {
    safeLog("[Misaka Desktop] openApp failed:", normalizedApp, e.message);
    return {
      success: false,
      app: normalizedApp,
      error: e.message,
    };
  }
}

function isSafeUrl(url) {
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

async function openExternalUrl(url) {
  safeLog("[Misaka Desktop] openUrl requested:", url);
  if (!isSafeUrl(url)) {
    return {
      success: false,
      error: "URL invalida. Use apenas http:// ou https://.",
    };
  }
  try {
    await shell.openExternal(url);
    safeLog("[Misaka Desktop] openUrl success:", url);
    return { success: true, url };
  } catch (e) {
    safeLog("[Misaka Desktop] openUrl failed:", url, e.message);
    return { success: false, url, error: e.message };
  }
}
function setupIPC() {
  ipcMain.handle("get-config", () => CONFIG);

  ipcMain.handle(
    "desktop:show-notification",
    async (_event, { title, body }) => {
      if (Notification.isSupported()) {
        const notification = new Notification({ title, body });
        notification.show();
        notification.on("click", () => mainWindow.show());
        return { success: true };
      }
      return { success: false, error: "Notificacoes nao suportadas." };
    },
  );

  ipcMain.handle("desktop:open-app", async (_event, appName) => {
    const name =
      typeof appName === "string"
        ? appName
        : appName && typeof appName.appName === "string"
          ? appName.appName
          : "";
    return launchApp(name);
  });

  ipcMain.handle("desktop:open-url", async (_event, url) => {
    const target =
      typeof url === "string"
        ? url
        : url && typeof url.url === "string"
          ? url.url
          : "";
    return openExternalUrl(target);
  });

  ipcMain.handle("desktop:search-web", async (_event, payload) => {
    const query =
      payload && typeof payload === "object" ? payload.query : payload;
    const provider =
      payload && typeof payload === "object" ? payload.provider : "google";
    if (!query || typeof query !== "string") {
      return { success: false, error: "Query is required" };
    }
    const encoded = encodeURIComponent(query.trim());
    const urls = {
      google: `https://www.google.com/search?q=${encoded}`,
      youtube: `https://www.youtube.com/results?search_query=${encoded}`,
      github: `https://github.com/search?q=${encoded}&type=repositories`,
      reddit: `https://www.reddit.com/search/?q=${encoded}`,
      modrinth: `https://modrinth.com/mods?q=${encoded}`,
      curseforge: `https://www.curseforge.com/minecraft/search?search=${encoded}`,
    };
    const url = urls[provider] || urls.google;
    const result = await openExternalUrl(url);
    return { ...result, provider: provider || "google", query: query.trim() };
  });

  ipcMain.handle("desktop:system-status", async () => {
    return {
      success: true,
      platform: process.platform,
      hostname: os.hostname(),
      arch: process.arch,
      pid: process.pid,
      memory: process.memoryUsage(),
      uptime: process.uptime(),
    };
  });

  ipcMain.handle("desktop:set-always-on-top", async (_event, enabled) => {
    mainWindow.setAlwaysOnTop(Boolean(enabled));
    return { success: true, alwaysOnTop: Boolean(enabled) };
  });

  ipcMain.handle("desktop:set-hud-mode", async (_event, enabled) => {
    const flag = Boolean(enabled);
    mainWindow.webContents
      .executeJavaScript(
        `
            document.body.classList.toggle('hud-mode', ${flag});
            localStorage.setItem('misaka_hud_mode', ${flag});
        `,
      )
      .catch(() => {});
    return { success: true };
  });

  ipcMain.handle("desktop:focus-window", async () => {
    mainWindow.show();
    mainWindow.focus();
    return { success: true };
  });

  // Backward-compatible aliases
  ipcMain.handle("open-app", (_event, payload) =>
    launchApp(typeof payload === "object" ? payload.appName : payload),
  );
  ipcMain.handle("open-url", async (_event, payload) =>
    openExternalUrl(typeof payload === "object" ? payload.url : payload),
  );
  ipcMain.handle("search-web", async (_event, payload) => {
    const query =
      payload && typeof payload === "object" ? payload.query : payload;
    const provider =
      payload && typeof payload === "object" ? payload.provider : "google";
    if (!query || typeof query !== "string") {
      return { success: false, error: "Query is required" };
    }
    const encoded = encodeURIComponent(query.trim());
    const urls = {
      google: `https://www.google.com/search?q=${encoded}`,
      youtube: `https://www.youtube.com/results?search_query=${encoded}`,
      github: `https://github.com/search?q=${encoded}&type=repositories`,
      reddit: `https://www.reddit.com/search/?q=${encoded}`,
      modrinth: `https://modrinth.com/mods?q=${encoded}`,
      curseforge: `https://www.curseforge.com/minecraft/search?search=${encoded}`,
    };
    const url = urls[provider] || urls.google;
    const result = await openExternalUrl(url);
    return { ...result, provider: provider || "google", query: query.trim() };
  });

  // --- Native Voice IPC ---
  function ensureNativeVoiceBridge() {
    if (!nativeVoiceBridge) {
      const { NativeVoiceBridge } = require("./voice/nativeVoiceBridge");
      nativeVoiceBridge = new NativeVoiceBridge(mainWindow);
    }
    return nativeVoiceBridge;
  }

  ipcMain.handle("native-voice:is-available", () => {
    try {
      return ensureNativeVoiceBridge().isAvailable();
    } catch (error) {
      safeError("[Misaka Desktop] native voice availability error:", error);
      return false;
    }
  });

  ipcMain.handle("native-voice:start", (_event, modelPath) => {
    try {
      return ensureNativeVoiceBridge().start(modelPath);
    } catch (error) {
      safeError("[Misaka Desktop] native voice start error:", error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle("native-voice:stop", () => {
    try {
      if (nativeVoiceBridge) return nativeVoiceBridge.stop();
      return { success: true };
    } catch (error) {
      safeError("[Misaka Desktop] native voice stop error:", error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle("native-voice:restart", (_event, modelPath) => {
    try {
      return ensureNativeVoiceBridge().restart(modelPath);
    } catch (error) {
      safeError("[Misaka Desktop] native voice restart error:", error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle("native-voice:status", () => {
    try {
      if (nativeVoiceBridge) return nativeVoiceBridge.status();
      return { state: "stopped", lastError: "", running: false };
    } catch (error) {
      safeError("[Misaka Desktop] native voice status error:", error);
      return { state: "error", lastError: error.message, running: false };
    }
  });

  ipcMain.handle("native-voice:diagnostics", () => {
    try {
      return ensureNativeVoiceBridge().diagnostics();
    } catch (error) {
      safeError("[Misaka Desktop] native voice diagnostics error:", error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle("native-voice:open-folder", (_event, folderPath) => {
    try {
      return ensureNativeVoiceBridge().openFolder(folderPath);
    } catch (error) {
      safeError("[Misaka Desktop] open folder error:", error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle("native-voice:open-docs", () => {
    try {
      return ensureNativeVoiceBridge().openDocs();
    } catch (error) {
      safeError("[Misaka Desktop] open docs error:", error);
      return { success: false, error: error.message };
    }
  });
}

function setupPolling() {
  setInterval(async () => {
    try {
      const response = await fetch(
        `${CONFIG.API_BASE_URL}/notifications/alerts`,
      );
      const data = await response.json();

      if (data.alerts && data.alerts.length > 0) {
        const criticalAlerts = data.alerts.filter(
          (a) => a.priority === "critical" && !notifiedAlertIds.has(a.id),
        );

        criticalAlerts.forEach((alert) => {
          if (Notification.isSupported()) {
            const notification = new Notification({
              title: alert.title,
              body: alert.message,
            });
            notification.show();
            notification.on("click", () => mainWindow.show());
          }
          notifiedAlertIds.add(alert.id);
        });

        saveNotifiedIds();
      }
    } catch (error) {
      safeError("Polling error:", error);
    }
  }, 10000);
}

app.whenReady().then(() => {
  loadNotifiedIds();
  setupMediaPermissions();
  createWindow();
  setupPolling();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  isQuitting = true;
});
