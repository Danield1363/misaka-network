create table if not exists notifications (
    id uuid primary key default uuid_generate_v4(),
    app_name text not null,
    package_name text,
    title text,
    content text,
    sender text,
    channel text,
    received_at timestamptz not null,
    importance text not null default 'normal',
    category text not null default 'general',
    is_sensitive boolean not null default false,
    should_alert boolean not null default false,
    summary text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists notification_rules (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    rule_type text not null,
    pattern text not null,
    action text not null,
    importance text,
    enabled boolean not null default true,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists important_alerts (
    id uuid primary key default uuid_generate_v4(),
    notification_id uuid,
    title text not null,
    message text not null,
    status text not null default 'pending',
    priority text not null default 'important',
    created_at timestamptz not null default now(),
    acknowledged_at timestamptz
);

create index if not exists idx_notifications_received_at on notifications(received_at);
create index if not exists idx_notifications_importance on notifications(importance);
create index if not exists idx_notifications_should_alert on notifications(should_alert);
create index if not exists idx_important_alerts_status on important_alerts(status);