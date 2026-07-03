const { contextBridge, ipcRenderer } = require("electron");

function invoke(channel, payload) {
  return ipcRenderer.invoke(channel, payload);
}

contextBridge.exposeInMainWorld("misakaDesktop", {
  isAvailable: true,

  openUrl: (url) => {
    if (typeof url !== "string") {
      return Promise.resolve({ success: false, error: "URL invalida." });
    }
    return invoke("desktop:open-url", url);
  },

  openApp: (appName) => {
    if (typeof appName !== "string") {
      return Promise.resolve({ success: false, error: "Nome do app invalido." });
    }
    return invoke("desktop:open-app", appName);
  },

  searchWeb: (query, provider) =>
    invoke("desktop:search-web", { query, provider }),

  showNotification: (title, body) =>
    invoke("desktop:show-notification", { title, body }),

  getSystemStatus: () => invoke("desktop:system-status"),

  setHudMode: (enabled) =>
    invoke("desktop:set-hud-mode", Boolean(enabled)),

  setAlwaysOnTop: (enabled) =>
    invoke("desktop:set-always-on-top", Boolean(enabled)),

  focusWindow: () => invoke("desktop:focus-window"),

  getConfig: () => invoke("get-config"),

  onWakeWordSetEnabled: (callback) => {
    if (typeof callback !== "function") return () => {};
    const listener = (_event, payload) => {
      const enabled =
        typeof payload === "object" && payload !== null
          ? Boolean(payload.enabled)
          : Boolean(payload);
      callback(enabled);
    };
    ipcRenderer.on("wake-word:set-enabled", listener);
    return () => ipcRenderer.removeListener("wake-word:set-enabled", listener);
  },

  // --- Native Voice ---
  nativeVoiceIsAvailable: () => invoke("native-voice:is-available"),

  nativeVoiceDiagnostics: () => invoke("native-voice:diagnostics"),

  nativeVoiceStart: (modelPath) =>
    invoke("native-voice:start", typeof modelPath === "string" ? modelPath : undefined),

  nativeVoiceStop: () => invoke("native-voice:stop"),

  nativeVoiceRestart: (modelPath) =>
    invoke("native-voice:restart", typeof modelPath === "string" ? modelPath : undefined),

  nativeVoiceStatus: () => invoke("native-voice:status"),

  nativeVoiceOpenFolder: (folderPath) =>
    invoke("native-voice:open-folder", typeof folderPath === "string" ? folderPath : undefined),

  nativeVoiceOpenDocs: () => invoke("native-voice:open-docs"),

  onNativeVoiceTranscript: (callback) => {
    if (typeof callback !== "function") return () => {};
    const listener = (_event, data) => callback(data);
    ipcRenderer.on("native-voice:transcript", listener);
    return () => ipcRenderer.removeListener("native-voice:transcript", listener);
  },

  onNativeVoiceCommand: (callback) => {
    if (typeof callback !== "function") return () => {};
    const listener = (_event, data) => callback(data);
    ipcRenderer.on("native-voice:command", listener);
    return () => ipcRenderer.removeListener("native-voice:command", listener);
  },

  onNativeVoiceStatus: (callback) => {
    if (typeof callback !== "function") return () => {};
    const listener = (_event, data) => callback(data);
    ipcRenderer.on("native-voice:status", listener);
    return () => ipcRenderer.removeListener("native-voice:status", listener);
  },

  onNativeVoiceError: (callback) => {
    if (typeof callback !== "function") return () => {};
    const listener = (_event, data) => callback(data);
    ipcRenderer.on("native-voice:error", listener);
    return () => ipcRenderer.removeListener("native-voice:error", listener);
  },
});
