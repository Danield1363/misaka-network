# Misaka Desktop

Electron shell for Misaka Network.

## Run

```bash
npm install
npm start
```

## Build

```bash
npm run dist
```

Outputs are written to `desktop/dist`.

## Logs

Runtime logs are written to:

```text
%APPDATA%\misaka-desktop\misaka-desktop.log
```

The app does not depend on stdout/stderr, so `EPIPE` does not crash the desktop process.

## Voice

Cloud Voice is the main mode. The dashboard captures microphone audio with `getUserMedia`/`MediaRecorder`, sends it to `/api/voice/transcribe`, and then sends the transcribed command through `/api/chat`.

Web Speech and the native daemon are fallbacks only.

## Bridge

The preload exposes `window.misakaDesktop` with safe helpers for URL opening, app opening, notifications, HUD, always-on-top, focus, wake toggle events and optional native voice controls.

No arbitrary shell execution is exposed.
