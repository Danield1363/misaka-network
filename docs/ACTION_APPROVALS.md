# Action Approval System

Misaka uses an approval system to protect against dangerous actions.

## Risk Levels

| Level | Behavior | Examples |
|-------|----------|----------|
| `safe` | Execute directly | Open app, clear chat, ack alerts |
| `medium` | Require confirmation | Close apps, send messages |
| `high` | Require confirmation | Run commands, change settings |
| `critical` | Block by default | Shutdown, delete files |

## How It Works

1. Misaka detects a command that requires confirmation
2. Returns a confirmation message to the user
3. User can respond "sim" to approve or "não" to deny
4. Dashboard shows a confirmation modal for UI actions
5. Approved actions are logged and executed

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/actions/pending-approvals` | List pending approvals |
| POST | `/api/actions/approvals` | Create approval request |
| POST | `/api/actions/approvals/{id}/approve` | Approve action |
| POST | `/api/actions/approvals/{id}/deny` | Deny action |

## Blocked Actions (Critical)

These actions are blocked by default and cannot be executed:

- `shutdown` — Shutdown PC
- `restart` — Restart PC
- `delete_files` — Delete files
- `shell_arbitrary` — Run arbitrary commands

## Configuration

Blocked actions can be configured in `desktop/control/permissions.js`.

## Security Rules

- No dangerous action executes without explicit confirmation
- Shell arbitrary commands disabled by default
- All actions generate action logs
- Tokens never exposed in frontend
- Secrets never placed in dashboard or desktop bundle
