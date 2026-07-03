# Voice System - Misaka v0.3.7

## Modos

`cloud_voice` e o modo principal. A dashboard captura audio com `navigator.mediaDevices.getUserMedia` + `MediaRecorder`, envia para o backend em `/api/voice/transcribe`, recebe texto e chama o mesmo fluxo do chat com `sendMessage(text, { source: "cloud_voice" })`.

Fallbacks:

- `web_speech_fallback`: usa `SpeechRecognition`/`webkitSpeechRecognition` apenas quando selecionado.
- `native_daemon_fallback`: usa o daemon local Vosk quando disponivel.
- `unavailable`: usado quando nenhum caminho de captura/transcricao esta disponivel.

## Fluxo

1. Usuario ativa escuta.
2. A Misaka pede consentimento e permissao do microfone.
3. O dashboard grava janelas curtas de audio.
4. O backend transcreve com o provider configurado.
5. O dashboard classifica o texto.
6. Comandos seguros chamam `/api/chat`.
7. O `CommandRouter` detecta a acao antes do LLM.
8. O dashboard executa `metadata.client_action`.
9. A Misaka so anuncia sucesso depois do resultado real da bridge.

## Variaveis

```env
VOICE_ENABLED=true
VOICE_PROVIDER=mock
VOICE_MAX_AUDIO_SECONDS=10
VOICE_MAX_AUDIO_BYTES=5000000
VOICE_LANGUAGE=pt
VOICE_MOCK_TRANSCRIPT="abrir youtube"
OPENAI_API_KEY=
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
```

## Providers

`mock`: usado em desenvolvimento e testes. Retorna `VOICE_MOCK_TRANSCRIPT`.

`openai`: preparado para transcricao real. So inicia se `OPENAI_API_KEY` existir no backend. A chave nunca vai para frontend, preload ou bundle desktop.

`unconfigured`: retorno seguro quando provider real nao esta configurado.

## Privacidade

- A escuta fica desligada por padrao.
- O primeiro start mostra aviso de consentimento.
- Audio nao e salvo por padrao.
- Arquivos temporarios do backend sao removidos no `finally`.
- Nenhuma API key e exposta ao dashboard ou Electron.
- Modelos Vosk locais ficam ignorados por Git em `desktop/voice/models/`.

## Comandos De Voz

Modo padrao: `hybrid`.

Aceita:

- `Misaka, abra o YouTube`
- `abrir youtube`
- `abrir canal do alanzoka no youtube`
- `pesquise wake on lan no google`
- `abrir notepad`
- `limpe os alertas`
- `ative o hud`

Comandos perigosos como `desligar computador`, `formatar`, `apagar arquivo`, `comprar` e `pagar` nao executam direto. A camada de voz bloqueia e o backend tambem retorna confirmacao quando recebe esse texto.

## Endpoints

`GET /api/voice/status`

Retorna provider, modo, readiness, formatos aceitos e erro mais recente.

`POST /api/voice/transcribe`

Recebe `multipart/form-data` com campo `audio`, alem de `language`, `source` e `session_id` opcionais.

Formatos aceitos: `webm`, `ogg`, `wav`, `mp3`, `m4a`.
