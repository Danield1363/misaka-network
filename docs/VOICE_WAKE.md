# Voice Wake

Desde a v0.3.7, a ativacao por voz da Misaka usa Cloud Voice como caminho principal.

Resumo:

- principal: `cloud_voice`
- fallback opcional: `web_speech_fallback`
- fallback opcional: `native_daemon_fallback`
- modo de comando padrao: `hybrid`

O usuario pode falar com palavra-chave:

```text
Misaka, abra o YouTube
```

Ou comando direto seguro:

```text
abrir youtube
```

Detalhes completos ficam em [VOICE_SYSTEM.md](VOICE_SYSTEM.md).
