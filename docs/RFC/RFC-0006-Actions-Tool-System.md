# RFC-0006 — Actions + Tool System

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core  

---

## 1. Objetivo

Criar o sistema oficial de ações e ferramentas da Misaka Network.

A Misaka não deve ter agentes chamando engines diretamente de forma desorganizada. A partir desta RFC, ações executáveis devem passar por um sistema central de ferramentas.

O objetivo é criar uma camada padronizada para que agentes possam executar capacidades como:

- Criar tarefa.
- Listar tarefas.
- Concluir tarefa.
- Criar memória.
- Buscar memórias.
- Criar lembrete.
- Listar lembretes.
- Criar evento.
- Listar eventos.
- Rodar scheduler.
- Futuramente controlar Android, PC, Minecraft e integrações externas.

---

## 2. Escopo

Implementar nesta RFC:

- Tool Interface
- Tool Registry
- Tool Executor
- Action Engine
- Action Log
- Permission System básico
- Dry Run Mode
- APIs de ferramentas
- Tools para Memory
- Tools para Tasks
- Tools para Calendar
- Tools para Reminders
- Tools para Scheduler
- Task Agent
- Coding Agent mock
- Atualização do Orchestrator
- Atualização do Brain metadata
- Testes básicos

---

## 3. Fora do escopo

Não implementar ainda:

- Android real.
- Desktop real.
- Minecraft real.
- Discord real.
- WhatsApp real.
- Google Calendar OAuth real.
- Voz.
- Dashboard.
- Autonomia total.
- Execução de comandos perigosos.
- LangChain.

---

## 4. Arquitetura esperada

Fluxo novo:

```text
User
  ↓
/api/chat
  ↓
BrainEngine
  ↓
Planner
  ↓
Orchestrator
  ↓
Agent
  ↓
ToolExecutor
  ↓
Tool
  ↓
Engine
  ↓
Repository
  ↓
Supabase

Exemplo:

User: "Misaka, cria uma tarefa para estudar Python"

BrainEngine
  ↓
Planner detecta tasks
  ↓
Orchestrator chama TaskAgent
  ↓
TaskAgent chama ToolExecutor
  ↓
ToolExecutor executa create_task
  ↓
TaskEngine cria tarefa
  ↓
Resposta final
5. Regra principal

Agentes não devem chamar diretamente:

MemoryEngine
TaskEngine
CalendarEngine
ReminderEngine
SchedulerEngine

A partir desta RFC, agentes devem usar:

ToolExecutor

Permitido:

Agent → ToolExecutor → Tool → Engine

Proibido:

Agent → Engine
Agent → Repository
Agent → Supabase
Route → Repository
6. Estrutura esperada

Criar ou ajustar:

backend/app/
├── actions/
│   ├── __init__.py
│   ├── engine.py
│   ├── repository.py
│   ├── interfaces.py
│   └── errors.py
│
├── tools/
│   ├── __init__.py
│   ├── base.py
│   ├── registry.py
│   ├── executor.py
│   ├── permissions.py
│   ├── errors.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── create_memory.py
│   │   └── search_memory.py
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── create_task.py
│   │   ├── list_tasks.py
│   │   └── complete_task.py
│   │
│   ├── calendar/
│   │   ├── __init__.py
│   │   ├── create_event.py
│   │   └── list_events.py
│   │
│   ├── reminders/
│   │   ├── __init__.py
│   │   ├── create_reminder.py
│   │   └── list_reminders.py
│   │
│   └── scheduler/
│       ├── __init__.py
│       └── run_scheduler.py
│
├── agents/
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── agent.py
│   │
│   └── coding/
│       ├── __init__.py
│       └── agent.py
│
├── api/
│   ├── tools.py
│   ├── actions.py
│   └── router.py
│
├── schemas/
│   ├── tools.py
│   └── actions.py
│
└── brain/
    ├── planner.py
    └── orchestrator.py

backend/sql/
└── 003_actions_tools_schema.sql

backend/tests/
├── test_tool_registry.py
├── test_tool_executor.py
├── test_actions.py
├── test_task_agent.py
└── test_coding_agent.py
7. SQL adicional

Criar:

backend/sql/003_actions_tools_schema.sql

Conteúdo esperado:

create table if not exists action_logs (
    id uuid primary key default uuid_generate_v4(),
    action_name text not null,
    tool_name text,
    agent_name text,
    status text not null default 'pending',
    input jsonb not null default '{}'::jsonb,
    output jsonb not null default '{}'::jsonb,
    error text,
    dry_run boolean not null default false,
    requires_confirmation boolean not null default false,
    confirmed boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    completed_at timestamptz
);

create index if not exists idx_action_logs_action_name on action_logs(action_name);
create index if not exists idx_action_logs_tool_name on action_logs(tool_name);
create index if not exists idx_action_logs_agent_name on action_logs(agent_name);
create index if not exists idx_action_logs_status on action_logs(status);
create index if not exists idx_action_logs_created_at on action_logs(created_at);
8. Tool Base

Criar:

backend/app/tools/base.py

Toda ferramenta deve ter:

name: str
description: str
category: str
requires_confirmation: bool = False
danger_level: str = "safe"

Danger levels aceitos:

safe
low
medium
high
critical

Método obrigatório:

async def run(self, input_data: dict, context: dict | None = None) -> dict:
    ...

Retorno padrão:

{
    "success": True,
    "data": {},
    "metadata": {}
}

Em caso de erro:

{
    "success": False,
    "error": "Mensagem do erro",
    "metadata": {}
}
9. Tool Registry

Criar:

backend/app/tools/registry.py

Responsabilidades:

Registrar ferramentas disponíveis.
Buscar ferramenta por nome.
Listar ferramentas.
Evitar ferramentas duplicadas.
Permitir expansão futura por plugins.

Métodos esperados:

register(tool)
get_tool(name: str)
list_tools()
has_tool(name: str)

Ferramentas iniciais registradas:

memory.create
memory.search

tasks.create
tasks.list
tasks.complete

calendar.create_event
calendar.list_events

reminders.create
reminders.list

scheduler.run
10. Tool Executor

Criar:

backend/app/tools/executor.py

Responsabilidades:

Receber nome da ferramenta.
Validar se ela existe.
Verificar permissões.
Executar dry-run quando solicitado.
Executar ferramenta real quando permitido.
Retornar resultado padronizado.
Registrar action log usando ActionEngine.

Método principal:

async def execute(
    self,
    tool_name: str,
    input_data: dict,
    context: dict | None = None,
    dry_run: bool = False,
    confirmed: bool = False
) -> dict:
    ...

Retorno esperado:

{
    "success": True,
    "tool": "tasks.create",
    "dry_run": False,
    "requires_confirmation": False,
    "data": {},
    "metadata": {}
}
11. Permission System

Criar:

backend/app/tools/permissions.py

Nesta RFC, permissões serão simples.

Regras:

Ferramentas safe

Podem rodar sem confirmação.

Exemplos:

memory.search
tasks.list
calendar.list_events
reminders.list
scheduler.run
Ferramentas low

Podem rodar sem confirmação inicialmente.

Exemplos:

tasks.create
memory.create
reminders.create
calendar.create_event
Ferramentas medium/high/critical

Devem exigir confirmação.

Futuramente:

android.send_message
desktop.run_command
minecraft.restart_server

Nesta RFC, não criar ferramentas perigosas reais.

12. Action Engine

Criar:

backend/app/actions/engine.py

Responsabilidades:

Criar logs de ações.
Atualizar status.
Registrar sucesso.
Registrar erro.
Listar logs.
Buscar log por ID.

Status aceitos:

pending
running
success
failed
cancelled
requires_confirmation

Métodos esperados:

async def log_action_start(...)
async def log_action_success(...)
async def log_action_error(...)
async def list_action_logs(...)
async def get_action_log(...)

Se Supabase estiver desativado, o ActionEngine deve funcionar em modo silencioso sem quebrar a execução.

13. Action Repository

Criar:

backend/app/actions/repository.py

Responsabilidade:

Acessar tabela action_logs.
Nunca ser chamado diretamente por rotas ou agentes.

Métodos esperados:

create_action_log
update_action_log
list_action_logs
get_action_log
14. Schemas de Tools

Criar:

backend/app/schemas/tools.py

Schemas:

ToolInfo
ToolListResponse
ToolExecuteRequest
ToolExecuteResponse
ToolExecuteRequest

Campos:

tool_name: str
input_data: dict = {}
dry_run: bool = False
confirmed: bool = False
metadata: dict = {}
15. Schemas de Actions

Criar:

backend/app/schemas/actions.py

Schemas:

ActionLogResponse
ActionLogListResponse

Campos esperados:

id: str | None
action_name: str
tool_name: str | None
agent_name: str | None
status: str
input: dict
output: dict
error: str | None
dry_run: bool
requires_confirmation: bool
confirmed: bool
metadata: dict
created_at: datetime | None
completed_at: datetime | None
16. API Tools

Criar:

backend/app/api/tools.py

Endpoints:

Listar ferramentas
GET /api/tools

Resposta:

{
  "tools": [
    {
      "name": "tasks.create",
      "description": "Create a task",
      "category": "tasks",
      "danger_level": "low",
      "requires_confirmation": false
    }
  ]
}
Executar ferramenta manualmente
POST /api/tools/execute

Body:

{
  "tool_name": "tasks.create",
  "input_data": {
    "title": "Estudar Python",
    "priority": 5
  },
  "dry_run": false,
  "confirmed": false
}
17. API Actions

Criar:

backend/app/api/actions.py

Endpoints:

Listar action logs
GET /api/actions/logs

Query opcional:

?status=success
Buscar action log
GET /api/actions/logs/{action_id}
18. Memory Tools

Criar ferramentas:

memory.create
memory.search
memory.create

Input:

{
  "content": "Daniel quer que a Misaka seja privada.",
  "type": "preference",
  "importance": 5,
  "metadata": {}
}

Engine usado:

MemoryEngine
memory.search

Input:

{
  "query": "Misaka"
}

Engine usado:

MemoryEngine
19. Task Tools

Criar ferramentas:

tasks.create
tasks.list
tasks.complete
tasks.create

Input:

{
  "title": "Configurar Oracle para Misaka",
  "description": "Criar VPS e preparar Docker",
  "priority": 5,
  "due_at": null,
  "metadata": {}
}

Engine usado:

TaskEngine
tasks.list

Input:

{
  "status": "pending"
}
tasks.complete

Input:

{
  "task_id": "uuid"
}
20. Calendar Tools

Criar ferramentas:

calendar.create_event
calendar.list_events
calendar.create_event

Input:

{
  "title": "Estudar programação",
  "description": "Aula de algoritmos",
  "starts_at": "2026-07-01T19:00:00Z",
  "ends_at": "2026-07-01T20:00:00Z",
  "metadata": {}
}
calendar.list_events

Input:

{
  "from_date": null,
  "to_date": null
}
21. Reminder Tools

Criar ferramentas:

reminders.create
reminders.list
reminders.create

Input:

{
  "title": "Estudar Python",
  "description": "Continuar aula de algoritmos",
  "remind_at": "2026-07-01T19:00:00Z",
  "metadata": {}
}
reminders.list

Input:

{
  "status": "pending"
}
22. Scheduler Tool

Criar ferramenta:

scheduler.run

Input:

{}

Responsabilidade:

Chamar SchedulerEngine.
Retornar quantidade de lembretes processados.
Retornar quantidade de notificações criadas.
23. Task Agent

Criar:

backend/app/agents/tasks/agent.py

Responsabilidade:

Responder mensagens classificadas como tasks.
Usar ToolExecutor.
Não chamar TaskEngine diretamente.

Parsing simples inicial:

Criar tarefa

Se mensagem tiver:

cria tarefa
criar tarefa
adiciona tarefa
adicionar tarefa
nova tarefa

Criar tarefa com título extraído de forma simples.

Exemplo:

Misaka, cria tarefa estudar Python

Deve chamar:

tasks.create
Listar tarefas

Se mensagem tiver:

listar tarefas
minhas tarefas
tarefas pendentes

Deve chamar:

tasks.list
Fallback

Responder:

Entendi que isso envolve tarefas, mas preciso de mais detalhes.
24. Coding Agent mock

Criar:

backend/app/agents/coding/agent.py

Responsabilidade:

Receber mensagens classificadas como coding.
Nesta RFC, não executar código real.
Apenas responder que a tarefa foi classificada como programação.

Resposta exemplo:

Entendi que essa é uma tarefa de programação. Por enquanto, o Coding Agent está em modo mock.

Metadata:

{
  "mock": true,
  "agent_type": "coding"
}
25. Atualizar Planner

Atualizar planner para manter intenções:

conversation
calendar
reminder
tasks
coding

Reforçar palavras-chave de tasks:

tarefa
tarefas
lista de tarefas
pendência
pendencias
concluir tarefa
nova tarefa
cria tarefa
adiciona tarefa

Reforçar palavras-chave de coding:

código
codigo
programar
programação
python
fastapi
bug
erro
api
docker
github
commit
26. Atualizar Orchestrator

Atualizar:

backend/app/brain/orchestrator.py

Registrar:

conversation → ConversationAgent
calendar → CalendarAgent
reminder → CalendarAgent
tasks → TaskAgent
coding → CodingAgent

Fallback:

conversation
27. Atualizar Calendar Agent

O CalendarAgent deve passar a usar ToolExecutor para:

calendar.list_events
reminders.create
reminders.list

Ele não deve chamar CalendarEngine ou ReminderEngine diretamente.

28. Integração com Brain metadata

Resposta do /api/chat deve incluir metadata útil:

{
  "intent": "tasks",
  "agent": "tasks",
  "tools_used": ["tasks.create"],
  "actions_logged": true
}

Quando nenhuma ferramenta for usada:

{
  "tools_used": []
}
29. Dry Run Mode

O ToolExecutor deve suportar:

{
  "dry_run": true
}

Quando dry_run=true:

Não executar ação real.
Retornar o que seria executado.
Registrar action log com dry_run=true, se possível.

Resposta exemplo:

{
  "success": true,
  "tool": "tasks.create",
  "dry_run": true,
  "would_execute": true,
  "input_data": {
    "title": "Estudar Python"
  }
}
30. Confirmação

Se uma ferramenta tiver:

requires_confirmation = True

e confirmed=false, o ToolExecutor deve retornar:

{
  "success": false,
  "requires_confirmation": true,
  "message": "Esta ação requer confirmação antes de ser executada."
}

Nesta RFC, todas as ferramentas reais devem ser safe ou low.

31. Testes obrigatórios

Criar ou atualizar testes:

test_tool_registry.py

Testar:

Registrar ferramenta.
Buscar ferramenta.
Listar ferramentas.
Evitar duplicata.
Erro para ferramenta inexistente.
test_tool_executor.py

Testar:

Executar ferramenta mock.
Dry run não executa ação real.
Ferramenta inexistente gera erro controlado.
Ferramenta com confirmação exige confirmação.
Retorno padronizado.
test_actions.py

Testar:

ActionEngine registra início.
ActionEngine registra sucesso.
ActionEngine registra erro.
ActionEngine não quebra com Supabase desativado.
test_task_agent.py

Testar:

Planner detecta tasks.
TaskAgent cria tarefa via ToolExecutor.
TaskAgent lista tarefas via ToolExecutor.
TaskAgent não chama TaskEngine diretamente.
/api/chat funciona com intenção tasks.
test_coding_agent.py

Testar:

Planner detecta coding.
Orchestrator chama CodingAgent.
CodingAgent responde mockado.
/api/chat funciona com intenção coding.
32. Critérios de aceitação

A RFC será aprovada quando:

Tool Registry existir.
Tool Executor existir.
Action Engine existir.
Action Log SQL existir.
APIs /api/tools e /api/actions/logs existirem.
Memory Tools existirem.
Task Tools existirem.
Calendar Tools existirem.
Reminder Tools existirem.
Scheduler Tool existir.
Task Agent existir.
Coding Agent mock existir.
Calendar Agent usar ToolExecutor.
Agentes não chamarem engines diretamente.
Orchestrator registrar TaskAgent e CodingAgent.
Dry run funcionar.
Confirmação básica funcionar.
Testes passarem.
/api/chat continuar funcionando.
/api/tasks, /api/memory, /api/calendar, /api/reminders continuarem funcionando.
Nenhuma rota acessar repository diretamente.
Nenhum agente acessar repository diretamente.
Nenhum segredo aparecer em logs.
33. Comandos esperados

Rodar testes:

pytest

Rodar API:

uvicorn main:app --reload

Testar:

GET /api/tools
POST /api/tools/execute
GET /api/actions/logs
POST /api/chat

Teste manual de ferramenta:

{
  "tool_name": "tasks.create",
  "input_data": {
    "title": "Estudar Python",
    "priority": 5
  },
  "dry_run": true
}

Teste manual de chat:

{
  "message": "Misaka, cria tarefa estudar Python"
}

Resposta esperada:

{
  "response": "...",
  "agent": "tasks",
  "metadata": {
    "intent": "tasks",
    "tools_used": ["tasks.create"]
  }
}
34. Observações para o Mimo

Esta RFC é a base do sistema de habilidades da Misaka.

Não implementar Android, Desktop ou Minecraft ainda.

Não executar comandos reais do sistema.

Não criar ferramentas perigosas.

Não permitir que agentes chamem engines diretamente.

O objetivo é padronizar ações.

Depois desta RFC, novas capacidades devem ser implementadas como Tools.