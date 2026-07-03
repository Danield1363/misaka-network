# Desktop Voice Setup — Misaka v0.3.6

## Pré-requisitos

- Python 3.8+
- pip
- Microfone conectado

## Passo 1: Instalar dependências Python

```bash
cd desktop/voice/python
pip install -r requirements.txt
```

## Passo 2: Baixar modelo Vosk

Baixe um modelo Vosk pt-BR de:
https://alphacephei.com/vosk/models

Modelos recomendados:
- `vosk-model-small-pt-0.3` (~40MB) — rápido, menor qualidade
- `vosk-model-pt-0.3` (~1.5GB) — melhor qualidade

## Passo 3: Colocar modelo

Extraia o modelo para:
```
desktop/voice/models/pt/
```

A estrutura deve ser:
```
desktop/voice/models/pt/
├── am/
├── conf/
├── graph/
└── ...
```

## Passo 4: Testar serviço manualmente

```bash
cd desktop/voice/python
python misaka_voice_service.py
```

Se funcionar, verá:
```json
{"type":"status","state":"listening_for_wake","message":"Ouvindo por Misaka"}
```

Fale "Misaka" no microfone. Se detectar, verá:
```json
{"type":"transcript","text":"misaka"}
```

## Passo 5: Usar no app desktop

1. Abra o app Misaka Desktop.
2. Clique em "Ativar escuta Misaka".
3. O app tentará usar Web Speech primeiro.
4. Se Web Speech não funcionar, usará o modo nativo.
5. Fale "Misaka, abra o YouTube" ou outro comando.

## Solução de problemas

### Python não encontrado
- Verifique se Python está no PATH: `python --version`

### Modelo não encontrado
- Verifique se o modelo está em `desktop/voice/models/pt/`
- O serviço procura por padrão nesse local

### Microfone não funciona
- Verifique se o microfone está conectado
- Teste com outro app (Gravador de Som)

### Erro "sounddevice"
- No Windows, pode ser necessário instalar PortAudio
- `pip install sounddevice` geralmente resolve
