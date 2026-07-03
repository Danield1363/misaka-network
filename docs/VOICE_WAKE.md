# Voice Wake — Misaka v0.3.6

## Modos de voz

A Misaka suporta três modos de reconhecimento de voz:

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

## Regra principal

A Misaka **nunca** fingir que está ouvindo. Se nenhum modo funcionar, mostra erro.

## Escolha automática de modo

O controller escolhe automaticamente:

```
Web Speech disponível? → web_speech
Web Speech indisponível + Native disponível? → native_desktop
Nenhum disponível? → unavailable
```

## Ativação

1. Clique em "Ativar escuta Misaka".
2. Se Web Speech: pede permissão do microfone.
3. Se Native: inicia serviço Python.
4. Status aparece na UI.

## Comandos por voz

Todos os comandos usam o mesmo pipeline do chat:

```
"Misaka, abra o YouTube"
→ sendMessage("abra o YouTube", { source: "voice" })
```

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| Permissão negada | Microfone bloqueado | Permitir microfone no browser/Electron |
| Modelo não encontrado | Vosk model ausente | Baixar modelo pt-BR |
| Serviço Python falhou | Python não instalado | `pip install -r requirements.txt` |
| Web Speech indisponível | Electron sem suporte | Usar modo nativo |

## Segurança

- Escuta desligada por padrão.
- Áudio processado localmente.
- Apenas texto/comando enviado.
- Nenhum áudio bruto vai para o backend.
