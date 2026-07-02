const API_BASE = MISAKA_CONFIG.API_BASE_URL;

// DOM Elements
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
const voiceSelect = document.getElementById('voiceSelect');
const voiceRateSlider = document.getElementById('voiceRate');
const voicePitchSlider = document.getElementById('voicePitch');
const rateValue = document.getElementById('rateValue');
const pitchValue = document.getElementById('pitchValue');
const voiceEnabledToggle = document.getElementById('voiceEnabledToggle');
const autoSpeakToggle = document.getElementById('autoSpeakToggle');
const btnTestVoice = document.getElementById('btnTestVoice');

// State
let conversationId = null;
let lastResponse = '';
let voiceEnabled = localStorage.getItem('misaka_voice_enabled') !== 'false';
let hudMode = localStorage.getItem('misaka_hud_mode') === 'true';
let autoSpeak = localStorage.getItem('misaka_auto_speak') === 'true';
let selectedVoiceName = localStorage.getItem('misaka_voice_name') || '';
let voiceRate = parseFloat(localStorage.getItem('misaka_voice_rate') || '1.0');
let voicePitch = parseFloat(localStorage.getItem('misaka_voice_pitch') || '1.1');
let pendingAlertIds = JSON.parse(localStorage.getItem('misaka_pending_alerts') || '[]');
let currentProvider = 'mock';
let currentModel = 'mock';

// Voice Functions
function initVoiceControls() {
    voiceRateSlider.value = voiceRate;
    voicePitchSlider.value = voicePitch;
    rateValue.textContent = voiceRate;
    pitchValue.textContent = voicePitch;
    voiceEnabledToggle.checked = voiceEnabled;
    autoSpeakToggle.checked = autoSpeak;

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = populateVoiceSelect;
        populateVoiceSelect();
    }
}

function populateVoiceSelect() {
    const voices = window.speechSynthesis.getVoices();
    voiceSelect.innerHTML = '<option value="">Default (pt-BR)</option>';

    const ptBrVoices = voices.filter(v => v.lang.includes('pt-BR'));
    const ptVoices = voices.filter(v => v.lang.includes('pt') && !v.lang.includes('pt-BR'));

    if (ptBrVoices.length > 0) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = 'Portuguese (Brazil)';
        ptBrVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name}${voice.localService ? ' (local)' : ''}`;
            if (voice.name === selectedVoiceName) option.selected = true;
            optgroup.appendChild(option);
        });
        voiceSelect.appendChild(optgroup);
    }

    if (ptVoices.length > 0) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = 'Portuguese';
        ptVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name}${voice.localService ? ' (local)' : ''}`;
            if (voice.name === selectedVoiceName) option.selected = true;
            optgroup.appendChild(option);
        });
        voiceSelect.appendChild(optgroup);
    }
}

function getSelectedVoice() {
    const voices = window.speechSynthesis.getVoices();
    if (selectedVoiceName) {
        const found = voices.find(v => v.name === selectedVoiceName);
        if (found) return found;
    }
    const ptBrFemale = voices.find(v =>
        v.lang.includes('pt-BR') &&
        (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('feminina'))
    );
    if (ptBrFemale) return ptBrFemale;
    const ptBr = voices.find(v => v.lang.includes('pt-BR'));
    if (ptBr) return ptBr;
    const female = voices.find(v =>
        v.name.toLowerCase().includes('female') ||
        v.name.toLowerCase().includes('feminina')
    );
    return female || voices[0];
}

function speak(text) {
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = voiceRate;
    utterance.pitch = voicePitch;

    const voice = getSelectedVoice();
    if (voice) {
        utterance.voice = voice;
    }

    utterance.onstart = () => setCoreState('speaking');
    utterance.onend = () => setCoreState(null);
    window.speechSynthesis.speak(utterance);
}

function testVoice() {
    speak('Olá, eu sou a Misaka. Esta é minha voz.');
}

// UI Functions
function updateVoiceButton() {
    btnVoice.style.color = voiceEnabled ? 'var(--color-primary)' : 'var(--color-muted)';
}

function updateHUDButton() {
    btnHUD.style.color = hudMode ? 'var(--color-primary)' : 'var(--color-muted)';
    document.body.classList.toggle('hud-mode', hudMode);
}

function showProviderStatus(provider, model, geminiConfigured) {
    const existing = document.querySelector('.mock-warning, .gemini-active');
    if (existing) existing.remove();

    const chatSection = document.querySelector('.chat-section');

    if (provider === 'mock') {
        const warning = document.createElement('div');
        warning.className = 'mock-warning';
        warning.textContent = 'Misaka está em modo simulação. Configure GEMINI_API_KEY para respostas inteligentes.';
        chatSection.prepend(warning);
    } else if (provider === 'gemini') {
        const active = document.createElement('div');
        active.className = 'gemini-active';
        active.textContent = `Gemini ativo — ${model}`;
        chatSection.prepend(active);
    }
}

async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/overview`);
        const data = await response.json();

        currentProvider = data.llm_provider;
        currentModel = data.llm_model;

        document.getElementById('version').textContent = `v${data.version}`;
        document.getElementById('llmProvider').textContent = data.llm_provider;
        document.getElementById('llmModel').textContent = data.llm_model;
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

        showProviderStatus(data.llm_provider, data.llm_model, data.gemini_configured);
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

// Chat Functions
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

        if (voiceEnabled || autoSpeak) {
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

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Alert Functions
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

// Event Listeners
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
    voiceEnabledToggle.checked = voiceEnabled;
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

// Voice Control Listeners
voiceSelect.addEventListener('change', (e) => {
    selectedVoiceName = e.target.value;
    localStorage.setItem('misaka_voice_name', selectedVoiceName);
});

voiceRateSlider.addEventListener('input', (e) => {
    voiceRate = parseFloat(e.target.value);
    rateValue.textContent = voiceRate.toFixed(1);
    localStorage.setItem('misaka_voice_rate', voiceRate);
});

voicePitchSlider.addEventListener('input', (e) => {
    voicePitch = parseFloat(e.target.value);
    pitchValue.textContent = voicePitch.toFixed(1);
    localStorage.setItem('misaka_voice_pitch', voicePitch);
});

voiceEnabledToggle.addEventListener('change', (e) => {
    voiceEnabled = e.target.checked;
    localStorage.setItem('misaka_voice_enabled', voiceEnabled);
    updateVoiceButton();
});

autoSpeakToggle.addEventListener('change', (e) => {
    autoSpeak = e.target.checked;
    localStorage.setItem('misaka_auto_speak', autoSpeak);
});

btnTestVoice.addEventListener('click', testVoice);

// Initialize
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

loadStatus();
loadAlerts();
initVoiceControls();
updateVoiceButton();
updateHUDButton();
messageInput.focus();

setInterval(loadStatus, MISAKA_CONFIG.POLL_INTERVAL_MS || 15000);
setInterval(loadAlerts, MISAKA_CONFIG.ALERTS_POLL_INTERVAL_MS || 10000);