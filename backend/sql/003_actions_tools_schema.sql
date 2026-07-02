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