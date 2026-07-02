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