const os = require('os');

function getCpuUsage() {
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;
    cpus.forEach(cpu => {
        for (const type in cpu.times) {
            totalTick += cpu.times[type];
        }
        totalIdle += cpu.times.idle;
    });
    return {
        idle: totalIdle / cpus.length,
        total: totalTick / cpus.length,
        count: cpus.length,
        model: cpus[0]?.model || 'unknown',
    };
}

function getMemoryInfo() {
    return {
        total: os.totalmem(),
        free: os.freemem(),
        used: os.totalmem() - os.freemem(),
        usagePercent: ((os.totalmem() - os.freemem()) / os.totalmem() * 100).toFixed(1),
    };
}

function getNetworkInfo() {
    const interfaces = os.networkInterfaces();
    const addresses = [];
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                addresses.push({ name, address: iface.address });
            }
        }
    }
    return addresses;
}

function getFullStatus() {
    return {
        platform: process.platform,
        arch: process.arch,
        hostname: os.hostname(),
        uptime: os.uptime(),
        cpu: getCpuUsage(),
        memory: getMemoryInfo(),
        network: getNetworkInfo(),
        nodeVersion: process.version,
        pid: process.pid,
    };
}

module.exports = { getCpuUsage, getMemoryInfo, getNetworkInfo, getFullStatus };
