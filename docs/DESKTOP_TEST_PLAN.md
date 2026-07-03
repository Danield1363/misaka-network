# Desktop Test Plan - Misaka Network

## Pre-requisitos

```bash
cd desktop
npm install
```

Backend recomendado:

```bash
cd backend
python -m uvicorn main:app --reload
```

## Start

1. Rodar `npm start`.
2. Verificar que a janela abre com a dashboard.
3. Verificar que nao abre `/docs`.
4. Verificar que o processo nao fecha sozinho apos 10 segundos.
5. Conferir `%APPDATA%\misaka-desktop\misaka-desktop.log`.
6. Esperado: sem `EPIPE`.

## Bridge

No chat:

1. `abrir notepad`
2. `abrir explorer`
3. `abrir calculadora`
4. `abrir discord`
5. `abrir vs code`
6. `abra o youtube`
7. `abra o canal do alanzoka no youtube`

Esperado:

- apps abrem quando instalados;
- falha mostra motivo real;
- URL usa `openUrl`;
- nenhuma resposta diz sucesso antes do retorno `success=true`.

## Tray

1. Abrir menu de tray.
2. Clicar `Abrir Misaka`.
3. Clicar `Ativar escuta Misaka`.
4. Verificar dashboard iniciando a escuta.
5. Clicar `Desativar escuta Misaka`.
6. Verificar dashboard parando a escuta.
7. Alternar `Always on top`.
8. Alternar `HUD Mode`.

## Cloud Voice

1. Selecionar `Cloud Voice`.
2. Selecionar `Hibrido`.
3. Clicar `Ativar escuta`.
4. Permitir microfone.
5. Falar `abrir youtube`.
6. Verificar transcricao, comando detectado, acao e resposta.

## Erros De Voz

1. Negar microfone.
   - Esperado: `Permissao de microfone negada.`
2. Remover provider real.
   - Esperado: `Transcricao de voz nao configurada no backend.`
3. Selecionar Web Speech em ambiente sem suporte.
   - Esperado: erro claro, sem estado falso de escuta.

## Build

1. Rodar `npm run dist`.
2. Esperado:
   - `desktop/dist/Misaka Network Setup 0.3.7.exe`
   - `desktop/dist/Misaka Network 0.3.7.exe`
3. Abrir portable.
4. Instalar pelo setup.
5. Repetir smoke test de dashboard e bridge.
