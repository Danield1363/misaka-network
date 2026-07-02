# Dashboard V2 - Misaka Experience Pack

## Overview

A Dashboard V2 é o redesign completo da interface da Misaka, com visual estilo HUD futurista.

## Funcionalidades

- Core Visualizer animado (anéis concêntricos + núcleo pulsante)
- Chat com mensagens estilo sistema
- Central de notificações melhorada
- Modo HUD transparente
- Voz da Misaka (SpeechSynthesis)
- Polling automático de alertas
- Notificações do navegador

## Visual

### Paleta
- Background: #081018
- Primary: #68d5ff
- Secondary: #7a7dff
- Accent: #b38cff

### Core Visualizer
- 3 anéis concêntricos rotativos
- Núcleo central pulsante
- Estados: idle, thinking, speaking

## Deploy

Continua compatível com Cloudflare Pages.

## Configuração

Edite `config.js` para alterar:
- `API_BASE_URL`
- `POLL_INTERVAL_MS`
- `ENABLE_VOICE`
- `ENABLE_HUD_MODE`