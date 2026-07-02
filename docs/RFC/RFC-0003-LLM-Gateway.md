# RFC-0003 — LLM Gateway

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core  

---

## 1. Objetivo

Criar o LLM Gateway da Misaka.

A Misaka nunca deve depender diretamente de um único modelo de IA. O objetivo desta RFC é criar uma camada intermediária que permita usar Gemini agora e, no futuro, trocar para OpenAI, Claude, Ollama ou outros modelos sem alterar os agentes.

---

## 2. Escopo

Esta RFC deve implementar:

- LLM Gateway
- Interface base para provedores de IA
- Gemini Provider
- Mock Provider para testes
- Configuração por variáveis de ambiente
- Integração do ConversationAgent com o LLM Gateway
- Tratamento básico de erro
- Testes básicos

---

## 3. Fora do escopo

Não implementar nesta RFC:

- Memória no Supabase
- Calendário
- Tarefas reais
- Voz
- Dashboard
- Controle do Android
- Controle do PC
- LangChain
- Banco vetorial
- Autenticação

---

## 4. Regra principal

Nenhum módulo fora de `app/llm/` pode importar diretamente SDKs como Gemini, OpenAI, Claude ou similares.

Permitido:

```text
ConversationAgent → LLMGateway
LLMGateway → GeminiProvider

Proibido:

ConversationAgent → Gemini SDK
BrainEngine → Gemini SDK
API Route → Gemini SDK
5. Estrutura esperada

Criar ou ajustar:

backend/app/
├── llm/
│   ├── __init__.py
│   ├── gateway.py
│   ├── interfaces.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── mock.py
│   │   └── gemini.py
│   └── errors.py
│
├── agents/
│   └── conversation/
│       └── agent.py
│
├── core/
│   └── config.py
│
└── schemas/
    └── chat.py
6. Variáveis de ambiente

Atualizar .env.example:

APP_NAME=Misaka Core
APP_VERSION=0.1 Genesis
ENVIRONMENT=development

LLM_PROVIDER=mock
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash

Por padrão, LLM_PROVIDER deve ser mock.

Isso evita erro quando a pessoa ainda não configurou chave de API.

7. LLM Interfaces

Criar backend/app/llm/interfaces.py.

Deve existir um protocolo ou classe base para provedores:

from typing import Protocol

class LLMProviderProtocol(Protocol):
    name: str
    model: str | None

    async def generate(self, prompt: str, system_prompt: str | None = None, metadata: dict | None = None) -> str:
        ...
8. Mock Provider

Criar backend/app/llm/providers/mock.py.

Responsabilidade:

Retornar resposta falsa para desenvolvimento e testes.
Não chamar APIs externas.

Exemplo de resposta:

[Mock LLM] Recebi sua mensagem: {prompt}
9. Gemini Provider

Criar backend/app/llm/providers/gemini.py.

Responsabilidade:

Usar a chave GEMINI_API_KEY.
Usar o modelo definido em GEMINI_MODEL.
Receber prompt e system_prompt.
Retornar apenas o texto final.

Regras:

Se GEMINI_API_KEY não estiver configurada, lançar erro claro.
Não deixar a aplicação quebrar silenciosamente.
Não imprimir a API key em logs.
Não commitar .env.
10. LLM Gateway

Criar backend/app/llm/gateway.py.

Responsabilidade:

Escolher o provider correto com base em LLM_PROVIDER.
Expor um método único:
async def generate(self, prompt: str, system_prompt: str | None = None, metadata: dict | None = None) -> dict:
    ...

Retorno esperado:

{
    "text": "...",
    "provider": "gemini",
    "model": "gemini-1.5-flash",
    "metadata": {}
}
11. Erros

Criar backend/app/llm/errors.py.

Erros esperados:

class LLMError(Exception):
    pass

class LLMProviderNotConfiguredError(LLMError):
    pass

class LLMProviderNotFoundError(LLMError):
    pass
12. Conversation Agent

Atualizar ConversationAgent.

Antes ele respondia mockado.

Agora ele deve:

Receber mensagem.
Obter personalidade da Misaka pelo contexto.
Chamar o LLM Gateway.
Retornar resposta padronizada.

Retorno interno esperado:

{
    "response": "...",
    "agent": "conversation",
    "model": "gemini-1.5-flash",
    "metadata": {
        "provider": "gemini"
    }
}

Se LLM_PROVIDER=mock, deve retornar usando o Mock Provider.

13. Personality Engine

A personalidade padrão deve ser usada como system_prompt.

Personalidade inicial:

Você é Misaka, uma assistente pessoal privada, modular, direta e inteligente.
Você ajuda Daniel com programação, estudos, organização, calendário, tarefas,
Minecraft, servidores e automações.
Você deve ser objetiva, mas amigável.
14. Configuração

Atualizar core/config.py para carregar:

llm_provider: str
gemini_api_key: str | None
gemini_model: str

Usar valores padrão seguros.

15. Testes obrigatórios

Criar ou atualizar testes:

tests/test_llm_gateway.py
tests/test_chat.py

Testar:

LLM Gateway usa Mock Provider por padrão.
Mock Provider retorna texto.
/chat funciona com provider mock.
/chat retorna model.
/chat retorna metadata com provider.
Provider inválido gera erro controlado.
Mensagem vazia continua sendo rejeitada.
16. Critérios de aceitação

A RFC será considerada concluída quando:

LLMGateway existir.
MockProvider funcionar.
GeminiProvider existir.
ConversationAgent usar LLMGateway.
Nenhum agente importar Gemini diretamente.
.env.example estiver atualizado.
/chat funcionar com LLM_PROVIDER=mock.
/chat funcionar com LLM_PROVIDER=gemini quando houver API key.
Testes passarem.
API key não aparecer em logs.
.env não for commitado.
17. Comandos esperados

Instalar dependências necessárias:

pip install google-genai python-dotenv

Rodar local:

uvicorn main:app --reload

Rodar testes:

pytest
18. Observações para o agente desenvolvedor

Não implementar LangChain.

Não criar memória ainda.

Não criar banco de dados ainda.

Não adicionar lógica de IA dentro das rotas.

Não acoplar o ConversationAgent ao Gemini.

Toda chamada de modelo deve passar pelo LLM Gateway.

Esta RFC é sobre criar a camada de modelos da Misaka, não sobre criar agentes avançados.

19. Próxima RFC

Após esta RFC, a próxima será:

RFC-0004 — Memory Engine

Ela conectará a Misaka ao Supabase e permitirá memória persistente.


---

Agora manda para o Mimo:

> Implemente `docs/rfc/RFC-0003-LLM-Gateway.md` exatamente como descrito. Não implemente memória, banco, calendário ou voz. Use `LLM_PROVIDER=mock` como padrão. O ConversationAgent deve usar o LLM Gateway, nunca Gemini diretamente.

Quando ele terminar, me manda a árvore atualizada ou o commit. Aí eu reviso a **RFC-0003**.