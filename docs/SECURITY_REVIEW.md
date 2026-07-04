# Security Review - Misaka v0.3.7

## Principios

- Nenhuma API key no frontend, preload ou bundle desktop.
- Sem shell arbitrario.
- Apps locais abertos apenas por registry configurado.
- Power actions desativadas por padrao e protegidas por configuracao explicita.
- Audio nao e salvo por padrao.
- Comandos perigosos fora do conjunto de power actions exigem confirmacao ou sao bloqueados.

## Riscos

| Risco | Nivel | Mitigacao |
| --- | --- | --- |
| Exposicao de API key | Alto | `OPENAI_API_KEY`, `GEMINI_API_KEY` e demais chaves ficam apenas no backend/env |
| Shell injection | Alto | Bridge Electron nao aceita comando shell arbitrario |
| Abertura de app indevido | Medio | `openApp` resolve apenas chaves em `apps.json`/`appAliases.json` |
| Desligamento acidental | Alto | `power_action` fica desativado por padrao e pode exigir confirmacao |
| URL insegura | Medio | `openUrl` aceita apenas `http://` e `https://` |
| Captura de audio sem consentimento | Alto | Escuta desligada por padrao e aviso antes da primeira ativacao |
| Persistencia de audio | Alto | Backend usa arquivo temporario e remove no `finally` |
| Provider real sem configuracao | Medio | Retorna erro seguro, sem stack trace |
| EPIPE/stdout crash | Medio | Logs em arquivo e handlers de stdout/stderr |

## Chaves

| Variavel | Local | Observacao |
| --- | --- | --- |
| `GEMINI_API_KEY` | Backend `.env` | Nunca injetar no dashboard |
| `OPENAI_API_KEY` | Backend `.env` | Usada apenas pelo provider de transcricao |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend `.env` | Nunca commitar |
| `NOTIFICATION_INGEST_TOKEN` | Backend `.env` | Bridge de notificacoes |

## Voice Privacy

- `VOICE_PROVIDER=mock` nao envia audio a terceiros.
- `VOICE_PROVIDER=openai` so funciona com chave no backend.
- O dashboard envia audio ao backend configurado apenas para gerar texto de comando.
- Audio recebido por `/api/voice/transcribe` e validado por tamanho/formato.
- Formatos aceitos: `webm`, `ogg`, `wav`, `mp3`, `m4a`.
- Arquivos vazios, grandes ou com extensao invalida sao rejeitados.

## Electron

- `contextIsolation: true`.
- `nodeIntegration: false`.
- Preload expõe apenas funções whitelisted.
- `ipcRenderer` nao e exposto.
- Permissoes Electron: `media`/`microphone` permitidas; demais negadas.
- Logs ficam em `%APPDATA%\misaka-desktop\misaka-desktop.log`.

## App Registry

- Apps padrao ficam em `desktop/apps.json`.
- Aliases ficam em `desktop/appAliases.json`.
- O Electron cria uma copia editavel no diretorio `userData`.
- A fala nunca vira comando shell.
- O renderer envia apenas `open_app` com uma chave, como `notepad` ou `spotify`.
- O Electron executa a entrada configurada com `spawn(..., { shell: false })`.

Se a chave nao existir no registry, a resposta segura e: `Aplicativo nao configurado. Adicione no desktop/apps.json.`

## Power Actions

- `shutdown`, `restart`, `sleep` e `lock` sao as unicas acoes aceitas.
- `powerActionsEnabled=false` por padrao.
- `powerActionsRequireConfirmation=true` por padrao.
- A configuracao e lida pelo processo principal do Electron.
- Nao existe canal para enviar comandos arbitrarios de energia.

## Nao Commitar

- `.env`
- arquivos de chave
- audio gravado
- `desktop/node_modules/`
- `desktop/dist/`
- `desktop/voice/models/`
