# Quality Gate - Misaka v0.3.7

**Fase:** RFC-0012.10 - Misaka Final Desktop Stability, Cloud Voice & Command System  
**Verificado em:** 2026-07-03  
**Branch:** `feature/rfc-0012-10-final-desktop-cloud-voice`

## Sintaxe

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `node --check dashboard/app.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/config.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.test.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/main.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/preload.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/voice/nativeVoiceBridge.js` | Sem SyntaxError | Sem erro | PASS |

## Testes Automatizados

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `node dashboard/voiceWake.test.js` | Normalizacao, wake phrase, direct command, risco, mock transcription e debounce | `all voiceWake tests passed` | PASS |
| `pytest` | Suite Python executa | Falhou por shim local quebrado: Hermes aponta para Python 3.11 inexistente | FAIL (ambiente) |
| `python -m pytest` | Suite Python executa | `324 passed, 1 warning in 9.68s` | PASS |
| Warning do pytest | Sem impacto funcional | `.pytest_cache` sem permissao de escrita | WARN |

## Desktop Runtime

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `cd desktop && npm install` | Dependencias instaladas | `changed 1 package in 3s` | PASS |
| `cd desktop && npm start` | Electron abre e nao fecha sozinho | 4 processos Electron vivos apos 12s; processo npm ainda ativo | PASS |
| Log do desktop | Sem EPIPE no start | `misaka-desktop.log` recebeu preload path, sem EPIPE no trecho verificado | PASS |
| Dashboard abre | Janela Electron carrega dashboard local | `npm start` criou processos Electron; sem erro no log | PASS |
| App nao abre `/docs` | URL do dashboard valida | `getDashboardUrl()` bloqueia `/docs`/`/redoc`; teste runtime nao mostrou erro | PASS |
| Tray wake enable/disable | Evento enviado ao renderer apos load | Implementado com fila `pendingWakeWordEnabled`; teste manual de clique no tray nao executado | PARTIAL |
| `cd desktop && npm run dist` | NSIS + portable gerados | `Misaka Network Setup 0.3.7.exe` e `Misaka Network 0.3.7.exe` criados em `desktop/dist` | PASS |

## Backend Voice

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `GET /api/voice/status` | Provider mock pronto | Coberto por `test_voice_status_mock` | PASS |
| `POST /api/voice/transcribe` mock | Retorna `VOICE_MOCK_TRANSCRIPT` | Coberto por `test_voice_transcribe_mock` | PASS |
| Sem arquivo | Erro seguro | `audio_missing`, `Nenhum audio recebido.` | PASS |
| Provider OpenAI sem chave | Erro seguro | `voice_provider_not_configured` | PASS |
| Provider real OpenAI | Transcricao real | Nao executado: `OPENAI_API_KEY` ausente no ambiente | NOT RUN |

## Comandos Operacionais

| Comando | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `abrir notepad` | `client_action.open_app=notepad` | Coberto por `test_chat_desktop_apps_do_not_fall_to_llm` | PASS |
| `abrir explorer` | `client_action.open_app=explorer` | Coberto por teste | PASS |
| `abrir calculadora` | `client_action.open_app=calculator` | Coberto por teste | PASS |
| `abrir discord` | `client_action.open_app=discord` | Coberto por teste | PASS |
| `abrir vscode` | `client_action.open_app=vscode` | Coberto por teste | PASS |
| `Misaka, abra o YouTube` | `client_action.open_url=https://www.youtube.com` | Coberto por teste | PASS |
| `abrir video do alanzoka de minecraft` | URL de busca YouTube codificada | Coberto por teste | PASS |
| `pesquise wake on lan no google` | Search Google | Coberto por teste | PASS |
| `pesquise misaka network no github` | Search GitHub | Coberto por teste | PASS |
| `pesquise cobblemon no modrinth` | Search Modrinth | Coberto por teste | PASS |
| `procure atm 10 no curseforge` | Search CurseForge | Coberto por teste | PASS |
| `desligar computador` | `client_action.power_action=shutdown` | Coberto por teste; execucao desktop desativada por padrao | PASS |

## Dashboard Voice

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| Cloud Voice como modo principal | `voice_input_mode=cloud_voice` default | Implementado em `VoiceWakeController` e UI | PASS |
| Web Speech fallback | Opcional, nao principal | Implementado como `web_speech_fallback` | PASS |
| Native daemon fallback | Opcional | Mantido via `nativeVoice*` bridge | PASS |
| MediaRecorder indisponivel | Erro claro | Mensagem: `MediaRecorder nao disponivel neste ambiente.` | PASS |
| Microfone negado | Erro claro e sem estado falso | Simulado no teste JS; `enabled=false`, `active=false` | PASS |
| Fala real no Chrome/Edge | Capturar audio real e executar comando | Nao executado: requer permissao/microfone humano | NOT RUN |
| Fala real no Electron | Capturar audio real e executar comando | Nao executado: requer permissao/microfone humano | NOT RUN |
| Vivaldi | Cloud Voice sem Web Speech | Nao executado manualmente | NOT RUN |

## Desktop Bridge

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `openApp` allowlist | Sem shell arbitrario | Allowlist mantida para notepad/explorer/calculator/discord/vscode/chrome/edge/browser/cmd/powershell | PASS |
| `openUrl` seguro | Apenas http/https | Validacao em main e fallback do dashboard | PASS |
| Popup falso | Nao reportar erro quando fallback dispara | `openUrlAction()` usa Electron primeiro e anchor fallback no navegador | PASS |
| Abrir apps reais via UI | Notepad/Explorer/Calculadora/etc. | Nao executado interativamente nesta rodada | NOT RUN |
| Abrir URL real via UI | YouTube/canal Alanzoka | Nao executado interativamente nesta rodada | NOT RUN |

## Resultado

Automatizado e empacotamento: PASS.  
Testes manuais com microfone, Vivaldi e clique/fala na UI: NOT RUN nesta rodada, documentados sem marcar PASS.

## Hotfix Cloud Voice Recording Loop - 2026-07-03

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `node --check dashboard/app.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.test.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/main.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/preload.js` | Sem SyntaxError | Sem erro | PASS |
| `node dashboard/voiceWake.test.js` | Recorder para chunk, envia mock transcription, detecta comando e nao fica em `recording` | `all voiceWake tests passed` | PASS |
| `pytest` | Suite Python executa | Falhou por shim local quebrado do Hermes/Python 3.11 | FAIL (ambiente) |
| `python -m pytest` | Suite Python executa | `325 passed, 1 warning in 15.91s` | PASS |
| Cloud Voice mock manual | Ativar escuta abre YouTube via microfone real | Nao executado nesta rodada | NOT RUN |

## Hotfix Cloud Voice Duplicate Command Loop - 2026-07-03

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `node --check dashboard/app.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.test.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/main.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/preload.js` | Sem SyntaxError | Sem erro | PASS |
| `node dashboard/voiceWake.test.js` | Mesmo transcript mock nao executa em loop; cooldown bloqueia duplicados; segundo loop nao inicia | `all voiceWake tests passed` | PASS |
| `pytest` | Suite Python executa | Falhou por shim local quebrado do Hermes/Python 3.11 | FAIL (ambiente) |
| `python -m pytest` | Suite Python executa | `325 passed, 1 warning in 8.91s` | PASS |
| Cloud Voice mock manual | `VOICE_PROVIDER=mock` e `VOICE_MOCK_TRANSCRIPT=abrir youtube` abre YouTube uma vez e ignora repeticoes | Nao executado nesta rodada; coberto por teste JS automatizado | NOT RUN |
| Desativar/reativar escuta manual | Loop para e volta sem duplicar gravacao | Nao executado nesta rodada; cobertura parcial em `voiceWake.test.js` | PARTIAL |
| Comandos digitados | `abrir youtube`, `abrir notepad`, `abra explorer`, `abra calculadora` continuam funcionando | Cobertos pela suite Python de comandos/chat | PASS |

## Hotfix Cloud Voice/Desktop Action Stabilization - 2026-07-03

| Teste | Resultado esperado | Resultado obtido | Status |
| --- | --- | --- | --- |
| `node --check dashboard/app.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check dashboard/voiceWake.test.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/main.js` | Sem SyntaxError | Sem erro | PASS |
| `node --check desktop/preload.js` | Sem SyntaxError | Sem erro | PASS |
| `node dashboard/voiceWake.test.js` | Cooldown, await de comando, stop forte e power command delegado | `all voiceWake tests passed` | PASS |
| `pytest` | Suite Python executa | Falhou por shim local quebrado do Hermes/Python 3.11 | FAIL (ambiente) |
| `python -m pytest` | Suite Python executa | `334 passed, 1 warning in 9.65s` | PASS |
| `python -m pytest backend/tests/test_voice_api.py backend/tests/test_chat_commands.py backend/tests/test_desktop_resolver.py` | Mock one-shot, comandos desktop/web/power e resolver | `66 passed, 1 warning in 4.92s` | PASS |
| `cd desktop && npm start` | Electron abre e nao fecha sozinho | Processo npm vivo apos 12s; 4 novos processos Electron; processos do teste encerrados | PASS |
| Cloud Voice mock `VOICE_MOCK_REPEAT=false` | `abrir youtube` nao repete infinitamente por session_id | Coberto por `test_voice_transcribe_mock_one_shot_by_session` e `voiceWake.test.js` | PASS |
| App desconhecido | `abrir spotify` retorna `open_app: spotify`; desktop mostra erro claro se nao configurado | Coberto por backend; execucao real nao testada | PARTIAL |
| Apps configurados | Sem confirmacao e sem shell arbitrario | Implementado via `apps.json`/`appAliases.json` e `spawn(..., shell=false)` | PASS |
| Power actions | Existem como `power_action` e ficam desativadas por padrao | Coberto por backend e configuracao desktop; execucao real nao testada por seguranca | PASS |
| Comandos manuais reais no Electron | notepad/explorer/calculadora/discord/vscode/youtube/canal Alanzoka | Nao executado interativamente nesta rodada | NOT RUN |
