const os = require('os');
const path = require('path');
const fs = require('fs');
const { shell } = require('electron');
const { spawn } = require('child_process');

function findWindowsApp(searchPaths) {
    for (const p of searchPaths) {
        if (fs.existsSync(p)) return p;
    }
    return null;
}

function getWindowsAppPath(appName) {
    const localAppData = process.env.LOCALAPPDATA || '';
    const programFiles = process.env['PROGRAMFILES'] || 'C:\\Program Files';
    const programFilesX86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';

    const paths = {
        chrome: [
            path.join(localAppData, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            path.join(programFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            path.join(programFilesX86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
        ],
        firefox: [
            path.join(programFiles, 'Mozilla Firefox', 'firefox.exe'),
            path.join(programFilesX86, 'Mozilla Firefox', 'firefox.exe'),
        ],
        edge: [
            path.join(localAppData, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            path.join(programFiles, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        ],
        vscode: [
            path.join(localAppData, 'Programs', 'Microsoft VS Code', 'Code.exe'),
            path.join(programFiles, 'Microsoft VS Code', 'Code.exe'),
            path.join(programFilesX86, 'Microsoft VS Code', 'Code.exe'),
        ],
        discord: [
            path.join(localAppData, 'Discord', 'Update.exe'),
            path.join(programFiles, 'Discord', 'Update.exe'),
        ],
    };

    return findWindowsApp(paths[appName] || []);
}

function openApp(appName) {
    if (process.platform === 'win32') {
        if (appName === 'explorer') {
            spawn('explorer', [], { detached: true, stdio: 'ignore' }).unref();
            return { success: true, app: appName };
        }

        const appPath = getWindowsAppPath(appName);
        if (appPath) {
            spawn(appPath, [], { detached: true, stdio: 'ignore' }).unref();
            return { success: true, app: appName, path: appPath };
        }

        return { success: false, error: `App "${appName}" not found on this system.` };
    }

    if (['youtube', 'spotify'].includes(appName)) {
        const urls = {
            youtube: 'https://www.youtube.com',
            spotify: 'https://open.spotify.com',
        };
        shell.openExternal(urls[appName] || '');
        return { success: true, app: appName };
    }

    return { success: false, error: `Unsupported platform: ${process.platform}` };
}

function openUrl(url) {
    shell.openExternal(url);
    return { success: true, url };
}

function getSystemStatus() {
    return {
        platform: process.platform,
        hostname: os.hostname(),
        arch: os.arch(),
        cpus: os.cpus().length,
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        uptime: os.uptime(),
        pid: process.pid,
    };
}

module.exports = { openApp, openUrl, getSystemStatus };
