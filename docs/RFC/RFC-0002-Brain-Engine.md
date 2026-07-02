# RFC-0002 — Misaka Brain Engine

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core  

---

## 1. Objetivo

Criar o primeiro **Brain Engine** da Misaka Network.

A Misaka não deve funcionar como um chatbot simples. Ela deve funcionar como uma arquitetura de agentes, onde o Brain recebe a mensagem do usuário, entende a intenção, escolhe o agente adequado e retorna uma resposta padronizada.

Nesta RFC, ainda não haverá integração real com Gemini, Supabase, Google Calendar ou qualquer API externa.

O objetivo é criar a base interna da inteligência da Misaka.

---

## 2. Escopo desta RFC

Esta RFC deve implementar:

- Brain Engine
- Planner
- Orchestrator
- Personality Engine
- Agent Interface
- Conversation Agent mock
- Padronização de resposta do `/chat`
- Refatoração das rotas da API
- Testes básicos

---

## 3. Fora do escopo

Não implementar nesta RFC:

- Gemini
- OpenAI
- Claude
- Supabase
- Memória real
- Calendário real
- Tarefas reais
- Controle do Android
- Controle do PC
- Voz
- Dashboard
- Autenticação

Esses recursos virão em RFCs futuras.

---

## 4. Arquitetura esperada

Fluxo esperado:

```text
User
  ↓
FastAPI /chat
  ↓
Brain Engine
  ↓
Planner
  ↓
Orchestrator
  ↓
Conversation Agent
  ↓
Personality Engine
  ↓
Mock response
  ↓
FastAPI Response

A API nunca deve conter lógica de decisão.

A rota /chat apenas recebe a requisição, chama o Brain e retorna a resposta.

5. Regras obrigatórias
5.1 API

As rotas devem ficar separadas:

backend/app/api/
├── router.py
├── health.py
└── chat.py

main.py não deve conter rotas diretamente.

5.2 Brain

O Brain é o centro da Misaka.

Ele pode conhecer:

Planner
Orchestrator
Personality Engine

Ele não deve chamar APIs externas diretamente.

5.3 Agents

Agentes nunca devem conversar diretamente entre si.

Agentes só devem ser chamados pelo Orchestrator.

5.4 Lógica externa

Nenhum módulo desta RFC deve chamar:

Gemini
OpenAI
Claude
Supabase
Google APIs
APIs externas

Tudo deve ser mockado.

5.5 Tipagem

Todo código novo deve ter type hints.

5.6 Tamanho dos arquivos

Nenhum arquivo deve ultrapassar 300 linhas.

6. Estrutura de arquivos esperada

Criar ou ajustar a estrutura:

backend/
├── app/
│   ├── api/
│   │   ├── router.py
│   │   ├── health.py
│   │   └── chat.py
│   │
│   ├── brain/
│   │   ├── engine.py
│   │   ├── planner.py
│   │   ├── orchestrator.py
│   │   ├── personality.py
│   │   └── interfaces.py
│   │
│   ├── agents/
│   │   ├── base.py
│   │   └── conversation/
│   │       ├── __init__.py
│   │       └── agent.py
│   │
│   ├── schemas/
│   │   └── chat.py
│   │
│   └── core/
│       ├── config.py
│       └── logging.py
│
├── tests/
│   ├── test_health.py
│   └── test_chat.py
│
└── main.py
7. Schemas

Criar backend/app/schemas/chat.py.

ChatRequest

Campos:

message: str
conversation_id: str | None = None
metadata: dict | None = None

Regras:

message é obrigatório.
message não pode ser vazio.
conversation_id é opcional.
metadata é opcional.
ChatResponse

Campos:

response: str
agent: str
model: str | None
execution_time: float
conversation_id: str
metadata: dict

Exemplo:

{
  "response": "Olá, eu sou a Misaka.",
  "agent": "conversation",
  "model": null,
  "execution_time": 0.004,
  "conversation_id": "generated-id",
  "metadata": {
    "intent": "conversation",
    "version": "0.1 Genesis"
  }
}
8. Brain Engine

Criar backend/app/brain/engine.py.

Responsabilidade:

Receber a mensagem do usuário.
Criar ou reaproveitar conversation_id.
Enviar mensagem para o Planner.
Enviar decisão para o Orchestrator.
Retornar resposta padronizada.

O Brain deve ter um método principal:

async def process_message(self, message: str, conversation_id: str | None = None, metadata: dict | None = None) -> ChatResponse:
    ...
9. Planner

Criar backend/app/brain/planner.py.

Responsabilidade:

Detectar a intenção inicial da mensagem.
Por enquanto, sempre retornar conversation.

Futuramente o Planner poderá retornar:

conversation
calendar
tasks
coding
android
desktop
minecraft
research

Modelo inicial:

class Planner:
    def detect_intent(self, message: str) -> str:
        return "conversation"
10. Orchestrator

Criar backend/app/brain/orchestrator.py.

Responsabilidade:

Receber a intenção do Planner.
Escolher o agente correto.
Executar o agente.

Nesta RFC, apenas o ConversationAgent precisa existir.

Se a intenção não for reconhecida, usar ConversationAgent.

11. Personality Engine

Criar backend/app/brain/personality.py.

Responsabilidade:

Definir a personalidade atual da Misaka.
Por enquanto, retornar uma personalidade padrão.

Personalidade padrão:

Você é Misaka, uma assistente pessoal privada, modular, direta e inteligente.
Você ajuda Daniel com programação, estudos, organização, calendário, tarefas,
Minecraft, servidores e automações.
Você deve ser objetiva, mas amigável.

Nesta RFC, a personalidade pode ser usada apenas como metadata ou texto interno do agente.

12. Interfaces

Criar backend/app/brain/interfaces.py.

Definir estruturas ou protocolos para:

Agent
Planner
Orchestrator

Objetivo:

Evitar acoplamento forte entre os módulos.

Pode usar Protocol do Python.

Exemplo:

from typing import Protocol

class AgentProtocol(Protocol):
    name: str

    async def run(self, message: str, context: dict) -> dict:
        ...
13. Base Agent

Criar backend/app/agents/base.py.

Responsabilidade:

Definir uma classe base para futuros agentes.

Campos mínimos:

name: str
description: str

Método obrigatório:

async def run(self, message: str, context: dict) -> dict:
    ...
14. Conversation Agent

Criar backend/app/agents/conversation/agent.py.

Responsabilidade:

Responder mensagens comuns.
Nesta RFC, resposta mock.

Comportamento inicial:

Se o usuário disser algo como:

Olá

Responder algo parecido com:

Olá, eu sou a Misaka. Meu Brain Engine já está online.

Caso contrário:

Recebi sua mensagem: {message}

Retorno interno esperado:

{
    "response": "...",
    "agent": "conversation",
    "model": None,
    "metadata": {
        "mock": True
    }
}
15. API
/health

Método: GET

Resposta:

{
  "status": "ok",
  "assistant": "Misaka",
  "version": "0.1 Genesis"
}
/chat

Método: POST

Entrada:

{
  "message": "Olá Misaka"
}

Saída:

{
  "response": "Olá, eu sou a Misaka. Meu Brain Engine já está online.",
  "agent": "conversation",
  "model": null,
  "execution_time": 0.004,
  "conversation_id": "uuid",
  "metadata": {
    "intent": "conversation",
    "mock": true,
    "version": "0.1 Genesis"
  }
}
16. Testes obrigatórios

Criar testes para:

Health

Arquivo:

tests/test_health.py

Verificar:

/health retorna status 200.
status é ok.
Chat

Arquivo:

tests/test_chat.py

Verificar:

/chat aceita uma mensagem válida.
/chat retorna response.
/chat retorna agent.
/chat retorna conversation_id.
/chat retorna execution_time.
/chat retorna metadata.
/chat rejeita mensagem vazia.
17. Critérios de aceitação

A RFC será considerada concluída quando:

/health funcionar.
/chat funcionar.
/chat passar pelo Brain Engine.
API não tiver lógica de decisão.
Planner existir.
Orchestrator existir.
Personality Engine existir.
Conversation Agent existir.
Schemas estiverem separados.
Testes básicos passarem.
Nenhuma API externa for chamada.
Código estiver tipado.
Arquivos estiverem organizados.
18. Comandos esperados

Rodar localmente:

uvicorn main:app --reload

ou, dependendo da estrutura:

uvicorn backend.main:app --reload

Rodar testes:

pytest
19. Observações para o agente desenvolvedor

O objetivo desta RFC não é criar inteligência real ainda.

O objetivo é criar o caminho correto para a inteligência.

Não implementar soluções rápidas diretamente na rota /chat.

Não chamar Gemini.

Não criar banco de dados.

Não criar dependências desnecessárias.

Não adicionar LangChain.

Manter o projeto simples, limpo e modular.