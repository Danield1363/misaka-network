const { app, BrowserWindow, Tray, Menu, nativeImage, Notification, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

let mainWindow;
let tray;
let isQuitting = false;
let notifiedAlertIds = new Set();

const isPackaged = app.isPackaged;

function getDashboardDir() {
    if (isPackaged) {
        const resourcePath = path.join(process.resourcesPath, 'dashboard');
        if (fs.existsSync(resourcePath)) return resourcePath;
        return path.join(process.resourcesPath, 'app', 'dashboard');
    }
    return path.join(__dirname, '..', 'dashboard');
}

const DASHBOARD_DIR = getDashboardDir();

const CONFIG = {
    API_BASE_URL: process.env.MISAKA_API_BASE_URL || 'https://p01--misaka-network--nf5wq7twf8xg.code.run/api',
    DASHBOARD_URL: process.env.MISAKA_DASHBOARD_URL || '',
    START_MINIMIZED: process.env.START_MINIMIZED === 'true',
    ALWAYS_ON_TOP_DEFAULT: process.env.ALWAYS_ON_TOP_DEFAULT === 'true',
    TRANSPARENT_MODE_DEFAULT: process.env.TRANSPARENT_MODE_DEFAULT === 'true',
};

const NOTIFIED_IDS_FILE = path.join(app.getPath('userData'), 'notified_alerts.json');

function loadNotifiedIds() {
    try {
        if (fs.existsSync(NOTIFIED_IDS_FILE)) {
            const data = JSON.parse(fs.readFileSync(NOTIFIED_IDS_FILE, 'utf-8'));
            notifiedAlertIds = new Set(data.ids || []);
        }
    } catch (error) {
        console.error('Failed to load notified IDs:', error);
    }
}

function saveNotifiedIds() {
    try {
        fs.writeFileSync(NOTIFIED_IDS_FILE, JSON.stringify({
            ids: Array.from(notifiedAlertIds),
        }));
    } catch (error) {
        console.error('Failed to save notified IDs:', error);
    }
}

function getDashboardUrl() {
    if (CONFIG.DASHBOARD_URL && !CONFIG.DASHBOARD_URL.includes('/docs')) {
        return CONFIG.DASHBOARD_URL;
    }

    const localIndex = path.join(DASHBOARD_DIR, 'index.html');
    if (fs.existsSync(localIndex)) {
        return `file://${localIndex}`;
    }

    return 'https://misaka-dashboard.pages.dev';
}

function isValidDashboardUrl(url) {
    if (url.includes('/docs') || url.includes('/redoc')) {
        return false;
    }
    return true;
}

function showErrorWindow(message) {
    const errorWindow = new BrowserWindow({
        width: 500,
        height: 300,
        title: 'Misaka - Configuration Error',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    errorWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(`
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
    `)}`);
}

function createWindow() {
    const dashboardUrl = getDashboardUrl();

    if (!isValidDashboardUrl(dashboardUrl)) {
        showErrorWindow('Dashboard URL inválida. Configure MISAKA_DASHBOARD_URL para a interface da Misaka.');
        return;
    }

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        title: 'Misaka Network',
        icon: path.join(__dirname, 'assets', 'icon.ico'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
        },
        alwaysOnTop: CONFIG.ALWAYS_ON_TOP_DEFAULT,
        transparent: CONFIG.TRANSPARENT_MODE_DEFAULT,
        frame: !CONFIG.TRANSPARENT_MODE_DEFAULT,
        show: !CONFIG.START_MINIMIZED,
    });

    mainWindow.loadURL(dashboardUrl);

    mainWindow.webContents.on('did-finish-load', () => {
        mainWindow.webContents.executeJavaScript(`
            if (typeof MISAKA_CONFIG !== 'undefined') {
                MISAKA_CONFIG.API_BASE_URL = '${CONFIG.API_BASE_URL}';
            }
        `).catch(() => {});
    });

    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    mainWindow.on('tray-clicked', () => {
        mainWindow.show();
    });

    createTray();
    setupIPC();
}

function createTray() {
    let icon;
    try {
        icon = nativeImage.createFromPath(path.join(__dirname, 'assets', 'icon.ico'));
    } catch (e) {
        icon = nativeImage.createEmpty();
    }

    tray = new Tray(icon);
    tray.setToolTip('Misaka Network');

    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show Misaka', click: () => mainWindow.show() },
        { label: 'Always on Top', type: 'checkbox', checked: CONFIG.ALWAYS_ON_TOP_DEFAULT, click: (item) => mainWindow.setAlwaysOnTop(item.checked) },
        { label: 'HUD Mode', type: 'checkbox', checked: false, click: (item) => {
            mainWindow.webContents.executeJavaScript(`
                document.body.classList.toggle('hud-mode', ${item.checked});
                localStorage.setItem('misaka_hud_mode', ${item.checked});
            `).catch(() => {});
        }},
        { type: 'separator' },
        { label: 'Quit', click: () => { isQuitting = true; app.quit(); } },
    ]);

    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => mainWindow.show());
}

function findWindowsApp(name) {
    const localAppData = process.env.LOCALAPPDATA || '';
    const programFiles = process.env['PROGRAMFILES'] || 'C:\\Program Files';
    const programFilesX86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';

    const searchPaths = [
        path.join(localAppData, 'Programs', name),
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
    browser: () => shell.openExternal('https://www.google.com'),
    chrome: () => {
        const found = findWindowsApp('Google\\Chrome\\Application\\chrome.exe');
        if (found) spawn(found, [], { detached: true, stdio: 'ignore' }).unref();
        else shell.openExternal('https://www.google.com');
    },
    firefox: () => {
        const found = findWindowsApp('Mozilla Firefox\\firefox.exe');
        if (found) spawn(found, [], { detached: true, stdio: 'ignore' }).unref();
        else shell.openExternal('https://www.google.com');
    },
    edge: () => {
        const found = findWindowsApp('Microsoft\\Edge\\Application\\msedge.exe');
        if (found) spawn(found, [], { detached: true, stdio: 'ignore' }).unref();
        else shell.openExternal('https://www.google.com');
    },
    vscode: () => {
        const found = findWindowsApp('Microsoft VS Code');
        if (found) spawn(found, [], { detached: true, stdio: 'ignore' }).unref();
        else spawn('code', [], { detached: true, stdio: 'ignore' }).unref();
    },
    explorer: () => spawn('explorer', [], { detached: true, stdio: 'ignore' }).unref(),
    discord: () => {
        const found = findWindowsApp('Discord');
        if (found) spawn(found, [], { detached: true, stdio: 'ignore' }).unref();
        else shell.openExternal('https://discord.com/app');
    },
    youtube: () => shell.openExternal('https://www.youtube.com'),
    spotify: () => shell.openExternal('https://open.spotify.com'),
};

function launchApp(appName) {
    if (process.platform === 'win32') {
        const launcher = WINDOWS_APP_LAUNCHERS[appName];
        if (launcher) {
            try { launcher(); } catch (e) { /* fallback */ }
            return { success: true, app: appName };
        }
        shell.openExternal(appName);
        return { success: true, app: appName };
    }
    shell.openExternal(appName);
    return { success: true, app: appName };
}

function setupIPC() {
    ipcMain.handle('get-config', () => CONFIG);

    ipcMain.handle('send-notification', (event, { title, body }) => {
        if (Notification.isSupported()) {
            const notification = new Notification({ title, body });
            notification.show();
            notification.on('click', () => mainWindow.show());
        }
    });

    ipcMain.handle('open-app', (event, { appName }) => {
        return launchApp(appName);
    });

    ipcMain.handle('open-url', (event, { url }) => {
        shell.openExternal(url);
        return { success: true };
    });

    ipcMain.handle('get-system-status', () => {
        return {
            platform: process.platform,
            hostname: os.hostname(),
            arch: process.arch,
            pid: process.pid,
            memory: process.memoryUsage(),
            uptime: process.uptime(),
        };
    });

    ipcMain.handle('set-always-on-top', (event, { enabled }) => {
        mainWindow.setAlwaysOnTop(enabled);
        return { success: true, alwaysOnTop: enabled };
    });

    ipcMain.handle('set-hud-mode', (event, { enabled }) => {
        mainWindow.webContents.executeJavaScript(`
            document.body.classList.toggle('hud-mode', ${enabled});
            localStorage.setItem('misaka_hud_mode', ${enabled});
        `).catch(() => {});
        return { success: true };
    });

    ipcMain.handle('focus-window', () => {
        mainWindow.show();
        mainWindow.focus();
        return { success: true };
    });

    ipcMain.handle('toggle-compact', (event, { enabled }) => {
        mainWindow.webContents.executeJavaScript(`
            document.body.classList.toggle('compact-mode', ${enabled});
            localStorage.setItem('misaka_compact_mode', ${enabled});
        `).catch(() => {});
        return { success: true };
    });

    ipcMain.handle('request-action', (event, action) => {
        return { received: true, action };
    });
}

function setupPolling() {
    setInterval(async () => {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/notifications/alerts`);
            const data = await response.json();

            if (data.alerts && data.alerts.length > 0) {
                const criticalAlerts = data.alerts.filter(
                    a => a.priority === 'critical' && !notifiedAlertIds.has(a.id)
                );

                criticalAlerts.forEach(alert => {
                    if (Notification.isSupported()) {
                        const notification = new Notification({
                            title: alert.title,
                            body: alert.message,
                        });
                        notification.show();
                        notification.on('click', () => mainWindow.show());
                    }
                    notifiedAlertIds.add(alert.id);
                });

                saveNotifiedIds();
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 10000);
}

app.whenReady().then(() => {
    loadNotifiedIds();
    createWindow();
    setupPolling();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    isQuitting = true;
});
