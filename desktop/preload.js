const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("misakaDesktop", {
  isAvailable: true,

  getConfig: () => ipcRenderer.invoke("get-config"),

  sendNotification: (title, body) =>
    ipcRenderer.invoke("send-notification", { title, body }),

  openApp: (appName) => ipcRenderer.invoke("open-app", { appName }),

  openUrl: (url) => ipcRenderer.invoke("open-url", { url }),

  searchWeb: (query, provider) =>
    ipcRenderer.invoke("search-web", { query, provider }),

  getSystemStatus: () => ipcRenderer.invoke("get-system-status"),

  setAlwaysOnTop: (enabled) =>
    ipcRenderer.invoke("set-always-on-top", { enabled }),

  setHudMode: (enabled) => ipcRenderer.invoke("set-hud-mode", { enabled }),

  focusWindow: () => ipcRenderer.invoke("focus-window"),

  toggleCompact: (enabled) => ipcRenderer.invoke("toggle-compact", { enabled }),

  requestAction: (action) => ipcRenderer.invoke("request-action", action),

  onWakeWordSetEnabled: (callback) => {
    ipcRenderer.removeAllListeners("wake-word:set-enabled");
    ipcRenderer.on("wake-word:set-enabled", (event, payload) =>
      callback(payload),
    );
  },
});
