const API_BASE = MISAKA_CONFIG.API_BASE_URL;

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const btnSend = document.getElementById('btnSend');
const btnClear = document.getElementById('btnClear');
const btnVoice = document.getElementById('btnVoice');
const btnHUD = document.getElementById('btnHUD');
const btnCopyLast = document.getElementById('btnCopyLast');
const btnSpeakLast = document.getElementById('btnSpeakLast');
const typingIndicator = document.getElementById('typingIndicator');
const coreVisualizer = document.getElementById('coreVisualizer');

let conversationId = null;
let lastResponse = '';
let voiceEnabled = localStorage.getItem('misaka_voice_enabled') === 'true';
let hudMode = localStorage.getItem('misaka_hud_mode') === 'true';
let pendingAlertIds = JSON.parse(localStorage.getItem('misaka_pending_alerts') || '[]');

function updateVoiceButton() {
    btnVoice.style.color = voiceEnabled ? 'var(--color-primary)' : 'var(--color-muted)';
}

function updateHUDButton() {
    btnHUD.style.color = hudMode ? 'var(--color-primary)' : 'var(--color-muted)';
    document.body.classList.toggle('hud-mode', hudMode);
}

async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/overview`);
        const data = await response.json();

        document.getElementById('version').textContent = `v${data.version}`;
        document.getElementById('llmProvider').textContent = data.llm_provider;
        document.getElementById('providerBadge').textContent = data.llm_provider;
        document.getElementById('memoryStatus').textContent = data.memory_enabled ? 'Enabled' : 'Disabled';
        document.getElementById('calendarStatus').textContent = data.calendar_enabled ? 'Enabled' : 'Disabled';
        document.getElementById('toolsStatus').textContent = data.tools_enabled ? 'Enabled' : 'Disabled';
        document.getElementById('notificationsStatus').textContent = data.notifications_enabled ? 'Enabled' : 'Disabled';

        document.getElementById('memoryModule').textContent = data.memory_enabled ? 'Active' : 'Disabled';
        document.getElementById('memoryModule').className = `module-status ${data.memory_enabled ? 'online' : ''}`;

        document.getElementById('calendarModule').textContent = data.calendar_enabled ? 'Active' : 'Disabled';
        document.getElementById('calendarModule').className = `module-status ${data.calendar_enabled ? 'online' : ''}`;

        document.getElementById('llmStatus').textContent = data.llm_provider === 'mock' ? 'Mock' : 'Active';
    } catch (error) {
        console.error('Failed to load status:', error);
    }
}

function setCoreState(state) {
    coreVisualizer.className = 'core-visualizer';
    if (state) {
        coreVisualizer.classList.add(state);
    }
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = type === 'user' ? 'D' : 'M';
    messageDiv.appendChild(avatarDiv);

    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'message-body';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    bodyDiv.appendChild(contentDiv);

    messageDiv.appendChild(bodyDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    lastResponse = text;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';

    setCoreState('thinking');
    typingIndicator.classList.add('active');
    btnSend.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });

        const data = await response.json();
        conversationId = data.conversation_id;

        setCoreState('speaking');
        addMessage(data.response, 'assistant');

        if (voiceEnabled) {
            speak(data.response);
        }

        setTimeout(() => setCoreState(null), 3000);
    } catch (error) {
        addMessage('Erro ao conectar com o servidor.', 'system');
        setCoreState(null);
    } finally {
        typingIndicator.classList.remove('active');
        btnSend.disabled = false;
        messageInput.focus();
    }
}

function clearChat() {
    chatMessages.innerHTML = '';
    conversationId = null;
    addMessage('Conversa reiniciada. Como posso ajudar?', 'system');
}

function speak(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.onstart = () => setCoreState('speaking');
        utterance.onend = () => setCoreState(null);
        window.speechSynthesis.speak(utterance);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).catch(err => {
        console.error('Failed to copy:', err);
    });
}

async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/notifications/alerts`);
        const data = await response.json();

        const alertsContainer = document.getElementById('alertsContainer');
        const alertsCount = document.getElementById('alertsCount');
        if (!alertsContainer) return;

        alertsContainer.textContent = '';

        if (data.alerts && data.alerts.length > 0) {
            alertsCount.textContent = data.alerts.length;

            data.alerts.slice(0, 10).forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert-item alert-${alert.priority}`;

                const titleSpan = document.createElement('span');
                titleSpan.className = 'alert-title';
                titleSpan.textContent = alert.title;
                alertDiv.appendChild(titleSpan);

                const messageSpan = document.createElement('span');
                messageSpan.className = 'alert-message';
                messageSpan.textContent = alert.message;
                alertDiv.appendChild(messageSpan);

                alertsContainer.appendChild(alertDiv);

                if (!pendingAlertIds.includes(alert.id)) {
                    pendingAlertIds.push(alert.id);
                    if (Notification.permission === 'granted') {
                        new Notification(alert.title, { body: alert.message });
                    }
                }
            });

            localStorage.setItem('misaka_pending_alerts', JSON.stringify(pendingAlertIds));
        } else {
            alertsCount.textContent = '0';
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'alert-empty';
            emptyDiv.textContent = 'No alerts';
            alertsContainer.appendChild(emptyDiv);
        }
    } catch (error) {
        console.error('Failed to load alerts:', error);
    }
}

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
});

btnSend.addEventListener('click', sendMessage);
btnClear.addEventListener('click', clearChat);

btnVoice.addEventListener('click', () => {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem('misaka_voice_enabled', voiceEnabled);
    updateVoiceButton();
});

btnHUD.addEventListener('click', () => {
    hudMode = !hudMode;
    localStorage.setItem('misaka_hud_mode', hudMode);
    updateHUDButton();
});

btnCopyLast.addEventListener('click', () => {
    if (lastResponse) copyToClipboard(lastResponse);
});

btnSpeakLast.addEventListener('click', () => {
    if (lastResponse) speak(lastResponse);
});

if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

loadStatus();
loadAlerts();
updateVoiceButton();
updateHUDButton();
messageInput.focus();

setInterval(loadStatus, MISAKA_CONFIG.POLL_INTERVAL_MS || 15000);
setInterval(loadAlerts, MISAKA_CONFIG.ALERTS_POLL_INTERVAL_MS || 10000);