# Desktop App - Misaka Network

## Visao Geral

O app desktop usa Electron para carregar a dashboard da Misaka, expor uma bridge segura para abrir apps/sites locais, gerenciar tray, notificacoes e modo HUD.

## Comandos

```bash
cd desktop
npm install
npm start
npm run debug
npm run dist
```

`npm run dist` gera:

- `desktop/dist/Misaka Network Setup 0.3.7.exe`
- `desktop/dist/Misaka Network 0.3.7.exe`

## Variaveis

- `MISAKA_API_BASE_URL`: API usada pela dashboard. Padrao: `http://127.0.0.1:8000/api`.
- `MISAKA_DASHBOARD_URL`: dashboard remoto/local customizado.
- `START_MINIMIZED`: inicia minimizado.
- `ALWAYS_ON_TOP_DEFAULT`: ativa always on top no start.
- `TRANSPARENT_MODE_DEFAULT`: inicia em modo HUD transparente.

URLs contendo `/docs` ou `/redoc` sao rejeitadas para evitar abrir a documentacao da API no app.

## Logs

O desktop nao depende de stdout/stderr. Logs sao escritos em:

```text
%APPDATA%\misaka-desktop\misaka-desktop.log
```

`EPIPE` em stdout/stderr e ignorado com seguranca e registrado em arquivo quando aplicavel.

## Bridge Segura

`window.misakaDesktop` expoe:

- `openUrl(url)`
- `openApp(appName)`
- `searchWeb(query, provider)`
- `showNotification(title, body)`
- `getSystemStatus()`
- `setHudMode(enabled)`
- `setAlwaysOnTop(enabled)`
- `focusWindow()`
- `onWakeWordSetEnabled(callback)`
- `removeWakeWordSetEnabledListener(callback)`
- `nativeVoice*` para fallback local opcional

Apps permitidos:

- `notepad`
- `explorer`
- `calculator`
- `discord`
- `vscode`
- `chrome`
- `edge`
- `browser`
- `cmd`
- `powershell`

Nao existe shell arbitrario na bridge.

## Tray

Menu:

- Abrir Misaka
- Always on top
- HUD Mode
- Ativar escuta Misaka
- Desativar escuta Misaka
- Sair

Se o renderer ainda estiver carregando, o estado de escuta fica pendente e e enviado apos `did-finish-load`.

## Voz

O modo principal e Cloud Voice. O Electron precisa permitir permissao de `media`/`microphone`; qualquer outra permissao e negada.

Web Speech e daemon nativo sao fallbacks opcionais. O daemon nativo nao e iniciado automaticamente.
