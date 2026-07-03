function resolveApiBaseUrl() {
  if (typeof window !== "undefined" && window.__MISAKA_API_BASE_URL__) {
    return window.__MISAKA_API_BASE_URL__;
  }

  const host = window.location.hostname;
  const protocol = window.location.protocol;
  const isElectronBridge =
    typeof window !== "undefined" &&
    window.misakaDesktop &&
    window.misakaDesktop.isAvailable;
  const isLocalHost =
    host === "localhost" || host === "127.0.0.1" || host === "";
  const isFileProtocol = protocol === "file:";

  if (isLocalHost || isFileProtocol || isElectronBridge) {
    return "http://127.0.0.1:8000/api";
  }

  return "https://p01--misaka-network--nf5wq7twf8xg.code.run/api";
}

const MISAKA_CONFIG = {
  get API_BASE_URL() {
    return resolveApiBaseUrl();
  },
  APP_NAME: "Misaka Dashboard",
  VERSION: "0.3.5",
  POLL_INTERVAL_MS: 15000,
  ALERTS_POLL_INTERVAL_MS: 10000,
  ENABLE_VOICE: true,
  ENABLE_DESKTOP_NOTIFICATIONS: true,
  ENABLE_HUD_MODE: true,
  ENABLE_WAKE_WORD: true,
};
