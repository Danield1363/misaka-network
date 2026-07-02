# RFC-0012 — Misaka Full Control, Stability & Final Foundation Pack

**Status:** Implemented  
**Version:** 0.3 Genesis  
**Date:** 2026-07-02  
**Branch:** `feature/rfc-0012-full-control-stability-pack`

---

## Resumo

Transformar a Misaka de uma dashboard bonita em uma assistente pessoal real, com voz, comandos, controle seguro do PC, controle do celular via bridge, fallback de LLM, desktop app empacotado em .exe, HUD funcional, configurações funcionais e comandos entendidos por linguagem natural.

---

## 1. Problemas Corrigidos

### 1.1 Voz Auto-Speak
- **Problema:** Voz só falava na primeira resposta
- **Solução:** `speakText()` agora é chamada em cada resposta quando `autoSpeak` está ativo
- **Arquivo:** `dashboard/app.js`

### 1.2 Botões HUD/Configurações
- **Problema:** Botões não funcionavam
- **Solução:** Event listeners corrigidos, settings drawer implementado
- **Arquivos:** `dashboard/app.js`, `dashboard/index.html`

### 1.3 Desktop App
- **Problema:** App abria /docs, fechava sozinho
- **Solução:** Validação de URL, minimize to tray, dashboard URL priority
- **Arquivo:** `desktop/main.js`

### 1.4 LLM Fallback
- **Problema:** Gemini Pro batia quota sem fallback
- **Solução:** Chain pro → flash → flash-lite com cooldown
- **Arquivos:** `backend/app/llm/providers/gemini.py`, `backend/app/llm/gateway.py`

### 1.5 Comandos
- **Problema:** Misaka não entendia comandos operacionais
- **Solução:** Command Router com detecção de intenção
- **Arquivos:** `backend/app/commands/`

---

## 2. Sistema de Segurança

### Classificação de Risco

| Nível | Ações | Exemplos |
|-------|-------|----------|
| **SAFE** | Executa direto | Abrir app, mudar HUD, limpar chat |
| **SENSITIVE** | Confirmação | Fechar app, enviar mensagem |
| **DANGEROUS** | Confirmação explícita | Shutdown, deletar arquivos |

### Regras
- Dangerous nunca executa sem confirmação
- Shell arbitrário desativado por padrão
- Tudo gera action log
- Tokens nunca expostos no frontend

---

## 3. LLM Fallback

### Chain
```
gemini-2.5-pro → gemini-2.5-flash → gemini-2.5-flash-lite
```

### Detecção de Erros
- 429 (rate limit)
- RESOURCE_EXHAUSTED
- quota exceeded
- daily limit
- invalid API key
- model not found
- network error

### Cooldown
- 60 segundos por modelo após erro de quota
- Não repete tentativas infinitas

### Endpoint
```
GET /api/llm/status
```

---

## 4. Command Router

### Pipeline
1. Normalização da mensagem
2. Detecção de intenção (keyword matching)
3. Se conversa → LLM
4. Se comando → mapear para tool/action
5. Se confirmação necessária → perguntar
6. Se seguro → executar
7. Responder em linguagem natural

### Comandos Implementados

**Alertas:**
- "limpe os alertas atuais" → `notifications.ack_all_alerts`
- "marque os alertas como vistos" → `notifications.ack_all_alerts`
- "mostrar alertas" → `notifications.list_alerts`

**HUD/Interface:**
- "ative o modo HUD" → `ui.set_hud_mode`
- "desative o modo HUD" → `ui.set_hud_mode`
- "abra configurações" → `ui.open_settings`
- "limpe o chat" → `ui.clear_chat`
- "ligue a voz" → `ui.set_voice_enabled`
- "desligue a voz" → `ui.set_voice_enabled`
- "mude para voz feminina" → `ui.set_voice_profile`

**Desktop:**
- "abra o navegador" → `desktop.open_app`
- "abra o Discord" → `desktop.open_app`
- "abra o VS Code" → `desktop.open_app`
- "pesquise por X" → `desktop.search_web`
- "qual o status do meu PC?" → `desktop.get_system_status`

**Celular:**
- "faça meu celular vibrar" → `android.vibrate`
- "abra o YouTube no celular" → `android.open_app`
- "mande um alerta no celular" → `android.show_toast`

**Tarefas:**
- "crie uma tarefa" → `tasks.create`
- "liste minhas tarefas" → `tasks.list`
- "marque tarefa como concluída" → `tasks.complete`

**Memória:**
- "lembre que..." → `memory.create`
- "o que você lembra sobre..." → `memory.search`
- "esqueça isso..." → `memory.delete` (com confirmação)

**Lembretes:**
- "me lembre de..." → `reminders.create`
- "liste lembretes" → `reminders.list`

---

## 5. Tools Novas

### Notificações
- `notifications.list_alerts`
- `notifications.ack_alert`
- `notifications.ack_all_alerts`
- `notifications.clear_resolved_alerts`
- `notifications.summary`

### Interface
- `ui.set_hud_mode`
- `ui.open_settings`
- `ui.clear_chat`
- `ui.set_voice_enabled`
- `ui.set_auto_speak`
- `ui.set_voice_profile`

### Desktop
- `desktop.open_app`
- `desktop.open_url`
- `desktop.search_web`
- `desktop.get_system_status`
- `desktop.set_volume`
- `desktop.show_notification`
- `desktop.focus_misaka`
- `desktop.toggle_always_on_top`
- `desktop.toggle_hud_mode`

### Android
- `android.enqueue_action`
- `android.list_pending_actions`
- `android.cancel_action`
- `android.ping_device`
- `android.show_toast`
- `android.vibrate`
- `android.open_app`
- `android.open_url`

---

## 6. Alertas

### Endpoints
```
POST /api/notifications/alerts/ack-all
GET  /api/notifications/summary
```

### Comportamento
- "limpar alertas" → marca pendentes como vistos
- Não deleta histórico por padrão
- Dashboard atualiza automaticamente

---

## 7. Voz

### Correções
- `speakText()` chamada em cada resposta
- `speechSynthesis.cancel()` antes de nova fala
- Carregamento assíncrono de vozes
- Estado persistido em localStorage
- Botão "Parar voz" funcional
- Aviso se navegador bloquear áudio

### Presets
- Misaka BR Feminina (pitch 1.15, rate 1.0)
- Misaka Suave (pitch 1.08, rate 0.9)
- Misaka Sistema (pitch 1.0, rate 1.05)
- Misaka Rápida (pitch 1.1, rate 1.3)

---

## 8. Desktop App

### Estrutura
```
desktop/
├── main.js
├── preload.js
├── package.json
├── assets/
│   └── icon.ico
└── build/
```

### Funcionalidades
- Dashboard URL priority: env → local → Cloudflare
- Never opens /docs
- System tray com minimize
- Always on top
- HUD transparent mode
- Native notifications
- IPC bridge seguro

### Empacotamento
```bash
npm install
npm start          # Desenvolvimento
npm run debug      # Com logs
npm run pack       # Diretório
npm run dist       # .exe (NSIS + portable)
```

---

## 9. Desktop Control Bridge

### Preload API
```javascript
window.misakaDesktop = {
    isAvailable,
    openApp,
    openUrl,
    showNotification,
    getSystemStatus,
    setAlwaysOnTop,
    setHudMode,
    setVolume,
    requestAction
}
```

### Segurança
- contextIsolation: true
- nodeIntegration: false
- Validação no main process
- Shell arbitrário bloqueado

---

## 10. Android Bridge

### Action Queue
```
POST /api/android/actions/enqueue
GET  /api/android/actions/pending
POST /api/android/actions/{id}/complete
POST /api/android/actions/{id}/fail
GET  /api/android/status
```

### Ações Iniciais
- show_toast, vibrate, open_url, open_app
- play_notification_sound

### MacroDroid
- Polling em `/api/android/actions/pending`
- Executa ações permitidas
- Chama complete/fail

---

## 11. Action Approvals

### Endpoints
```
GET  /api/actions/pending-approvals
POST /api/actions/approvals
POST /api/actions/approvals/{id}/approve
POST /api/actions/approvals/{id}/deny
```

### Dashboard
- Modal de confirmação
- Painel de aprovações pendentes
- Chat: "sim" aprova última ação pendente

---

## 12. UI

### Toast System
- Mensagens de feedback
- Tipos: info, success, error
- Auto-dismiss após 3s

### Settings Drawer
- LLM status
- Cooldowns ativos
- Voz config
- HUD toggle
- Bridge status

### Status Badges
- Provider badge no header
- Module status na sidebar
- Alerts count com botões

---

## 13. API Overview Atualizado

```json
{
  "assistant": "Misaka",
  "version": "0.3 Genesis",
  "status": "online",
  "llm_provider": "gemini",
  "llm_model": "gemini-2.5-flash",
  "llm_primary_model": "gemini-2.5-pro",
  "llm_fallback_active": true,
  "gemini_configured": true,
  "memory_enabled": true,
  "tasks_enabled": true,
  "calendar_enabled": true,
  "notifications_enabled": true,
  "desktop_enabled": true,
  "android_bridge_enabled": true,
  "voice_enabled": true,
  "wake_word_available": true,
  "pending_alerts": 0,
  "critical_alerts": 0,
  "pending_approvals": 0,
  "last_error": null
}
```

---

## 14. Configurações

### Dashboard (localStorage)
- `misaka_voice_enabled`
- `misaka_auto_speak`
- `misaka_voice_name`
- `misaka_voice_rate`
- `misaka_voice_pitch`
- `misaka_hud_mode`
- `misaka_compact_mode`
- `misaka_speak_suffix`
- `misaka_pending_alerts`

### Backend
- `LLM_PROVIDER`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_FALLBACK_MODEL`
- `GEMINI_SECONDARY_FALLBACK_MODEL`
- `MEMORY_ENABLED`
- `NOTIFICATIONS_ENABLED`
- `DESKTOP_CONTROL_ENABLED`
- `ANDROID_BRIDGE_ENABLED`
- `WAKE_WORD_ENABLED`

---

## 15. Testes

### Backend
- `test_llm_fallback` — fallback chain
- `test_quota_error_detection` — error types
- `test_command_router_*` — command detection
- `test_notifications_ack_all` — ack-all endpoint
- `test_android_action_enqueue` — android queue
- `test_action_approval_required` — approvals
- `test_overview` — overview endpoint
- `test_llm_status` — LLM status endpoint

### Dashboard (Manual)
- Chat responde
- Auto speak fala todas as respostas
- Botão testar voz funciona
- Botão parar voz funciona
- HUD liga/desliga
- Configurações abre/fecha
- Limpar alertas funciona
- Clear chat funciona
- Status LLM aparece
- Fallback aparece

### Desktop
- npm install / start / debug / dist
- App abre e não fecha sozinho
- Dashboard aparece
- .exe é gerado
- Notificação desktop funciona
- Tray funciona
- HUD funciona
- Always on top funciona

---

## 16. Critérios de Aceitação

1. Misaka fala em voz alta todas as respostas com auto speak
2. Voz feminina pode ser escolhida
3. Comando "limpe os alertas atuais" funciona
4. Botão HUD funciona
5. Botão configurações funciona
6. Desktop abre dashboard, não /docs
7. Desktop não fecha sozinho
8. .exe pode ser gerado
9. LLM fallback funciona
10. Dashboard mostra fallback quando Pro bater quota
11. Misaka entende comandos básicos
12. Misaka controla PC com segurança
13. Misaka cria ações para celular via bridge
14. Wake word funcional quando ativado
15. Nada expõe tokens
16. Ações sensíveis pedem confirmação
17. Testes passam

---

## 17. Arquivos Criados/Modificados

### Backend
- `backend/app/llm/providers/gemini.py` — fallback chain + cooldown
- `backend/app/llm/gateway.py` — fallback orchestration + status
- `backend/app/commands/` — router, intents, parser, confirmations, schemas
- `backend/app/tools/notifications/tools.py` — 5 tools
- `backend/app/tools/ui/tools.py` — 6 tools
- `backend/app/tools/desktop/tools.py` — 9 tools
- `backend/app/tools/android/tools.py` — 8 tools
- `backend/app/tools/registry.py` — all tools registered
- `backend/app/api/llm_status.py` — new endpoint
- `backend/app/api/commands.py` — command routing endpoint
- `backend/app/api/android.py` — android action queue
- `backend/app/api/action_approvals.py` — approval system
- `backend/app/api/notifications.py` — ack-all + summary
- `backend/app/api/overview.py` — updated with LLM status
- `backend/app/api/router.py` — new routers included
- `backend/app/brain/engine.py` — command router integration
- `backend/sql/005_action_approvals_android_schema.sql` — new tables

### Dashboard
- `dashboard/app.js` — voice fix, HUD, settings, toasts, approvals
- `dashboard/index.html` — settings drawer, approval modal, toasts
- `dashboard/style.css` — new UI components

### Desktop
- `desktop/main.js` — full IPC bridge, controls
- `desktop/preload.js` — expanded API
- `desktop/package.json` — electron-builder config

### Docs
- `docs/rfc/RFC-0012-Misaka-Full-Control-Stability-Pack.md`
- `docs/LLM_FALLBACK.md`
- `docs/VOICE_WAKE.md`
- `docs/ACTION_APPROVALS.md`
- `docs/SECURITY.md`
- `docs/ANDROID_APP_PLAN.md`
