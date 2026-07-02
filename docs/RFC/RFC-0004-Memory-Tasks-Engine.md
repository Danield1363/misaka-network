# RFC-0004 — Memory + Tasks Engine

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core  

---

## 1. Objetivo

Criar a primeira memória persistente da Misaka usando Supabase e adicionar um sistema básico de tarefas.

Depois desta RFC, a Misaka deve ser capaz de:

- Salvar memórias importantes.
- Listar memórias salvas.
- Buscar memórias por texto.
- Criar tarefas.
- Listar tarefas.
- Marcar tarefas como concluídas.
- Usar memórias como contexto no chat.
- Manter uma estrutura limpa para evoluir calendário, projetos e automações depois.

---

## 2. Escopo

Implementar nesta RFC:

- Supabase client.
- Memory Engine.
- Memory Repository.
- Task Engine.
- Task Repository.
- Schemas de memória.
- Schemas de tarefas.
- Rotas `/api/memory`.
- Rotas `/api/tasks`.
- Integração básica do Brain com memória.
- Testes com mock repository.
- Atualização do `.env.example`.
- SQL inicial para Supabase.

---

## 3. Fora do escopo

Não implementar ainda:

- Google Calendar real.
- Google Tasks real.
- Voz.
- Android control.
- Desktop control.
- Vector search.
- Embeddings.
- Autenticação completa.
- Dashboard.
- LangChain.

---

## 4. Arquitetura esperada

Fluxo de chat com memória:

```text
User
  ↓
/api/chat
  ↓
BrainEngine
  ↓
MemoryEngine
  ↓
Relevant memories
  ↓
Planner
  ↓
Orchestrator
  ↓
ConversationAgent
  ↓
LLMGateway
  ↓
Response
  ↓
MemoryEngine saves interaction summary

Fluxo de tarefa:

User/API
  ↓
/api/tasks
  ↓
TaskEngine
  ↓
TaskRepository
  ↓
Supabase
5. Regras obrigatórias
5.1 Nenhuma rota acessa Supabase diretamente

Permitido:

Route → Engine → Repository → Supabase

Proibido:

Route → Supabase
Agent → Supabase direto
Brain → Supabase direto
5.2 Supabase fica isolado

Todo acesso ao Supabase deve ficar em:

backend/app/services/supabase.py

e nos repositories.

5.3 Memória não pode quebrar o chat

Se o Supabase estiver fora do ar ou sem configuração, /api/chat ainda deve responder.

Nesse caso, adicionar no metadata:

{
  "memory_enabled": false
}
5.4 Segurança

Nunca logar:

SUPABASE_SERVICE_ROLE_KEY
GEMINI_API_KEY
qualquer chave secreta

O arquivo .env nunca deve ser commitado.

6. Estrutura esperada

Criar ou ajustar:

backend/app/
├── memory/
│   ├── __init__.py
│   ├── engine.py
│   ├── repository.py
│   ├── interfaces.py
│   └── errors.py
│
├── tasks/
│   ├── __init__.py
│   ├── engine.py
│   ├── repository.py
│   ├── interfaces.py
│   └── errors.py
│
├── services/
│   └── supabase.py
│
├── api/
│   ├── memory.py
│   ├── tasks.py
│   └── router.py
│
├── schemas/
│   ├── memory.py
│   └── tasks.py
│
└── core/
    └── config.py

backend/sql/
└── 001_initial_schema.sql

backend/tests/
├── test_memory.py
├── test_tasks.py
└── test_chat_memory.py
7. Variáveis de ambiente

Atualizar .env.example:

APP_NAME=Misaka Core
APP_VERSION=0.1 Genesis
ENVIRONMENT=development

LLM_PROVIDER=mock
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
MEMORY_ENABLED=false

Por padrão:

MEMORY_ENABLED=false

Isso permite rodar localmente sem Supabase.

8. Dependências

Adicionar ao requirements.txt ou equivalente:

supabase

Se já existir, não duplicar.

9. SQL inicial

Criar:

backend/sql/001_initial_schema.sql

Conteúdo esperado:

create extension if not exists "uuid-ossp";

create table if not exists memories (
    id uuid primary key default uuid_generate_v4(),
    content text not null,
    type text not null default 'general',
    source text not null default 'manual',
    importance integer not null default 3,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists tasks (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    description text,
    status text not null default 'pending',
    priority integer not null default 3,
    due_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists conversations (
    id uuid primary key default uuid_generate_v4(),
    conversation_id text not null,
    user_message text not null,
    assistant_response text not null,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_memories_type on memories(type);
create index if not exists idx_memories_content on memories using gin(to_tsvector('simple', content));
create index if not exists idx_tasks_status on tasks(status);
create index if not exists idx_tasks_due_at on tasks(due_at);
create index if not exists idx_conversations_conversation_id on conversations(conversation_id);
10. Memory Schemas

Criar:

backend/app/schemas/memory.py

Schemas:

MemoryCreate
MemoryUpdate
MemoryResponse
MemorySearchRequest
MemorySearchResponse
MemoryCreate

Campos:

content: str
type: str = "general"
source: str = "manual"
importance: int = 3
metadata: dict = {}

Regras:

content obrigatório.
content não pode ser vazio.
importance deve ser entre 1 e 5.

Tipos esperados inicialmente:

general
preference
project
task_context
profile
system
11. Task Schemas

Criar:

backend/app/schemas/tasks.py

Schemas:

TaskCreate
TaskUpdate
TaskResponse
TaskListResponse
TaskCreate

Campos:

title: str
description: str | None = None
priority: int = 3
due_at: datetime | None = None
metadata: dict = {}
TaskUpdate

Campos opcionais:

title
description
status
priority
due_at
metadata

Status aceitos:

pending
in_progress
done
cancelled
12. Supabase Service

Criar:

backend/app/services/supabase.py

Responsabilidade:

Criar cliente Supabase.
Validar configuração.
Não logar secrets.
Retornar None ou lançar erro controlado se não configurado.

Exemplo de uso:

client = get_supabase_client()

Se MEMORY_ENABLED=false, não criar cliente.

13. Memory Repository

Criar:

backend/app/memory/repository.py

Responsabilidades:

create_memory
get_memory
list_memories
search_memories
delete_memory
save_conversation

A busca inicial pode ser simples:

content ilike %query%

Não usar embeddings ainda.

14. Memory Engine

Criar:

backend/app/memory/engine.py

Responsabilidades:

Isolar regra de negócio.
Receber chamadas do Brain.
Buscar contexto relevante.
Salvar memórias.
Salvar conversas.

Métodos esperados:

async def create_memory(...)
async def search_memories(...)
async def get_relevant_context(message: str) -> list[dict]
async def save_interaction(conversation_id: str, user_message: str, assistant_response: str, metadata: dict)

Se memória estiver desativada, retornar vazio sem quebrar.

15. Task Repository

Criar:

backend/app/tasks/repository.py

Métodos esperados:

create_task
get_task
list_tasks
update_task
complete_task
delete_task
16. Task Engine

Criar:

backend/app/tasks/engine.py

Responsabilidades:

Criar tarefas.
Listar tarefas.
Marcar como concluída.
Validar status.
Preparar futuro Calendar Agent.
17. API Memory

Criar:

backend/app/api/memory.py

Endpoints:

Criar memória
POST /api/memory

Body:

{
  "content": "Daniel está criando a Misaka Network.",
  "type": "project",
  "importance": 5,
  "metadata": {
    "project": "Misaka Network"
  }
}
Listar memórias
GET /api/memory
Buscar memórias
POST /api/memory/search

Body:

{
  "query": "Misaka"
}
Deletar memória
DELETE /api/memory/{memory_id}
18. API Tasks

Criar:

backend/app/api/tasks.py

Endpoints:

Criar tarefa
POST /api/tasks

Body:

{
  "title": "Configurar Supabase da Misaka",
  "description": "Criar tabelas iniciais e testar memória",
  "priority": 5
}
Listar tarefas
GET /api/tasks

Query opcional:

?status=pending
Atualizar tarefa
PATCH /api/tasks/{task_id}
Concluir tarefa
POST /api/tasks/{task_id}/complete
Deletar tarefa
DELETE /api/tasks/{task_id}
19. Integração com BrainEngine

Atualizar o BrainEngine.

Antes:

Brain → Planner → Orchestrator

Depois:

Brain
  ↓
MemoryEngine.get_relevant_context(message)
  ↓
Planner
  ↓
Orchestrator
  ↓
Response
  ↓
MemoryEngine.save_interaction(...)

O contexto deve ser passado para o agente dentro do context.

Exemplo:

context = {
    "conversation_id": conversation_id,
    "metadata": metadata,
    "memories": relevant_memories,
    "personality": personality
}

O metadata final do /api/chat deve incluir:

{
  "memory_enabled": true,
  "memories_used": 2
}

Se memória desativada:

{
  "memory_enabled": false,
  "memories_used": 0
}
20. Atualizar ConversationAgent

O ConversationAgent deve usar as memórias do contexto para montar o prompt.

Exemplo interno:

System:
{personality}

Relevant memories:
- Daniel está criando a Misaka Network.
- Daniel quer que a Misaka seja privada.

User:
{message}

Se não houver memórias, seguir normalmente.

21. Testes obrigatórios

Criar ou atualizar testes.

test_memory.py

Testar:

criar memória mockada;
buscar memória mockada;
rejeitar conteúdo vazio;
rejeitar importância fora de 1 a 5;
memória desativada não quebra.
test_tasks.py

Testar:

criar tarefa;
listar tarefas;
atualizar tarefa;
concluir tarefa;
rejeitar status inválido;
rejeitar título vazio.
test_chat_memory.py

Testar:

/api/chat funciona com memória desativada;
/api/chat inclui memory_enabled;
/api/chat inclui memories_used;
Brain passa memories no contexto;
erro de memória não quebra chat.
22. Critérios de aceitação

A RFC será aprovada quando:

Supabase client existir.
Memory Engine existir.
Task Engine existir.
APIs /api/memory e /api/tasks existirem.
/api/chat continuar funcionando.
Memória desativada não quebrar nada.
Memória ativada usar Supabase.
Tarefas forem salvas no Supabase.
Testes passarem.
.env.example atualizado.
SQL inicial criado.
Nenhuma rota acessar Supabase diretamente.
Nenhum agente acessar Supabase diretamente.
Secrets não aparecerem em logs.
Código seguir a arquitetura existente.
23. Comandos esperados

Instalar dependências:

pip install supabase

Rodar testes:

pytest

Rodar API:

uvicorn main:app --reload

Testar health:

GET /api/health

Testar chat:

POST /api/chat

Testar memória:

POST /api/memory
GET /api/memory
POST /api/memory/search

Testar tarefas:

POST /api/tasks
GET /api/tasks
POST /api/tasks/{task_id}/complete
24. Observações para o Mimo

Esta RFC é maior que as anteriores.

Implementar com calma, mas sem fugir da arquitetura.

Não criar shortcuts.

Não colocar Supabase dentro das rotas.

Não colocar Supabase dentro dos agentes.

Não usar embeddings ainda.

Não usar LangChain.

Não implementar calendário ainda.

Não implementar autenticação ainda.

Não quebrar o /api/chat.

Prioridade máxima:
/chat continua funcionando mesmo se memória falhar.