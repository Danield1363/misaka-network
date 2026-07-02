# Misaka Network — Project Status

## Current Version: v0.3 Genesis Foundation

Misaka is a personal AI assistant with voice, commands, safe PC control, mobile bridge, and a packaged desktop app.

## What Misaka Does Today

### Backend (FastAPI)
- **Brain Engine** — Central coordinator for intent detection, agent routing, memory
- **LLM Gateway** — Gemini with 3-tier fallback (Pro → Flash → Flash-lite)
- **Command Router** — 25+ Portuguese intent patterns for natural language commands
- **Notification Engine** — Ingest, classify, alert, and manage notifications
- **Memory Engine** — Create, search, and recall memories (Supabase)
- **Task Engine** — Create, list, complete tasks (Supabase)
- **Calendar Engine** — Events, reminders, scheduler (Supabase)
- **Android Bridge** — Action queue for MacroDroid/Tasker polling
- **Action Approvals** — Confirmation system for sensitive operations
- **Tools Registry** — 30+ tools across notifications, UI, desktop, Android

### Dashboard (HTML/CSS/JS)
- Chat with Misaka (text responses with voice)
- Voice system with auto-speak, presets, rate/pitch control
- HUD overlay mode
- Settings drawer with LLM, voice, bridge status
- Alert management with filters and ack-all
- Toast notification system
- Confirmation modal for sensitive actions
- Wake word (experimental)

### Desktop App (Electron)
- Opens dashboard (local or remote)
- System tray with show/always-on-top/HUD/quit
- Native desktop notifications
- PC control bridge (open apps, URLs, system status)
- .exe generation via electron-builder
- Secure IPC (contextIsolation, no Node in renderer)

## How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Dashboard: http://localhost:8000/docs

### Dashboard (standalone)
```bash
cd dashboard
# Serve with any static file server
python -m http.server 3000
```
Open: http://localhost:3000

### Desktop App
```bash
cd desktop
npm install
npm start          # Run app
npm run debug      # Run with logs
npm run dist       # Build .exe
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `mock` | `mock` or `gemini` |
| `GEMINI_API_KEY` | `""` | Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-pro` | Primary model |
| `GEMINI_FALLBACK_MODEL` | `gemini-2.5-flash` | First fallback |
| `SUPABASE_URL` | `""` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | `""` | Supabase service key |
| `MEMORY_ENABLED` | `false` | Enable memory engine |
| `NOTIFICATIONS_ENABLED` | `false` | Enable notifications |
| `ANDROID_BRIDGE_ENABLED` | `false` | Enable Android bridge |
| `DESKTOP_CONTROL_ENABLED` | `true` | Enable desktop control |

## Version History

- **v0.3 Genesis** — Full control, stability, LLM fallback, command router, desktop .exe
- **v0.2 Genesis** — Brain engine, LLM gateway, memory, tasks, calendar, notifications
- **v0.1 Genesis** — Initial setup, persona, tools framework

## Next Steps

1. Android native app (Notification Listener Service)
2. Google Calendar OAuth integration
3. Automation engine (rules, triggers, schedules)
4. Voice wake word improvements
5. Multi-device sync
