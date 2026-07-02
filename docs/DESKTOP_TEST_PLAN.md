# Desktop Test Plan — Misaka Network

## Prerequisites

1. Node.js installed
2. `cd desktop && npm install`

## Test Cases

### 1. Basic Launch
1. Run `npm start`
2. Verify: Window opens with Misaka dashboard
3. Verify: Window title is "Misaka Network"
4. Verify: No console errors in dev tools

### 2. Dashboard Loading
1. Verify: Dashboard loads (not /docs)
2. Verify: API status shows in sidebar
3. Verify: Chat input is functional

### 3. Window Management
1. Click X to close
2. Verify: Window minimizes to tray (doesn't quit)
3. Double-click tray icon
4. Verify: Window reappears

### 4. System Tray
1. Right-click tray icon
2. Verify: Context menu shows (Show, Always on Top, HUD Mode, Quit)
3. Click "Show Misaka"
4. Verify: Window shows
5. Click "Always on Top"
6. Verify: Window stays on top of other windows
7. Click "HUD Mode"
8. Verify: Dashboard switches to HUD overlay mode

### 5. Notifications
1. Ensure backend has critical alerts
2. Wait for polling cycle (10 seconds)
3. Verify: Native notification appears
4. Click notification
5. Verify: Window focuses

### 6. Notification Deduplication
1. Wait for notification to appear
2. Wait for next polling cycle
3. Verify: Same notification doesn't appear again

### 7. Debug Mode
1. Run `npm run debug`
2. Verify: Logs appear in terminal
3. Verify: Electron debug info visible

### 8. Build .exe
1. Run `npm run dist`
2. Verify: `dist/` folder created
3. Verify: .exe file exists
4. Run the .exe
5. Verify: App opens correctly
6. Verify: Dashboard loads in .exe

### 9. Packaged Mode
1. Run `npm run pack`
2. Verify: Unpacked app in `dist/win-unpacked/`
3. Run the unpacked app
4. Verify: Dashboard loads from resources

### 10. Error Handling
1. Set invalid MISAKA_DASHBOARD_URL
2. Run `npm start`
3. Verify: Error window appears with clear message
4. Fix the URL
5. Verify: App works normally

### 11. IPC Bridge
1. Open dev tools in renderer
2. Check `window.misakaDesktop` exists
3. Verify: `isAvailable` is true
4. Verify: Methods are callable

### 12. Always On Top Persistence
1. Enable always on top via tray
2. Close and reopen app
3. Verify: Setting persists (if saved)

### 13. Memory Usage
1. Open app
2. Check memory usage in task manager
3. Verify: Memory usage is reasonable (< 200MB)
