-- Action Approvals
CREATE TABLE IF NOT EXISTS action_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_name TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    risk_level TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'pending',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    denied_at TIMESTAMPTZ,
    CONSTRAINT valid_approval_status CHECK (status IN ('pending', 'approved', 'denied', 'expired'))
);

CREATE INDEX IF NOT EXISTS idx_action_approvals_status ON action_approvals(status);
CREATE INDEX IF NOT EXISTS idx_action_approvals_created ON action_approvals(created_at);
