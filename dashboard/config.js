const MISAKA_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000/api'
        : 'https://p01--misaka-network--nf5wq7twf8xg.code.run/api',
    APP_NAME: 'Misaka Dashboard',
    VERSION: '0.1 Genesis'
};