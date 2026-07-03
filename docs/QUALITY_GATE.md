# Quality Gate — Misaka v0.3.5

Use this checklist before any merge or release.

**Last verified:** 2026-07-02 (v0.3.5 finalized — desktop bridge, app launching, voice wake, URL fix)

## Syntax Validation

### Comando: `node --check dashboard/app.js`
- Resultado esperado: Sem SyntaxError.
- Resultado obtido: OK
- Status: **PASS**

### Comando: `node --check dashboard/voiceWake.js`
- Resultado esperado: Sem SyntaxError.
- Resultado obtido: OK
- Status: **PASS**

### Comando: `node --check dashboard/voiceWake.test.js`
- Resultado esperado: Sem SyntaxError.
- Resultado obtido: OK
- Status: **PASS**

### Comando: `node --check dashboard/config.js`
- Resultado esperado: Sem SyntaxError.
- Resultado obtido: OK
- Status: **PASS**

### Comando: `node --check desktop/main.js`
- Resultado esperado: Sem SyntaxError.
- Resultado obtido: OK
- Status: **PASS**

### Comando: `node --check desktop/preload.js`
- Resultado esperado: Sem SyntaxError.
- Resultado obtido: OK
- Status: **PASS**

### Comando: `node dashboard/voiceWake.test.js`
- Resultado esperado: wake phrase extraction + two-step flow + start failure.
- Resultado obtido: `voiceWake extraction tests passed`
- Status: **PASS**

### Comando: `python -m pytest`
- Resultado esperado: All tests pass.
- Resultado obtido: **308 passed** in 7.01s
- Status: **PASS**

### Comando: `POST /api/chat` com `"abrir discord"` (backend local)
- Resultado esperado: `agent=command_router`, `client_action.open_app=discord`, resposta curta.
- Resultado obtido: PASS — resposta `"Vou abrir o Discord no seu computador..."`, sem tutorial.
- Status: **PASS**

### Limitação conhecida: API remota (Northflank)
- A URL `https://p01--misaka-network--nf5wq7twf8xg.code.run/api` ainda retorna resposta LLM/mock para `"abrir discord"`.
- Dashboard/Electron agora defaultam para `http://127.0.0.1:8000/api` em modo local/file/Electron.
- Deploy do backend atualizado é necessário para produção remota.

## Syntax Validation (tabela resumida)

| Command | Expected | Status |
|---------|----------|--------|
| `python -m py_compile backend/app/brain/engine.py` | OK | PASS |
| `python -m py_compile backend/app/api/commands.py` | OK | PASS |
| `python -m py_compile backend/app/commands/router.py` | OK | PASS |
| `python -m py_compile backend/app/commands/confirmations.py` | OK | PASS |
| `python -m py_compile` (all backend/app/*.py) | OK | PASS |
| `node --check dashboard/app.js` | OK | PASS |
| `node --check dashboard/voiceWake.js` | OK | PASS |
| `node --check dashboard/voiceWake.test.js` | OK | PASS |
| `node --check dashboard/config.js` | OK | PASS |
| `node --check desktop/main.js` | OK | PASS |
| `node --check desktop/preload.js` | OK | PASS |
| `node --check desktop/control/*.js` | OK | PASS |

## Backend (308 tests)

| Test | Command | Expected | Status |
|------|---------|----------|--------|
| Health endpoint | `test_health` | 200, status=ok | PASS |
| Status endpoint | `test_root_status` | version, provider | PASS |
| Overview endpoint | `test_overview` | full status + alerts | PASS |
| LLM status | `test_llm_status` | provider, models, cooldowns | PASS |
| LLM fallback | `test_llm_fallback` | fallback chain, cooldowns | PASS |
| Chat conversation | `test_chat` | response, agent, metadata | PASS |
| Chat commands | `test_chat_commands` | ui_effect + client_action correct | PASS |
| Command router | `test_command_router` | intent detection, routing | PASS |
| Commands API | `test_commands_api` | route, confirmations | PASS |
| Notifications ack | `test_notifications_ack` | ack-all, summary | PASS |
| Android bridge | `test_android_bridge` | queue lifecycle | PASS |
| Android flag | `test_android_bridge_flag` | ANDROID_BRIDGE_ENABLED | PASS |
| Action approvals | `test_action_approvals` | create, approve, deny | PASS |
| Suffix no duplicate | `test_suffix_no_duplicate` | suffix once | PASS |
| Settings | `test_settings` | get, update, reset | PASS |
| Devices | `test_devices` | register, heartbeat, list | PASS |
| Desktop package | `test_desktop_package` | extraResources includes dashboard | PASS |
| Full suite | `python -m pytest` | 308 passed | PASS |
| Voice wake extraction | `node dashboard/voiceWake.test.js` | wake phrase + two-step command flow | PASS |

## Operational Actions

| Command | Expected client action | Expected result |
|---------|------------------------|-----------------|
| `abrir notepad no meu computador` | `open_app` / `notepad` | Bloco de Notas opens through desktop bridge |
| `abra explorer` | `open_app` / `explorer` | Explorador de Arquivos opens through desktop bridge |
| `abra o youtube` | `open_url` / `https://www.youtube.com` | YouTube opens as a page |
| `abra o canal do alanzoka no youtube` | `open_url` / YouTube search URL | YouTube channel search opens |
| `pesquisar wake on lan no Google` | `search_web` / `google` | Google search opens |
| `pesquisar alanzoka no YouTube` | `search_web` / `youtube` | YouTube search opens |

## Dashboard

| Check | Command | Expected | Status |
|-------|---------|----------|--------|
| Loads without errors | Open browser | No console errors | PASS |
| Shows LLM status | Check sidebar | Provider + model | PASS |
| Chat works | Send message | Response appears | PASS |
| Auto-speak | Enable + send messages | All responses spoken | PASS |
| HUD toggle | Click HUD button | Body class toggles | PASS |
| Settings drawer | Click gear | Opens, ESC closes | PASS |
| Alerts load | Check sidebar | Alert count correct | PASS |
| Ack-all | Click "✓ All" | Alerts cleared | PASS |
| Clear chat | Click "Clear" | Chat resets | PASS |
| Toast system | Perform actions | Toasts appear | PASS |
| Voice controls | Test/Stop buttons | Work correctly | PASS |

## Desktop

| Check | Command | Expected | Status |
|-------|---------|----------|--------|
| npm install | `cd desktop && npm install` | Success | PASS |
| npm start | `npm start` | Window opens | PASS |
| npm run debug | `npm run debug` | Logs visible | PASS |
| App stays open | Click X | Minimizes to tray | PASS |
| Opens dashboard | Check window | Not /docs | PASS |
| Tray works | Right-click tray | Menu appears | PASS |
| Always on top | Toggle | Window stays on top | PASS |
| npm run dist | `npm run dist` | .exe generated | PASS |
| App launcher allowlist | Unknown app | Returns error, not arbitrary open | PASS |

## Security

| Check | Method | Status |
|-------|--------|--------|
| No tokens in frontend | Code review | PASS |
| No tokens hardcoded | .env only | PASS |
| No secrets in desktop bundle | extraResources only | PASS |
| Dangerous actions blocked | permissions.js BLOCKED_ACTIONS | PASS |
| Sensitive actions require confirmation | ConfirmationManager | PASS |
| App launcher uses allowlist | WINDOWS_APP_LAUNCHERS | PASS |
| IPC uses contextIsolation | preload.js contextBridge | PASS |
| Error messages safe | No internals leaked | PASS |

## Voice Wake

| Check | Method | Expected | Status |
|-------|--------|----------|--------|
| Wake controller syntax | `node --check dashboard/voiceWake.js` | OK | PASS |
| Wake phrase extraction | `node dashboard/voiceWake.test.js` | "Misaka, abra..." extracts command | PASS |
| Two-step command flow | `node dashboard/voiceWake.test.js` | "Misaka" then command sends command | PASS |
| Recognition start failure | `node dashboard/voiceWake.test.js` | start failure sets error and does not listen | PASS |
| Missing SpeechRecognition | Code path | Shows unavailable/error state, not listening | PASS |
| Microphone denied | Code path | Shows "Permissão de microfone negada." | PASS |
| Electron media permission | Code review | `session.defaultSession.setPermissionRequestHandler` allows media/microphone | PASS |
| Tray wake controls | Code review | Tray sends wake enable/disable event to renderer | PASS |
| Native wake fallback | `docs/VOICE_WAKE_NATIVE_PLAN.md` | Documents future native mode and limitations | PASS |
| Electron dashboard launch | `cd desktop && npm start` | Electron processes stay running after launch | PASS |
| Real microphone phrase | Manual Chrome/Edge microphone test | Requires human speech and browser permission | MANUAL |
