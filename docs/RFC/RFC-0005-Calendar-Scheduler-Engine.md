# RFC-0005 — Calendar + Scheduler Engine

Status: Proposed  
Version: 0.1 Genesis  
Owner: Daniel  
Architect: ChatGPT  
Developer Agent: Mimo v2.5  
Target: Misaka Core  

---

## 1. Objetivo

Criar o sistema inicial de calendário, lembretes e agendamentos da Misaka.

Depois desta RFC, a Misaka deve ser capaz de:

- Criar eventos internos.
- Listar eventos.
- Atualizar eventos.
- Cancelar eventos.
- Criar lembretes.
- Listar lembretes.
- Marcar lembretes como concluídos.
- Detectar lembretes vencidos.
- Criar registros de notificação pendente.
- Ter base para futura integração com Google Calendar.
- Interpretar comandos simples relacionados a agenda e tarefas.

Exemplos futuros:

```text
Misaka, me lembra de estudar Python amanhã às 19h.
Misaka, marca uma reunião sexta às 14h.
Misaka, o que tenho hoje?
Misaka, lista meus lembretes pendentes.
2. Escopo

Implementar nesta RFC:

Calendar Engine
Calendar Repository
Scheduler Engine
Reminder Engine
Notification Outbox
Calendar Agent
Atualização do Planner
Integração inicial com Brain
Endpoints /api/calendar
Endpoints /api/reminders
Endpoints /api/scheduler
SQL adicional
Testes básicos
3. Fora do escopo

Não implementar ainda:

Google Calendar OAuth real.
Envio real de notificação no Android.
Envio real de e-mail.
Voz.
Controle do Android.
Controle do PC.
Dashboard.
Autenticação completa.
LangChain.
Cron externo.
Webhooks externos.
4. Arquitetura esperada

Fluxo de criação de evento:

User/API
  ↓
/api/calendar/events
  ↓
CalendarEngine
  ↓
CalendarRepository
  ↓
Supabase

Fluxo de lembrete:

User/API
  ↓
/api/reminders
  ↓
ReminderEngine
  ↓
CalendarRepository
  ↓
Supabase

Fluxo do scheduler:

SchedulerEngine
  ↓
Busca lembretes vencidos
  ↓
Cria Notification Outbox
  ↓
Marca lembrete como triggered

Fluxo pelo chat:

User
  ↓
/api/chat
  ↓
BrainEngine
  ↓
Planner detecta calendar/reminder/task
  ↓
Orchestrator
  ↓
CalendarAgent
  ↓
CalendarEngine ou ReminderEngine
  ↓
Response
5. Regras obrigatórias
5.1 Rotas não acessam Supabase diretamente

Permitido:

Route → Engine → Repository → Supabase

Proibido:

Route → Supabase
Agent → Supabase direto
Brain → Supabase direto
5.2 Scheduler não pode quebrar a API

Se o Supabase estiver desativado ou indisponível, o scheduler deve retornar erro controlado.

O /api/chat deve continuar funcionando.

5.3 Não executar notificações reais ainda

Nesta RFC, o sistema apenas cria registros em notification_outbox.

O envio real virá em RFC futura.

5.4 Horários

Todos os horários devem ser salvos em UTC no banco.

A API pode aceitar ISO 8601.

Exemplo:

{
  "starts_at": "2026-07-01T19:00:00Z"
}
6. Estrutura esperada

Criar ou ajustar:

backend/app/
├── calendar/
│   ├── __init__.py
│   ├── engine.py
│   ├── reminder_engine.py
│   ├── scheduler.py
│   ├── repository.py
│   ├── interfaces.py
│   └── errors.py
│
├── agents/
│   └── calendar/
│       ├── __init__.py
│       └── agent.py
│
├── api/
│   ├── calendar.py
│   ├── reminders.py
│   ├── scheduler.py
│   └── router.py
│
├── schemas/
│   ├── calendar.py
│   ├── reminders.py
│   └── scheduler.py
│
├── planner/
│   └── intent_rules.py
│
└── brain/
    ├── planner.py
    └── orchestrator.py

backend/sql/
└── 002_calendar_scheduler_schema.sql

backend/tests/
├── test_calendar.py
├── test_reminders.py
├── test_scheduler.py
└── test_calendar_agent.py
7. SQL adicional

Criar:

backend/sql/002_calendar_scheduler_schema.sql

Conteúdo esperado:

create table if not exists calendar_events (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    description text,
    location text,
    starts_at timestamptz not null,
    ends_at timestamptz,
    status text not null default 'scheduled',
    source text not null default 'misaka',
    external_id text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists reminders (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    description text,
    remind_at timestamptz not null,
    status text not null default 'pending',
    source text not null default 'misaka',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists notification_outbox (
    id uuid primary key default uuid_generate_v4(),
    type text not null default 'reminder',
    title text not null,
    message text not null,
    status text not null default 'pending',
    target text not null default 'default',
    payload jsonb not null default '{}'::jsonb,
    scheduled_for timestamptz,
    sent_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_calendar_events_starts_at on calendar_events(starts_at);
create index if not exists idx_calendar_events_status on calendar_events(status);
create index if not exists idx_reminders_remind_at on reminders(remind_at);
create index if not exists idx_reminders_status on reminders(status);
create index if not exists idx_notification_outbox_status on notification_outbox(status);
create index if not exists idx_notification_outbox_scheduled_for on notification_outbox(scheduled_for);
8. Schemas de calendário

Criar:

backend/app/schemas/calendar.py

Schemas:

CalendarEventCreate
CalendarEventUpdate
CalendarEventResponse
CalendarEventListResponse
CalendarEventCreate

Campos:

title: str
description: str | None = None
location: str | None = None
starts_at: datetime
ends_at: datetime | None = None
metadata: dict = {}

Regras:

title obrigatório.
title não pode ser vazio.
starts_at obrigatório.
Se ends_at existir, deve ser depois de starts_at.

Status aceitos:

scheduled
cancelled
done
9. Schemas de lembretes

Criar:

backend/app/schemas/reminders.py

Schemas:

ReminderCreate
ReminderUpdate
ReminderResponse
ReminderListResponse
ReminderCreate

Campos:

title: str
description: str | None = None
remind_at: datetime
metadata: dict = {}

Status aceitos:

pending
triggered
done
cancelled
10. Schemas de scheduler

Criar:

backend/app/schemas/scheduler.py

Schemas:

SchedulerRunResponse
NotificationOutboxResponse

Resposta esperada do scheduler:

{
  "processed_reminders": 2,
  "created_notifications": 2,
  "status": "ok"
}
11. Calendar Repository

Criar:

backend/app/calendar/repository.py

Métodos esperados:

create_event
get_event
list_events
update_event
cancel_event
delete_event

create_reminder
get_reminder
list_reminders
update_reminder
complete_reminder
cancel_reminder
get_due_reminders
mark_reminder_triggered

create_notification
list_notifications
mark_notification_sent

A implementação deve usar Supabase quando configurado.

Se MEMORY_ENABLED=false ou Supabase não estiver configurado, retornar erro controlado nas rotas de calendário, mas não quebrar o chat.

12. Calendar Engine

Criar:

backend/app/calendar/engine.py

Responsabilidades:

Criar eventos.
Listar eventos.
Atualizar eventos.
Cancelar eventos.
Buscar eventos por período.

Métodos esperados:

async def create_event(...)
async def list_events(...)
async def update_event(...)
async def cancel_event(...)
async def get_today_events(...)
async def get_upcoming_events(...)
13. Reminder Engine

Criar:

backend/app/calendar/reminder_engine.py

Responsabilidades:

Criar lembretes.
Listar lembretes.
Atualizar lembretes.
Marcar como concluído.
Cancelar lembretes.

Métodos esperados:

async def create_reminder(...)
async def list_reminders(...)
async def complete_reminder(...)
async def cancel_reminder(...)
async def get_pending_reminders(...)
14. Scheduler Engine

Criar:

backend/app/calendar/scheduler.py

Responsabilidades:

Buscar lembretes vencidos.
Criar notificações em notification_outbox.
Marcar lembretes como triggered.

Método principal:

async def run_due_reminders(self) -> dict:
    ...

Comportamento esperado:

Buscar lembretes com:
status = pending
remind_at <= now()
Para cada lembrete:
Criar uma notificação pendente.
Marcar lembrete como triggered.
Retornar contagem.
15. Calendar Agent

Criar:

backend/app/agents/calendar/agent.py

Responsabilidade:

Receber mensagens classificadas como calendário/lembrete.
Executar ações simples.
Responder de forma natural.

Nesta RFC, o agente pode usar parsing simples baseado em palavras-chave.

Exemplos mínimos:

Criar lembrete genérico

Se a mensagem tiver:

me lembra
lembrete
lembrar

Responder:

Posso criar esse lembrete, mas preciso de uma data e horário em formato claro.

Se o contexto já trouxer metadata estruturada futuramente, criar lembrete.

Consultar agenda

Se a mensagem tiver:

agenda
compromissos
eventos
hoje

Chamar CalendarEngine.get_today_events() ou get_upcoming_events().

Fallback

Se não entender:

Entendi que isso envolve sua agenda, mas preciso de mais detalhes.
16. Atualizar Planner

Atualizar:

backend/app/brain/planner.py

ou criar regras em:

backend/app/planner/intent_rules.py

Intenções mínimas:

conversation
calendar
reminder
tasks
coding

Regras simples:

Mensagens com:

agenda
evento
compromisso
reunião
calendário

→ calendar

Mensagens com:

me lembra
lembrete
lembrar
avisar

→ reminder

Mensagens com:

tarefa
lista de tarefas
pendência
concluir tarefa

→ tasks

Mensagens com:

código
programa
bug
erro
python
fastapi

→ coding

Caso contrário:

conversation
17. Atualizar Orchestrator

Atualizar:

backend/app/brain/orchestrator.py

Registrar:

ConversationAgent
CalendarAgent

Por enquanto:

calendar → CalendarAgent
reminder → CalendarAgent
tasks → ConversationAgent ou futuro TaskAgent
coding → ConversationAgent ou futuro CodingAgent

Não criar CodingAgent real ainda, a menos que já exista mock.

18. APIs de calendário

Criar:

backend/app/api/calendar.py

Endpoints:

Criar evento
POST /api/calendar/events

Body:

{
  "title": "Estudar Python",
  "description": "Sessão de estudos da Misaka",
  "starts_at": "2026-07-01T19:00:00Z",
  "ends_at": "2026-07-01T20:00:00Z"
}
Listar eventos
GET /api/calendar/events

Query opcional:

?from_date=2026-07-01T00:00:00Z&to_date=2026-07-07T23:59:59Z
Atualizar evento
PATCH /api/calendar/events/{event_id}
Cancelar evento
POST /api/calendar/events/{event_id}/cancel
Deletar evento
DELETE /api/calendar/events/{event_id}
19. APIs de lembretes

Criar:

backend/app/api/reminders.py

Endpoints:

Criar lembrete
POST /api/reminders

Body:

{
  "title": "Estudar algoritmos",
  "description": "Continuar aulas de programação",
  "remind_at": "2026-07-01T19:00:00Z"
}
Listar lembretes
GET /api/reminders

Query opcional:

?status=pending
Atualizar lembrete
PATCH /api/reminders/{reminder_id}
Concluir lembrete
POST /api/reminders/{reminder_id}/complete
Cancelar lembrete
POST /api/reminders/{reminder_id}/cancel
Deletar lembrete
DELETE /api/reminders/{reminder_id}
20. API de scheduler

Criar:

backend/app/api/scheduler.py

Endpoints:

Rodar scheduler manualmente
POST /api/scheduler/run

Resposta:

{
  "processed_reminders": 1,
  "created_notifications": 1,
  "status": "ok"
}
Listar notificações pendentes
GET /api/scheduler/notifications
21. Atualizar router principal

Atualizar:

backend/app/api/router.py

Incluir:

calendar_router
reminders_router
scheduler_router

Endpoints finais esperados:

/api/calendar/events
/api/reminders
/api/scheduler/run
/api/scheduler/notifications
22. Integração com Brain metadata

Quando Planner detectar calendar ou reminder, metadata final do /api/chat deve incluir:

{
  "intent": "calendar",
  "agent": "calendar",
  "calendar_enabled": true
}

ou:

{
  "intent": "reminder",
  "agent": "calendar",
  "calendar_enabled": true
}

Se Supabase/calendário estiver indisponível:

{
  "calendar_enabled": false
}

Mas /api/chat não deve quebrar.

23. Testes obrigatórios

Criar:

backend/tests/test_calendar.py
backend/tests/test_reminders.py
backend/tests/test_scheduler.py
backend/tests/test_calendar_agent.py

Testar:

Calendar
Criar evento válido.
Rejeitar evento sem título.
Rejeitar ends_at antes de starts_at.
Listar eventos.
Cancelar evento.
Reminders
Criar lembrete válido.
Rejeitar lembrete sem título.
Listar lembretes.
Concluir lembrete.
Cancelar lembrete.
Scheduler
Detectar lembretes vencidos.
Criar notification outbox.
Marcar lembrete como triggered.
Não processar lembretes futuros.
Rodar sem quebrar se não houver lembretes.
Calendar Agent
Mensagem com "agenda" vai para intenção calendar.
Mensagem com "me lembra" vai para intenção reminder.
CalendarAgent responde sem quebrar.
/api/chat continua funcionando.
24. Critérios de aceitação

A RFC será aprovada quando:

Calendar Engine existir.
Reminder Engine existir.
Scheduler Engine existir.
Calendar Agent existir.
Planner detectar calendar e reminder.
Orchestrator chamar CalendarAgent.
APIs /api/calendar/events, /api/reminders e /api/scheduler existirem.
SQL 002_calendar_scheduler_schema.sql existir.
Notification Outbox existir.
Scheduler processar lembretes vencidos.
Chat continuar funcionando.
Testes passarem.
Nenhuma rota acessar Supabase diretamente.
Nenhum agente acessar Supabase diretamente.
Google Calendar real não for implementado ainda.
Código manter tipagem.
Arquivos não passarem de 300 linhas.
25. Comandos esperados

Rodar testes:

pytest

Rodar API:

uvicorn main:app --reload

Testar:

GET /api/health
POST /api/chat
POST /api/calendar/events
GET /api/calendar/events
POST /api/reminders
GET /api/reminders
POST /api/scheduler/run
GET /api/scheduler/notifications
26. Observações para o Mimo

Esta RFC deve criar a fundação da agenda da Misaka.

Não implementar Google Calendar real ainda.

Não implementar envio real de notificações.

A prioridade é criar um calendário interno robusto e testável.

O scheduler deve ser manual nesta RFC através de /api/scheduler/run.

Em RFC futura, ele poderá rodar automaticamente em background, Docker worker ou cron.