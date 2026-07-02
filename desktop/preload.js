const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('misakaDesktop', {
    getConfig: () => ipcRenderer.invoke('get-config'),
    sendNotification: (title, body) => ipcRenderer.invoke('send-notification', { title, body })
});