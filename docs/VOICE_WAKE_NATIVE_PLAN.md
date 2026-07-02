# Voice Wake Native Plan

O wake word atual tenta usar a Web Speech API no renderer:

- `window.SpeechRecognition`
- `window.webkitSpeechRecognition`

Se essas APIs não existirem no Electron, a dashboard deve mostrar:

> Reconhecimento de voz não disponível neste Electron. Use Chrome/Edge por enquanto ou ative o futuro modo nativo de voz.

Ela não deve fingir que está ouvindo.

## Opções Futuras

| Opção | Uso | Observações |
|-------|-----|-------------|
| Vosk local | Reconhecimento offline | Bom para comandos curtos em PT-BR se houver modelo local. |
| Whisper local | Transcrição robusta | Mais pesado; ideal como serviço local com fila de áudio. |
| Porcupine wake word | Detecção de palavra de ativação | Bom para detectar "Misaka" antes de transcrever o comando. |
| Serviço Python local | Bridge de microfone + STT | Pode combinar Porcupine/Vosk/Whisper e expor HTTP/WebSocket local. |
| Serviço Node local | Integração direta com Electron | Útil para controlar ciclo de vida junto ao app desktop. |

## Arquitetura Recomendada

1. Electron inicializa um serviço local de voz.
2. O serviço captura microfone com permissão explícita.
3. O detector local aguarda "Misaka".
4. Ao detectar, transcreve o comando por alguns segundos.
5. O renderer recebe `{ source: "voice", command }`.
6. A dashboard chama o mesmo pipeline do chat: `sendMessage(command, { source: "voice" })`.
7. `metadata.client_action` continua sendo executado pelo desktop bridge.

## Estado da UI

Enquanto o modo nativo não existir, a UI deve informar:

> Modo nativo de wake word ainda não configurado.

O modo Web Speech pode continuar funcionando em Chrome/Edge e em versões do Electron que exponham `SpeechRecognition`.
