# Dashboard V2 — Misaka v0.3 Genesis

## Overview

The dashboard has been completely overhauled for v0.3 Genesis with working settings, voice controls, alert management, and desktop/Android bridge integration.

## New Features

### Settings Drawer
- Open with gear icon in header
- LLM status display
- Voice configuration
- HUD mode toggle
- Compact mode
- Wake word settings
- Desktop/Android bridge status
- Clear all data option

### Voice System
- **Auto-speak on every response** (fixed from v0.2)
- Voice presets prioritizing pt-BR female voices
- Rate/pitch sliders with localStorage persistence
- Test voice button
- Stop voice button
- Speak suffix toggle ("diz Misaka Misaka")

### Alert Management
- Ack all button
- Refresh button
- Filter buttons (All, Critical, Important, Pending)
- Individual ack button per alert
- Auto-refresh every 10 seconds

### Toast System
- Non-intrusive notifications for actions
- Types: success, error, info, warning
- Auto-dismiss after 4 seconds

### Confirmation Modal
- For sensitive actions
- Approve/Deny buttons
- ESC to close

### HUD Mode
- Transparent overlay mode
- Works in web and desktop
- Persisted in localStorage

### Wake Word (Experimental)
- Web Speech API integration
- "Misaka" wake phrase detection
- Visual feedback when listening
- Privacy: only text sent, no audio

### Status Badges
- Real-time LLM provider/model status
- Fallback indicator
- Desktop bridge status
- Android bridge status
- Memory/Calendar/Tools/Notifications status

## Layout

```
┌─────────────────────────────────────────────┐
│ Header: Logo | Provider Badge | Voice/HUD/Settings │
├───────┬───────────────────────┬─────────────┤
│ Side  │ Chat Messages         │ Alerts      │
│ bar   │                       │ Sidebar     │
│       │ [Messages...]         │ [Filters]   │
│ Voice │                       │ [Alerts]    │
│ Panel │                       │             │
│       │ Chat Input            │             │
│ Modules│ [Text] [Send]       │             │
└───────┴───────────────────────┴─────────────┘
```

## Responsive

- < 1024px: Alerts sidebar hidden
- < 768px: Left sidebar hidden, full-width chat
