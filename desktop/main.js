const { app, BrowserWindow, Tray, Menu, nativeImage, Notification, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;
let tray;
let isQuitting = false;
let notifiedAlertIds = new Set();

const CONFIG = {
    API_BASE_URL: process.env.MISAKA_API_BASE_URL || 'https://p01--misaka-network--nf5wq7twf8xg.code.run/api',
    DASHBOARD_URL: process.env.MISAKA_DASHBOARD_URL || 'https://misaka-dashboard.pages.dev',
    START_MINIMIZED: process.env.START_MINIMIZED === 'true',
    ALWAYS_ON_TOP_DEFAULT: process.env.ALWAYS_ON_TOP_DEFAULT === 'true',
    TRANSPARENT_MODE_DEFAULT: process.env.TRANSPARENT_MODE_DEFAULT === 'true'
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
            ids: Array.from(notifiedAlertIds)
        }));
    } catch (error) {
        console.error('Failed to save notified IDs:', error);
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        title: 'Misaka Network',
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        alwaysOnTop: CONFIG.ALWAYS_ON_TOP_DEFAULT,
        transparent: CONFIG.TRANSPARENT_MODE_DEFAULT,
        frame: !CONFIG.TRANSPARENT_MODE_DEFAULT
    });

    mainWindow.loadURL(CONFIG.DASHBOARD_URL);

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
    const icon = nativeImage.createEmpty();
    tray = new Tray(icon);
    tray.setToolTip('Misaka Network');

    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show Misaka', click: () => mainWindow.show() },
        { label: 'Always on Top', type: 'checkbox', checked: CONFIG.ALWAYS_ON_TOP_DEFAULT, click: (item) => mainWindow.setAlwaysOnTop(item.checked) },
        { type: 'separator' },
        { label: 'Quit', click: () => { isQuitting = true; app.quit(); } }
    ]);

    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => mainWindow.show());
}

function setupIPC() {
    ipcMain.handle('get-config', () => CONFIG);

    ipcMain.handle('send-notification', (event, { title, body }) => {
        if (Notification.isSupported()) {
            const notification = new Notification({ title, body });
            notification.show();
        }
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
                        new Notification({
                            title: alert.title,
                            body: alert.message
                        }).show();
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