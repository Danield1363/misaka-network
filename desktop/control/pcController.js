const os = require('os');
const { shell } = require('electron');

const APP_MAP = {
    browser: null,
    chrome: process.platform === 'win32' ? 'chrome' : 'google-chrome',
    firefox: process.platform === 'win32' ? 'firefox' : 'firefox',
    edge: process.platform === 'win32' ? 'msedge' : 'microsoft-edge',
    discord: process.platform === 'win32' ? 'Discord' : 'discord',
    vscode: process.platform === 'win32' ? 'code' : 'code',
    explorer: process.platform === 'win32' ? 'explorer' : 'nautilus',
    youtube: 'https://www.youtube.com',
    spotify: process.platform === 'win32' ? 'spotify' : 'spotify',
};

function openApp(appName) {
    const cmd = APP_MAP[appName];
    if (cmd === null || cmd === undefined) {
        return { success: false, error: `Unknown app: ${appName}` };
    }
    if (cmd.startsWith('http')) {
        shell.openExternal(cmd);
    } else {
        shell.openExternal(cmd).catch(() => {});
    }
    return { success: true, app: appName };
}

function openUrl(url) {
    shell.openExternal(url);
    return { success: true, url };
}

function getSystemStatus() {
    return {
        platform: process.platform,
        hostname: os.hostname(),
        arch: process.arch,
        cpus: os.cpus().length,
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        uptime: os.uptime(),
        pid: process.pid,
    };
}

module.exports = { openApp, openUrl, getSystemStatus, APP_MAP };
