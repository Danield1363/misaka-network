# Voice Mode — Misaka v0.3

## Features

- **Auto-speak** — Speaks every assistant response when enabled
- **Voice presets** — Pre-configured voice profiles
- **Rate/pitch control** — Adjustable speech speed and tone
- **Speak suffix** — "diz Misaka Misaka." appended to speech
- **Stop button** — Immediately stops current speech
- **Test button** — Tests voice with sample phrase
- **Wake word** — Experimental voice activation

## Voice Presets

| Preset | Description |
|--------|-------------|
| Misaka BR Feminina | pt-BR female voice, pitch 1.15, rate 1.0 |
| Misaka Suave | Softer tone, pitch 1.1, rate 0.9 |
| Misaka Sistema | Clear system voice, pitch 1.0, rate 1.0 |
| Misaka Rápida | Faster speech, pitch 1.0, rate 1.2 |
| Sistema padrão | Browser default voice |

## Configuration

Settings are persisted in localStorage:
- `misaka_voice_enabled` — Voice on/off
- `misaka_auto_speak` — Auto-speak on/off
- `misaka_voice_name` — Selected voice name
- `misaka_voice_rate` — Speech rate (0.5–2.0)
- `misaka_voice_pitch` — Speech pitch (0.5–2.0)
- `misaka_speak_suffix` — Suffix on/off

## Technical Details

- Uses Web Speech API (`SpeechSynthesis`)
- Each response creates a new `SpeechSynthesisUtterance`
- Previous speech is cancelled before new speech starts
- Voice list loaded asynchronously via `onvoiceschanged`
- Desktop Electron supports voice via Chromium's implementation

## Troubleshooting

- **No voice**: Check if browser supports Web Speech API
- **Voice stops after first response**: Fixed in v0.3 — auto-speak now triggers on every response
- **Wrong voice**: Re-select voice in settings panel
- **Voice too fast/slow**: Adjust rate slider
