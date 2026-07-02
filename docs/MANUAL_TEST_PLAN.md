# Manual Test Plan — Dashboard

## Prerequisites

1. Backend running on `http://localhost:8000`
2. Dashboard open at `http://localhost:8000` or `http://localhost:3000`

## Test Cases

### 1. Chat Basic Flow
1. Type "Olá Misaka" in the chat input
2. Press Enter or click Enviar
3. Verify: Response appears with "diz Misaka Misaka." suffix
4. Verify: Core visualizer animates (thinking → speaking → idle)

### 2. Command: Clear Alerts
1. Type "limpe os alertas atuais"
2. Press Enter
3. Verify: Response says alerts were marked as seen
4. Verify: Alert count updates in sidebar

### 3. Command: HUD Toggle
1. Type "ative o modo hud"
2. Press Enter
3. Verify: Background becomes transparent, HUD overlay appears
4. Type "desative o modo hud"
5. Verify: Normal background returns

### 4. Command: Voice Toggle
1. Type "ligue a voz"
2. Press Enter
3. Verify: Voice indicator shows enabled
4. Type "desligue a voz"
5. Verify: Voice indicator shows disabled

### 5. Voice Auto-Speak
1. Enable auto-speak in voice panel
2. Send multiple messages
3. Verify: Every response is spoken aloud
4. Verify: Previous speech is cancelled when new response arrives

### 6. Voice Controls
1. Click "Test" button
2. Verify: "Olá, eu sou a Misaka" is spoken
3. Click "Stop" button
4. Verify: Speech stops immediately
5. Adjust rate slider
6. Adjust pitch slider
7. Verify: New speech uses updated settings

### 7. Settings Drawer
1. Click gear icon in header
2. Verify: Settings drawer slides in from right
3. Verify: LLM status shows provider and model
4. Verify: Voice settings show current configuration
5. Press ESC
6. Verify: Drawer closes
7. Open again, click outside
8. Verify: Drawer closes

### 8. Alert Management
1. Verify: Alert count shows correct number
2. Click "✓ All" button
3. Verify: All alerts marked as seen
4. Click "↻" refresh button
5. Verify: Alerts refresh from server

### 9. Alert Filters
1. Click "Critical" filter
2. Verify: Only critical alerts shown
3. Click "Important" filter
4. Verify: Only important alerts shown
5. Click "All" filter
6. Verify: All alerts shown

### 10. Clear Chat
1. Send several messages
2. Click "Clear" button
3. Verify: Chat clears
4. Verify: "Conversa reiniciada" message appears

### 11. Copy Last Response
1. Send a message
2. Click copy icon
3. Verify: "Copiado!" toast appears
4. Paste in text editor
5. Verify: Response text is correct

### 12. Toast Notifications
1. Perform actions that trigger toasts
2. Verify: Toasts appear in bottom-right
3. Verify: Toasts auto-dismiss after 4 seconds
4. Verify: Toasts show correct type (success/error/info)

### 13. LLM Status Display
1. Verify: Provider badge shows "mock" or "gemini"
2. Verify: Model name displayed correctly
3. If Gemini: Verify fallback status when active
4. If mock: Verify warning message displayed

### 14. Module Status Grid
1. Verify: Brain shows "Active"
2. Verify: Memory shows "Enabled" or "Disabled"
3. Verify: Calendar shows status
4. Verify: Tools shows "Active"
5. Verify: LLM shows status

### 15. Responsive Layout
1. Resize browser to < 1024px
2. Verify: Alerts sidebar hides
3. Resize to < 768px
4. Verify: Left sidebar hides
5. Verify: Chat takes full width

### 16. Error Handling
1. Stop the backend
2. Send a message
3. Verify: "Erro ao conectar com o servidor" appears
4. Restart backend
5. Verify: Chat works again

### 17. Keyboard Shortcuts
1. Press Enter in chat input
2. Verify: Message sends
3. Press Shift+Enter
4. Verify: New line in input (no send)
