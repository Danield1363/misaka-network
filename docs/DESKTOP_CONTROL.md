# Desktop Control Bridge

Misaka can control your PC safely through the Electron IPC bridge.

## Architecture

```
Dashboard (Renderer) → preload.js (Context Bridge) → main.js (Main Process) → OS
```

## Available Commands

### SAFE (execute directly)
- `open_app` — Open browser, Discord, VS Code, Explorer, etc.
- `open_url` — Open any URL in default browser
- `get_system_status` — Get platform, memory, CPU info
- `show_notification` — Show native desktop notification
- `focus_misaka` — Bring Misaka window to front
- `toggle_always_on_top` — Toggle always-on-top
- `set_hud_mode` — Toggle HUD overlay

### SENSITIVE (require confirmation)
- `set_volume` — Adjust system volume
- `close_app` — Close an application
- `open_terminal` — Open terminal

### DANGEROUS (blocked by default)
- `shutdown` — Shutdown PC
- `restart` — Restart PC
- `delete_files` — Delete files
- `shell_arbitrary` — Run arbitrary commands

## IPC Bridge (preload.js)

```javascript
window.misakaDesktop = {
    isAvailable: true,
    getConfig(),
    sendNotification(title, body),
    openApp(appName),
    openUrl(url),
    getSystemStatus(),
    setAlwaysOnTop(enabled),
    setHudMode(enabled),
    focusWindow(),
    toggleCompact(enabled),
    requestAction(action),
}
```

## Security Rules

1. `contextIsolation: true` — No direct Node access in renderer
2. `nodeIntegration: false` — Renderer can't access Node APIs
3. All commands validated in main process
4. Shell arbitrary blocked by default
5. Action logs generated for all operations

## Configuration

```bash
MISAKA_API_BASE_URL=https://.../api
MISAKA_DASHBOARD_URL=http://localhost:3000
ALWAYS_ON_TOP_DEFAULT=true
TRANSPARENT_MODE_DEFAULT=false
START_MINIMIZED=false
```
