const MISAKA_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000/api'
        : 'https://misaka-core.northflank.app/api',
    APP_NAME: 'Misaka Dashboard',
    VERSION: '0.1 Genesis'
};