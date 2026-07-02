const RISK_LEVELS = {
    safe: { requiresConfirmation: false },
    medium: { requiresConfirmation: true },
    high: { requiresConfirmation: true },
    critical: { requiresConfirmation: true, blockedByDefault: true },
};

const BLOCKED_ACTIONS = new Set([
    'shutdown',
    'restart',
    'delete_files',
    'shell_arbitrary',
]);

function isActionBlocked(actionName) {
    return BLOCKED_ACTIONS.has(actionName);
}

function requiresConfirmation(actionName, riskLevel) {
    const level = RISK_LEVELS[riskLevel];
    if (!level) return true;
    return level.requiresConfirmation;
}

function validateAction(actionName, riskLevel) {
    if (isActionBlocked(actionName)) {
        return { allowed: false, reason: 'Action blocked by default' };
    }
    if (requiresConfirmation(actionName, riskLevel)) {
        return { allowed: false, reason: 'Requires confirmation', requiresConfirmation: true };
    }
    return { allowed: true };
}

module.exports = { isActionBlocked, requiresConfirmation, validateAction, RISK_LEVELS, BLOCKED_ACTIONS };
