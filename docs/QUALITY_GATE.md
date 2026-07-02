# Quality Gate — Misaka v0.3 Genesis

Use this checklist before any merge or release.

## Backend

- [ ] `GET /api/health` returns 200 with status=ok
- [ ] `GET /api/status` returns version, provider, memory, calendar, tools
- [ ] `GET /api/overview` returns full system status with alert counts
- [ ] `GET /api/llm/status` returns provider, models, cooldowns, errors
- [ ] `POST /api/chat` responds to conversation messages
- [ ] `POST /api/chat` executes commands ("limpe os alertas atuais")
- [ ] `GET /api/notifications/alerts` returns alert list
- [ ] `POST /api/notifications/alerts/ack-all` marks all as seen
- [ ] `POST /api/commands/route` routes commands
- [ ] `GET /api/commands/confirmations/pending` lists pending confirmations
- [ ] `GET /api/actions/pending-approvals` lists pending approvals
- [ ] `GET /api/android/status` returns bridge status
- [ ] `GET /api/settings` returns user settings
- [ ] `PUT /api/settings` updates user settings
- [ ] `GET /api/devices` lists registered devices
- [ ] `POST /api/devices/register` registers a device
- [ ] All 249 tests pass

## Dashboard

- [ ] Loads without console errors
- [ ] Shows correct LLM provider and model
- [ ] Shows Gemini/Flash/fallback status
- [ ] Chat sends and receives messages
- [ ] Voice speaks all responses when auto-speak is on
- [ ] HUD toggles on/off
- [ ] Settings drawer opens/closes (ESC, click-outside)
- [ ] Alerts load and display correctly
- [ ] "Mark all as seen" clears pending alerts
- [ ] Refresh button updates alerts
- [ ] Toast notifications appear for actions
- [ ] Confirmation modal appears for sensitive actions
- [ ] Wake word shows correct state
- [ ] Errors display clearly (no stack traces)

## Desktop

- [ ] `npm install` succeeds
- [ ] `npm start` opens window
- [ ] `npm run debug` shows logs
- [ ] App doesn't close silently (minimizes to tray)
- [ ] App opens dashboard, never /docs
- [ ] Tray icon works (show, always-on-top, quit)
- [ ] Always on top toggles
- [ ] HUD mode works
- [ ] Native notifications work
- [ ] Notifications don't repeat
- [ ] `npm run dist` generates .exe
- [ ] .exe opens correctly

## Security

- [ ] No tokens in frontend code
- [ ] No tokens hardcoded in source
- [ ] No secrets in desktop bundle
- [ ] API keys not in logs
- [ ] Dangerous actions blocked by default
- [ ] Sensitive actions require confirmation
- [ ] Action approvals functional
- [ ] Action logs generated
- [ ] Error messages don't leak internals
