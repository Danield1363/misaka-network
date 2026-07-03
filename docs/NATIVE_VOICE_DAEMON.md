# Native Voice Daemon — Misaka v0.3.7

## O que e

O Misaka Voice Daemon e um servico local de reconhecimento de voz que:
- roda no PC do usuario;
- escuta o microfone continuamente;
- transcreve voz com Vosk;
- detecta comandos operacionais;
- envia comandos via WebSocket para a dashboard;
- funciona em Chrome, Vivaldi, Electron e qualquer navegador.

## Por que

- Web Speech API nao funciona no Vivaldi.
- Web Speech e instavel no Electron.
- O daemon resolve isso ficando sempre disponivel.

## Arquitetura

```
Microfone → Vosk (transcricao) → Classificador → WebSocket → Dashboard
```

Daemon roda em: `ws://127.0.0.1:8765`

## Como instalar

```bash
cd desktop/voice/python
pip install -r requirements.txt
```

## Como baixar modelo Vosk

Baixe de: https://alphacephei.com/vosk/models

Modelos recomendados:
- `vosk-model-small-pt-0.3` (~40MB) — rapido
- `vosk-model-pt-0.3` (~1.5GB) — melhor qualidade

Coloque em: `desktop/voice/models/pt/`

## Como rodar manualmente

```bash
cd desktop/voice/python
python misaka_voice_daemon.py --port 8765
```

## Como usar no app desktop

1. Abra o Misaka Desktop.
2. Clique em "Ativar escuta Misaka".
3. O app tentara: Web Speech → Daemon → Native Desktop → Erro.
4. Se o daemon estiver rodando, conecta automaticamente.

## Eventos enviados

| Tipo | Descricao |
|------|-----------|
| status | Estado do daemon (listening, error) |
| transcript | Texto transcrito do microfone |
| command | Comando detectado e classificado |
| error | Erro no daemon |

## Seguranca

- WebSocket escuta apenas em 127.0.0.1 (localhost).
- Nenhum audio bruto sai do PC.
- Apenas texto transcrito e enviado.
- Comandos perigosos exigem confirmacao.
