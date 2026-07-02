# Settings Sync — Preparation

## Current State

Settings are stored in two places:

1. **Dashboard localStorage** — Client-side, browser only
2. **Backend `/api/settings`** — Server-side, persistent

The dashboard reads from localStorage first, then falls back to backend settings if available. This ensures the dashboard works even if the backend settings endpoint fails.

## Settings Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings` | Get all user settings |
| PUT | `/api/settings` | Update settings (partial) |
| POST | `/api/settings/reset` | Reset to defaults |

## Default Settings

```json
{
  "voice_enabled": true,
  "auto_speak": false,
  "selected_voice": "",
  "voice_rate": 1.0,
  "voice_pitch": 1.1,
  "speak_suffix_enabled": true,
  "hud_enabled": false,
  "compact_mode": false,
  "desktop_notifications_enabled": false,
  "wake_word_enabled": false,
  "theme": "dark",
  "language": "pt-BR"
}
```

## Device Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/devices` | List registered devices |
| POST | `/api/devices/register` | Register a new device |
| POST | `/api/devices/{id}/heartbeat` | Send heartbeat |
| DELETE | `/api/devices/{id}` | Remove device |

## Future: Android App Sync

When the native Android app is built, it will:
1. Register via `POST /api/devices/register`
2. Send heartbeats every 5 minutes
3. Poll `/api/android/actions/pending` for actions
4. Report completion via `POST /api/android/actions/{id}/complete`
5. Sync settings via `/api/settings`
