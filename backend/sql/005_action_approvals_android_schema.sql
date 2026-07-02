-- Action Approvals table
CREATE TABLE IF NOT EXISTS action_approvals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    action_name TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    risk_level TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    denied_at TIMESTAMPTZ
);

CREATE INDEX idx_action_approvals_status ON action_approvals(status);
CREATE INDEX idx_action_approvals_created_at ON action_approvals(created_at);

-- Android Actions table
CREATE TABLE IF NOT EXISTS android_actions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    device_id TEXT NOT NULL DEFAULT 'default',
    action_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    risk_level TEXT NOT NULL DEFAULT 'safe',
    requires_confirmation BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX idx_android_actions_status ON android_actions(status);
CREATE INDEX idx_android_actions_device_id ON android_actions(device_id);
CREATE INDEX idx_android_actions_created_at ON android_actions(created_at);
