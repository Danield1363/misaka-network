# Security Model

Misaka follows a strict security model for all operations.

## Risk Classification

| Level | Description | Auto-Execute | Examples |
|-------|-------------|:------------:|----------|
| **SAFE** | No side effects | Yes | Open app, clear chat, read status |
| **SENSITIVE** | Minor side effects | No | Close app, send message, change settings |
| **HIGH** | Significant side effects | No | Run commands, download files |
| **CRITICAL** | Destructive/risky | No (blocked) | Shutdown, delete files, shell arbitrary |

## Rules

1. **No dangerous action executes without explicit confirmation**
2. **Shell arbitrary commands are disabled by default**
3. **All actions generate action logs**
4. **Tokens are never exposed in the frontend**
5. **Secrets are never placed in dashboard or desktop bundle**

## Desktop Security

- `contextIsolation: true` — Renderer cannot access Node
- `nodeIntegration: false` — No direct Node access from web
- All commands validated in main process
- IPC bridge only exposes whitelisted functions

## API Security

- CORS configured for specific origins
- Ingest token required for notification ingestion
- Supabase service role key only in backend
- No secrets in frontend code

## Token Handling

- API keys stored in `.env` files (gitignored)
- Never included in desktop builds
- Never sent to frontend
- Backend only environment variables
