# Desktop App - Misaka Network

## Overview

App desktop da Misaka usando Electron.

## Funcionalidades

- Dashboard embutida
- System tray
- Notificações nativas
- Always on top
- Modo HUD transparente

## Instalação

```bash
cd desktop
npm install
npm start
```

## Configuração

Variáveis de ambiente:
- `MISAKA_API_BASE_URL` - URL da API
- `MISAKA_DASHBOARD_URL` - URL do dashboard
- `START_MINIMIZED` - Iniciar minimizado
- `ALWAYS_ON_TOP_DEFAULT` - Sempre no topo
- `TRANSPARENT_MODE_DEFAULT` - Modo transparente

## Build

```bash
npm run build
```