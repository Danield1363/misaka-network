# Manual Test Plan - Misaka v0.3.7

## Pre-requisitos

1. Backend rodando em `http://127.0.0.1:8000`.
2. `VOICE_ENABLED=true`.
3. Para mock: `VOICE_PROVIDER=mock` e `VOICE_MOCK_TRANSCRIPT="abrir youtube"`.
4. Para provider real: `VOICE_PROVIDER=openai`, `OPENAI_API_KEY` e `OPENAI_TRANSCRIPTION_MODEL`.
5. Desktop iniciado com `cd desktop && npm start`.

## Chat E Comandos

1. Digitar `abrir notepad`.
   - Esperado: Notepad abre, resposta curta de sucesso.
2. Digitar `abrir explorer`.
   - Esperado: Explorador de Arquivos abre.
3. Digitar `abrir calculadora`.
   - Esperado: Calculadora abre.
4. Digitar `abrir discord`.
   - Esperado: Discord abre ou erro real da bridge.
5. Digitar `abrir vs code`.
   - Esperado: VS Code abre ou erro real da bridge.
6. Digitar `abra o youtube`.
   - Esperado: YouTube abre sem erro falso de popup.
7. Digitar `abra o canal do alanzoka no youtube`.
   - Esperado: busca correta no YouTube.
8. Digitar `desligar computador`.
   - Esperado: confirmacao exigida, nada executado.

## Cloud Voice No Electron

1. Selecionar `Cloud Voice`.
2. Selecionar modo `Hibrido`.
3. Clicar `Ativar escuta`.
4. Aceitar aviso de captura.
5. Permitir microfone.
6. Falar `abrir youtube`.
7. Verificar:
   - status passa por gravando/transcrevendo/processando;
   - ultimo ouvido mostra texto transcrito;
   - comando detectado aparece;
   - `/api/chat` recebe o texto;
   - client_action abre a pagina;
   - resposta so anuncia sucesso apos retorno da acao.

## Cloud Voice Mock

1. Configurar `VOICE_PROVIDER=mock`.
2. Configurar `VOICE_MOCK_TRANSCRIPT="abrir youtube"`.
3. Ativar escuta.
4. Gravar qualquer audio curto.
5. Esperado: a transcricao mock vira `abrir youtube` e abre YouTube.

## Provider Nao Configurado

1. Configurar `VOICE_PROVIDER=openai` sem `OPENAI_API_KEY`.
2. Ativar escuta.
3. Esperado: erro claro `Transcricao de voz nao configurada no backend.`
4. Verificar que o botao nao fica em estado falso de escuta.

## Microfone Negado

1. Bloquear permissao de microfone.
2. Clicar `Ativar escuta`.
3. Esperado: `Permissao de microfone negada.`
4. Verificar que `enabled=false`, sem loop de toast.

## Vivaldi

1. Abrir dashboard no Vivaldi.
2. Selecionar `Cloud Voice`.
3. Permitir microfone.
4. Falar `abrir youtube`.
5. Esperado: funciona sem `SpeechRecognition`.

## Web Speech Fallback

1. Selecionar `Web Speech fallback`.
2. Usar Chrome/Edge.
3. Falar `Misaka, abra o YouTube`.
4. Esperado: se o navegador suportar, comando executa; se nao suportar, erro claro.

## Tray

1. Abrir menu da bandeja.
2. Clicar `Ativar escuta Misaka`.
3. Esperado: dashboard recebe evento e tenta iniciar a escuta.
4. Clicar `Desativar escuta Misaka`.
5. Esperado: escuta para.

## Build

1. Rodar `cd desktop && npm run dist`.
2. Abrir `desktop/dist/Misaka Network 0.3.7.exe`.
3. Instalar via `Misaka Network Setup 0.3.7.exe`.
4. Verificar dashboard, bridge e logs.
