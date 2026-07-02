# Voice Mode - Misaka Network

## Overview

A Misaka pode falar respostas em voz alta usando SpeechSynthesis do navegador.

## Funcionalidades

- Toggle voice on/off
- Botão "falar última resposta"
- Voz em português (pt-BR)
- Velocidade e pitch configuráveis

## Como usar

1. Clique no ícone 🔊 no header para ativar/desativar voz
2. Clique no botão 🔊 ao lado do chat para falar a última resposta
3. As respostas serão faladas automaticamente quando a voz está ativa

## Configuração

GET /api/voice-config retorna:
```json
{
  "voice_enabled": true,
  "auto_speak": false,
  "speak_suffix_enabled": true,
  "rate": 1.0,
  "pitch": 1.0
}
```

## Preferências

A preferência de voz é salva localmente no navegador.