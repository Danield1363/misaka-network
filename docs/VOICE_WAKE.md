# Voice Wake Word (Experimental)

Misaka supports voice activation through the Web Speech API.

## How It Works

1. User enables "Wake Word" in settings
2. Dashboard starts listening via Web Speech API
3. When "Misaka" is detected, visual feedback appears
4. The following speech is captured as a command
5. Command is sent to `/api/chat` for processing
6. Response is spoken if auto-speak is enabled

## Wake Phrases

- "Misaka"
- "Ei Misaka"
- "Ok Misaka"

## States

- `off` — Not listening
- `listening` — Actively listening for wake word
- `wake_detected` — Wake word detected, capturing command
- `command_captured` — Command captured, sending to backend
- `processing` — Processing command
- `speaking` — Speaking response

## Requirements

- Web Speech API supported browser (Chrome, Edge, Safari)
- Microphone permission granted
- HTTPS or localhost

## Privacy

- Only text transcription is sent to backend
- No raw audio is transmitted
- Voice processing happens locally in the browser
- Can be disabled at any time

## Desktop Support

The wake word feature works in the Electron desktop app through Chromium's Web Speech API implementation.

## Limitations

- Experimental feature
- May not work in all environments
- Background noise can affect accuracy
- Requires user interaction to start (browser autoplay policy)
