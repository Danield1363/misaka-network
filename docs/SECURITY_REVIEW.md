# Security Review — Misaka v0.3 Genesis

## Current Risks

| Risk | Level | Status |
|------|-------|--------|
| API key exposure | HIGH | Mitigated — keys in .env only, never in frontend |
| Shell injection | HIGH | Mitigated — no arbitrary shell commands allowed |
| Token leakage | HIGH | Mitigated — tokens never in dashboard or desktop bundle |
| Action abuse | MEDIUM | Mitigated — confirmation system for sensitive/dangerous |
| Data exfiltration | MEDIUM | Mitigated — no raw audio sent, only text |
| Supply chain | LOW | Mitigated — dependencies pinned, no auto-updates |

## Blocked Actions (Critical — Never Execute)

- `shutdown` — Shutdown PC
- `restart` — Restart PC
- `delete_files` — Delete files
- `shell_arbitrary` — Run arbitrary commands
- `install_software` — Install software
- `modify_system` — Modify system settings

These actions are defined in `desktop/control/permissions.js` and `BLOCKED_ACTIONS` set. They return an error if attempted.

## Actions Requiring Confirmation

| Action | Risk Level | Requires |
|--------|-----------|----------|
| Close app | SENSITIVE | One-time approval |
| Send message | SENSITIVE | One-time approval |
| Change settings | SENSITIVE | One-time approval |
| Run terminal command | SENSITIVE | One-time approval |
| Download file | SENSITIVE | One-time approval |
| Clear chat history | SAFE | None |
| Open app/URL | SAFE | None |
| Read status | SAFE | None |

## Token Configuration

| Token | Location | Purpose |
|-------|----------|---------|
| GEMINI_API_KEY | `.env` | Gemini LLM access |
| SUPABASE_SERVICE_ROLE_KEY | `.env` | Database access |
| NOTIFICATION_INGEST_TOKEN | `.env` | Bridge authentication |

**Never commit these values.** Use `.env.example` as template.

## What Never to Commit

- `.env` files
- `*.key` files
- `credentials.json`
- `service-account*.json`
- `notified_alerts.json` (contains alert IDs)
- `desktop/node_modules/` (already gitignored)

## Dashboard Security

- Uses `textContent` (not `innerHTML`) — XSS safe
- CORS configured for specific origins only
- No inline scripts from external sources
- API keys never injected into frontend

## Desktop Security

- `contextIsolation: true` — Renderer can't access Node
- `nodeIntegration: false` — No direct Node access from web
- IPC bridge only exposes whitelisted functions
- App launcher uses allowlist, not arbitrary commands
- Preload script is the only bridge between main and renderer
