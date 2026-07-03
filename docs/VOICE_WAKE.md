# Voice Wake — Misaka v0.3.7

## Modos de voz (engine)

A Misaka suporta três engines de reconhecimento de voz:

### 1. Web Speech Mode
- Usado no Chrome/Edge quando `SpeechRecognition` existe.
- Funciona no navegador e pode funcionar no Electron (não confiável).
- Configuração: `pt-BR`, `continuous`, `interimResults`.

### 2. Native Desktop Mode
- Serviço Python local com Vosk.
- Funciona no Electron quando Web Speech não está disponível.
- Requer: Python 3, Vosk, modelo pt-BR em `desktop/voice/models/pt`.

### 3. Unavailable
- Nenhum modo disponível.
- Mostra erro claro.

## Modos de comando

A Misaka suporta três modos de comando:

### 1. Wake Word (Apenas "Misaka")
- Exige dizer "Misaka" antes do comando.
- Exemplo: "Misaka, abra o YouTube"

### 2. Direct Command (Comandos diretos)
- Não exige "Misaka".
- Executa comandos claros que começam com verbos de ação.
- Exemplo: "abrir YouTube", "abra o discord"

### 3. Hybrid (Híbrido) — Padrão
- Aceita tanto wake word quanto comando direto.
- "Misaka, abra o YouTube" funciona.
- "abrir YouTube" também funciona.

## Comandos diretos suportados

Verbos de ação que ativam execução direta:

**Abrir:** abrir, abra, abre, iniciar, inicia, executar, execute, rodar, roda, rode
**Pesquisar:** pesquisar, pesquise, procurar, procure, buscar, busque
**Interface:** ative, ativar, desative, desativar, limpe, limpar, mostrar, mostre

Exemplos:
- "abrir youtube" → abre YouTube
- "abra o discord" → abre Discord
- "pesquise wake on lan no google" → pesquisa no Google
- "limpe os alertas" → limpa alertas
- "ative o hud" → ativa HUD

## Comandos perigosos (exigem confirmação)

Estes NÃO são executados direto:
- desligar/reiniciar computador
- apagar/deletar arquivo
- formatar
- executar comando arbitrário

## Configuração

Seletor na UI: "Modo de escuta"
- Padrão: Hibrido
- Salvo em `localStorage` como `voice_command_mode`

## Fluxo de processamento

```
Transcrição recebida
    ↓
Contém wake phrase "Misaka"?
    Sim → extrair comando → executar
    Não ↓
Modo permite comandos diretos?
    Sim → classifyVoiceCommand()
         matched + safe → executar
         matched + dangerous → executar com confirmação
         not matched → ignorar
    Não → ignorar
```

## Debounce

Comandos duplicados são ignorados dentro de 2500ms para evitar execução em duplicidade.

## Regra principal

A Misaka **nunca** fingir que está ouvindo. Se nenhum modo funcionar, mostra erro.

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| Permissão negada | Microfone bloqueado | Permitir microfone no browser/Electron |
| Modelo não encontrado | Vosk model ausente | Baixar modelo pt-BR |
| Serviço Python falhou | Python não instalado | `pip install -r requirements.txt` |
| Web Speech indisponível | Electron sem suporte | Usar modo nativo |
| Vivaldi não funciona | Service worker bloqueado | Usar Chrome/Edge |

## Segurança

- Escuta desligada por padrão.
- Áudio processado localmente.
- Apenas texto/comando enviado.
- Nenhum áudio bruto vai para o backend.
- Comandos perigosos exigem confirmação.
