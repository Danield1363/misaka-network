# Android App Plan (Future)

This document outlines the future native Android app for Misaka.

## Current Status

For now, Misaka uses **MacroDroid/Tasker** as a bridge to communicate with Android devices. The action queue system at `/api/android/*` provides a polling-based interface.

## Future Architecture

### App Components

1. **Notification Listener Service** — Captures notifications from all apps
2. **Foreground Service** — Keeps the bridge alive in background
3. **Action Executor** — Receives and executes actions from Misaka
4. **Voice Activation** — Local wake word detection
5. **Bridge Client** — Secure communication with Misaka backend

### Permissions Required

- `BIND_NOTIFICATION_LISTENER_SERVICE` — Read notifications
- `FOREGROUND_SERVICE` — Keep service alive
- `VIBRATE` — Vibrate device
- `INTERNET` — Communication with backend
- `SYSTEM_ALERT_WINDOW` — Overlay for HUD mode
- `RECEIVE_BOOT_COMPLETED` — Auto-start on boot

### Communication

- Token-based authentication
- WebSocket for real-time commands
- HTTPS for action queue polling
- Local encryption for sensitive data

### Security

- All communication encrypted
- Token rotation
- Action approval for sensitive operations
- No raw notification content sent without user consent
- Local-only voice processing

## Migration from MacroDroid

The native app will replace MacroDroid by:

1. Using Notification Listener Service instead of notification capture
2. Direct WebSocket connection instead of HTTP polling
3. Local action execution without third-party apps
4. Better battery optimization
5. Real-time status updates

## Timeline

- Phase 1: Notification capture + basic bridge (replace MacroDroid)
- Phase 2: Action execution + voice activation
- Phase 3: HUD mode + advanced controls
- Phase 4: Full assistant integration
