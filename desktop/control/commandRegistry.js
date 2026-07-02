const commands = new Map();

function registerCommand(name, handler, riskLevel = 'safe') {
    commands.set(name, { handler, riskLevel });
}

function getCommand(name) {
    return commands.get(name);
}

function listCommands() {
    const list = [];
    commands.forEach((value, key) => {
        list.push({ name: key, riskLevel: value.riskLevel });
    });
    return list;
}

function hasCommand(name) {
    return commands.has(name);
}

// Default safe commands
registerCommand('open_app', async (args) => {
    const { openApp } = require('./pcController');
    return openApp(args.appName);
}, 'safe');

registerCommand('open_url', async (args) => {
    const { openUrl } = require('./pcController');
    return openUrl(args.url);
}, 'safe');

registerCommand('get_system_status', async () => {
    const { getSystemStatus } = require('./pcController');
    return getSystemStatus();
}, 'safe');

module.exports = { registerCommand, getCommand, listCommands, hasCommand };
