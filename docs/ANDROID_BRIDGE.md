# Android Bridge

Misaka communicates with Android devices through an action queue system compatible with MacroDroid/Tasker.

## Architecture

```
Misaka Backend (Action Queue) → MacroDroid/Tasker polls → Executes on device → Reports back
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/android/status` | Device connection status |
| POST | `/api/android/actions/enqueue` | Queue a new action |
| GET | `/api/android/actions/pending` | List pending actions |
| POST | `/api/android/actions/{id}/complete` | Mark action completed |
| POST | `/api/android/actions/{id}/fail` | Mark action failed |
| POST | `/api/android/actions/{id}/cancel` | Cancel action |

## Action Types

### SAFE
- `show_toast` — Show toast message
- `vibrate` — Vibrate device
- `open_url` — Open URL in browser
- `open_app` — Open app by package name
- `play_notification_sound` — Play notification sound

### SENSITIVE (disabled by default)
- `send_sms` — Send SMS
- `send_whatsapp` — Send WhatsApp message
- `change_settings` — Change device settings

## Setup with MacroDroid

1. Install MacroDroid on your Android device
2. Create a "HTTP Request" macro that polls `GET /api/android/actions/pending`
3. Parse the response and execute allowed actions
4. Call `POST /api/android/actions/{id}/complete` or `/fail` when done

## Example Action Enqueue

```bash
curl -X POST http://localhost:8000/api/android/actions/enqueue \
  -H "Content-Type: application/json" \
  -d '{"action_type": "vibrate", "payload": {"duration": 500}, "risk_level": "safe"}'
```

## Security

- Actions are classified by risk level
- Sensitive actions require explicit confirmation
- All actions are logged
- WhatsApp/SMS sending disabled by default
