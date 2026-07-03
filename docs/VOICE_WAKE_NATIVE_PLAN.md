# Voice Wake Native Plan — Misaka v0.3.6+

## Status atual

- **v0.3.5**: Web Speech + diagnóstico
- **v0.3.6**: Hybrid Voice Wake (Web Speech + Native Desktop Fallback)

## Implementado

### v0.3.6 — Hybrid Voice Wake
- Modo Web Speech para Chrome/Edge
- Modo Native Desktop com Python + Vosk
- Escolha automática de modo
- Bridge IPC entre Electron e Python
- Serviço Python com wake phrase detection
- UI com status do modo atual

## Próximos passos

### Porcupine (wake word dedicado)
- Picovoice Porcupine para detecção eficiente de "Misaka"
- Baixo uso de CPU/memória
- Funciona offline
- Precisa de licença (free tier disponível)

### Whisper local
- OpenAI Whisper para transcrição de alta qualidade
- Mais pesado que Vosk
- Melhor para comandos complexos
- Pode rodar localmente ou via API

### ElevenLabs (TTS premium)
- Voz TTS de alta qualidade
- Mais natural que SpeechSynthesis nativo
- Requer API key
- Pode ser opcional

### Android Voice Wake
- Reconhecimento nativo Android
- Sem necessidade de Python
- Usar SpeechRecognizer nativo
- Integrar com o app Android futuro

## Arquitetura futura

```
Usuário fala "Misaka"
    ↓
Porcupine detecta wake word (baixo custo)
    ↓
Whisper transcreve comando (alta qualidade)
    ↓
Comando enviado para pipeline do chat
    ↓
Misaka responde com ElevenLabs TTS
```

## Prioridades

1. **Porcupine** — wake word mais eficiente
2. **Whisper** — transcrição melhor
3. **ElevenLabs** — voz mais natural
4. **Android** — suporte nativo mobile
