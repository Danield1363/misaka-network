const MISAKA_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000/api'
        : 'https://p01--misaka-network--nf5wq7twf8xg.code.run/api',
    APP_NAME: 'Misaka Dashboard',
    VERSION: '0.3 Genesis',
    POLL_INTERVAL_MS: 15000,
    ALERTS_POLL_INTERVAL_MS: 10000,
    ENABLE_VOICE: true,
    ENABLE_DESKTOP_NOTIFICATIONS: true,
    ENABLE_HUD_MODE: true,
    ENABLE_WAKE_WORD: true,
};
