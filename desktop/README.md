# Misaka Desktop App

App desktop da Misaka Network usando Electron.

## Instalação

```bash
cd desktop
npm install
```

## Execução

```bash
npm start
```

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `MISAKA_API_BASE_URL` | URL da API Misaka Core | `https://p01--misaka-network--*.code.run/api` |
| `MISAKA_DASHBOARD_URL` | URL do dashboard | (vazio = usar local) |
| `START_MINIMIZED` | Iniciar minimizado | `false` |
| `ALWAYS_ON_TOP_DEFAULT` | Sempre no topo | `false` |
| `TRANSPARENT_MODE_DEFAULT` | Modo transparente | `false` |

### Dashboard

O app desktop pode carregar a dashboard de duas formas:

1. **Local (padrão):** Carrega os arquivos de `../dashboard/`
2. **Remota:** Configure `MISAKA_DASHBOARD_URL` para uma URL remota

**IMPORTANTE:** Não configure `MISAKA_DASHBOARD_URL` com `/docs` ou `/redoc`. O app detectará e mostrará erro.

### Exemplos

**Dashboard local (padrão):**
```bash
npm start
```

**Dashboard remota:**
```bash
MISAKA_DASHBOARD_URL=https://misaka-dashboard.pages.dev npm start
```

**Com API customizada:**
```bash
MISAKA_API_BASE_URL=http://localhost:8000/api npm start
```

## Funcionalidades

- Dashboard visual com HUD
- System tray
- Notificações nativas do sistema
- Always on top
- Modo transparente/HUD
- Alert polling
- Deduplicação de notificações

## Funcionamento

1. O app tenta carregar `MISAKA_DASHBOARD_URL`
2. Se não configurado, carrega `../dashboard/index.html` (local)
3. Se não encontrar local, usa `https://misaka-dashboard.pages.dev`
4. A API base é injetada na dashboard via JavaScript

## Solução de Problemas

### App abre /docs em vez da dashboard

Configure `MISAKA_DASHBOARD_URL` corretamente:
```bash
MISAKA_DASHBOARD_URL=http://localhost:8000 npm start
```

### Dashboard não carrega

1. Verifique se o backend está rodando
2. Verifique se `MISAKA_API_BASE_URL` está correto
3. Verifique o console do Electron (F12)

### Notificações não funcionam

1. Verifique se o desktop app tem permissão de notificação
2. Verifique se `NOTIFICATIONS_ENABLED=true` no backend