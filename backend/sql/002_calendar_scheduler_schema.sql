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