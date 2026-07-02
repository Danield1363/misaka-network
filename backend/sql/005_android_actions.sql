-- Android Action Queue
CREATE TABLE IF NOT EXISTS android_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id TEXT,
    action_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    risk_level TEXT NOT NULL DEFAULT 'safe',
    requires_confirmation BOOLEAN DEFAULT FALSE,
    result JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_android_actions_status ON android_actions(status);
CREATE INDEX IF NOT EXISTS idx_android_actions_device ON android_actions(device_id);
CREATE INDEX IF NOT EXISTS idx_android_actions_created ON android_actions(created_at);
