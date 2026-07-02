const API_BASE = MISAKA_CONFIG.API_BASE_URL;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const btnSend = document.getElementById('btnSend');
const btnClear = document.getElementById('btnClear');
const btnVoice = document.getElementById('btnVoice');
const btnHUD = document.getElementById('btnHUD');
const btnSettings = document.getElementById('btnSettings');
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
const btnStopVoice = document.getElementById('btnStopVoice');
const btnWakeWord = document.getElementById('btnWakeWord');
const settingsOverlay = document.getElementById('settingsOverlay');
const settingsDrawer = document.getElementById('settingsDrawer');
const btnCloseSettings = document.getElementById('btnCloseSettings');
const toastContainer = document.getElementById('toastContainer');
const modalOverlay = document.getElementById('modalOverlay');
const wakeIndicator = document.getElementById('wakeIndicator');

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
let currentAlertFilter = 'all';
let speaking = false;
let currentUtterance = null;
let pendingConfirmation = null;
let wakeWordEnabled = localStorage.getItem('misaka_wake_word') === 'true';
let wakeRecognition = null;
let compactMode = localStorage.getItem('misaka_compact_mode') === 'true';
let desktopNotificationsEnabled = localStorage.getItem('misaka_desktop_notifications') === 'true';

// ==================== Toast System ====================
function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('toast-show'));
    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ==================== Voice System ====================
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
    const femaleVoices = voices.filter(v =>
        v.name.toLowerCase().includes('female') ||
        v.name.toLowerCase().includes('feminina') ||
        v.name.toLowerCase().includes('helena') ||
        v.name.toLowerCase().includes('francisca')
    );
    const ptVoices = voices.filter(v => v.lang.includes('pt') && !v.lang.includes('pt-BR'));

    if (ptBrVoices.length > 0) {
        const og = document.createElement('optgroup');
        og.label = 'Portuguese (Brazil)';
        ptBrVoices.forEach(v => {
            const o = document.createElement('option');
            o.value = v.name;
            o.textContent = `${v.name}${v.localService ? ' (local)' : ''}`;
            if (v.name === selectedVoiceName) o.selected = true;
            og.appendChild(o);
        });
        voiceSelect.appendChild(og);
    }

    if (ptVoices.length > 0) {
        const og = document.createElement('optgroup');
        og.label = 'Portuguese';
        ptVoices.forEach(v => {
            const o = document.createElement('option');
            o.value = v.name;
            o.textContent = `${v.name}${v.localService ? ' (local)' : ''}`;
            if (v.name === selectedVoiceName) o.selected = true;
            og.appendChild(o);
        });
        voiceSelect.appendChild(og);
    }

    if (femaleVoices.length > 0 && ptBrVoices.length === 0) {
        const og = document.createElement('optgroup');
        og.label = 'Female voices';
        femaleVoices.forEach(v => {
            const o = document.createElement('option');
            o.value = v.name;
            o.textContent = `${v.name}${v.localService ? ' (local)' : ''}`;
            if (v.name === selectedVoiceName) o.selected = true;
            og.appendChild(o);
        });
        voiceSelect.appendChild(og);
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
        (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('feminina')
         || v.name.toLowerCase().includes('helena') || v.name.toLowerCase().includes('francisca'))
    );
    if (ptBrFemale) return ptBrFemale;
    const ptBr = voices.find(v => v.lang.includes('pt-BR'));
    if (ptBr) return ptBr;
    const female = voices.find(v =>
        v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('feminina')
    );
    return female || voices[0];
}

function speak(text) {
    if (!('speechSynthesis' in window)) return;
    if (!voiceEnabled && !autoSpeak) return;

    window.speechSynthesis.cancel();
    speaking = false;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = voiceRate;
    utterance.pitch = voicePitch;

    const voice = getSelectedVoice();
    if (voice) {
        utterance.voice = voice;
    }

    utterance.onstart = () => {
        speaking = true;
        setCoreState('speaking');
    };
    utterance.onend = () => {
        speaking = false;
        setCoreState(null);
    };
    utterance.onerror = (e) => {
        speaking = false;
        setCoreState(null);
        if (e.error !== 'canceled') {
            console.error('Speech error:', e.error);
        }
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

function stopVoice() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        speaking = false;
        currentUtterance = null;
        setCoreState(null);
        showToast('Voz parada.', 'info');
    }
}

function testVoice() {
    speak('Olá, eu sou a Misaka. Esta é minha voz.');
}

// ==================== UI Functions ====================
function updateVoiceButton() {
    btnVoice.style.color = voiceEnabled ? 'var(--color-primary)' : 'var(--color-muted)';
}

function updateHUDButton() {
    btnHUD.style.color = hudMode ? 'var(--color-primary)' : 'var(--color-muted)';
    document.body.classList.toggle('hud-mode', hudMode);
}

function showProviderStatus(provider, model, fallbackActive) {
    const existing = document.querySelector('.mock-warning, .gemini-active, .gemini-fallback');
    if (existing) existing.remove();

    const chatSection = document.querySelector('.chat-section');

    if (provider === 'mock') {
        const warning = document.createElement('div');
        warning.className = 'mock-warning';
        warning.textContent = 'Misaka está em modo simulação. Configure GEMINI_API_KEY para respostas inteligentes.';
        chatSection.prepend(warning);
    } else if (provider === 'gemini' && fallbackActive) {
        const fb = document.createElement('div');
        fb.className = 'gemini-fallback';
        fb.textContent = `Usando ${model} temporariamente (fallback ativo)`;
        chatSection.prepend(fb);
    } else if (provider === 'gemini') {
        const active = document.createElement('div');
        active.className = 'gemini-active';
        active.textContent = `Gemini Pro ativo — ${model}`;
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
        document.getElementById('desktopStatus').textContent = data.desktop_enabled ? 'Online' : 'Offline';
        document.getElementById('androidStatus').textContent = data.android_bridge_enabled ? 'Online' : 'Offline';

        document.getElementById('memoryModule').textContent = data.memory_enabled ? 'Active' : 'Disabled';
        document.getElementById('memoryModule').className = `module-status ${data.memory_enabled ? 'online' : ''}`;
        document.getElementById('calendarModule').textContent = data.calendar_enabled ? 'Active' : 'Disabled';
        document.getElementById('calendarModule').className = `module-status ${data.calendar_enabled ? 'online' : ''}`;
        document.getElementById('llmStatus').textContent = data.llm_provider === 'mock' ? 'Mock' : 'Active';
        document.getElementById('bridgeStatus').textContent = data.android_bridge_enabled ? 'Online' : 'Offline';
        document.getElementById('bridgeStatus').className = `module-status ${data.android_bridge_enabled ? 'online' : ''}`;

        // Fallback status
        const fallbackItem = document.getElementById('fallbackStatusItem');
        if (data.llm_fallback_active) {
            fallbackItem.style.display = 'flex';
            document.getElementById('fallbackStatus').textContent = `Active (${data.llm_model})`;
        } else {
            fallbackItem.style.display = 'none';
        }

        showProviderStatus(data.llm_provider, data.llm_model, data.llm_fallback_active);
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

    if (type === 'assistant') {
        const suffix = document.createElement('div');
        suffix.className = 'message-suffix';
        suffix.textContent = 'diz Misaka Misaka.';
        bodyDiv.appendChild(suffix);
    }

    messageDiv.appendChild(bodyDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    lastResponse = text;
}

// ==================== Chat Functions ====================
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

        // Auto speak - FIXED: always speak if enabled, not just first time
        if (voiceEnabled && autoSpeak) {
            speak(data.response);
        }

        // Show command-specific UI effects
        if (data.metadata && data.metadata.intent === 'command') {
            if (data.metadata.command === 'clear_chat') {
                setTimeout(clearChat, 500);
            }
            if (data.metadata.command === 'hud_enable') {
                hudMode = true;
                localStorage.setItem('misaka_hud_mode', 'true');
                updateHUDButton();
            }
            if (data.metadata.command === 'hud_disable') {
                hudMode = false;
                localStorage.setItem('misaka_hud_mode', 'false');
                updateHUDButton();
            }
            if (data.metadata.command === 'voice_enable') {
                voiceEnabled = true;
                localStorage.setItem('misaka_voice_enabled', 'true');
                voiceEnabledToggle.checked = true;
                updateVoiceButton();
            }
            if (data.metadata.command === 'voice_disable') {
                voiceEnabled = false;
                localStorage.setItem('misaka_voice_enabled', 'false');
                voiceEnabledToggle.checked = false;
                updateVoiceButton();
            }
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
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado!', 'success');
    }).catch(() => {
        showToast('Erro ao copiar.', 'error');
    });
}

// ==================== Alert Functions ====================
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

            let filtered = data.alerts;
            if (currentAlertFilter !== 'all') {
                if (currentAlertFilter === 'pending') {
                    filtered = data.alerts.filter(a => a.status === 'pending');
                } else {
                    filtered = data.alerts.filter(a => a.priority === currentAlertFilter);
                }
            }

            filtered.slice(0, 10).forEach(alert => {
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

                if (alert.status === 'pending') {
                    const ackBtn = document.createElement('button');
                    ackBtn.className = 'btn-alert-ack';
                    ackBtn.textContent = '✓';
                    ackBtn.title = 'Mark as seen';
                    ackBtn.onclick = async (e) => {
                        e.stopPropagation();
                        try {
                            await fetch(`${API_BASE}/notifications/alerts/${alert.id}/ack`, { method: 'POST' });
                            loadAlerts();
                            showToast('Alerta marcado como visto.', 'success');
                        } catch (err) {
                            showToast('Erro ao marcar alerta.', 'error');
                        }
                    };
                    alertDiv.appendChild(ackBtn);
                }

                alertsContainer.appendChild(alertDiv);

                if (!pendingAlertIds.includes(alert.id)) {
                    pendingAlertIds.push(alert.id);
                    if (desktopNotificationsEnabled && Notification.permission === 'granted') {
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

async function ackAllAlerts() {
    try {
        const response = await fetch(`${API_BASE}/notifications/alerts/ack-all`, { method: 'POST' });
        const data = await response.json();
        showToast(data.message || 'Alertas marcados como vistos.', 'success');
        loadAlerts();
    } catch (error) {
        showToast('Erro ao limpar alertas.', 'error');
    }
}

// ==================== Settings ====================
function openSettings() {
    settingsOverlay.classList.add('active');
    settingsDrawer.classList.add('active');
    loadSettingsInfo();
}

function closeSettings() {
    settingsOverlay.classList.remove('active');
    settingsDrawer.classList.remove('active');
}

async function loadSettingsInfo() {
    try {
        const response = await fetch(`${API_BASE}/llm/status`);
        const data = await response.json();
        const info = document.getElementById('settingsLLMInfo');
        info.innerHTML = `
            <div class="settings-info-row"><span>Provider:</span><span>${data.provider}</span></div>
            <div class="settings-info-row"><span>Active model:</span><span>${data.active_model || '-'}</span></div>
            <div class="settings-info-row"><span>Primary:</span><span>${data.primary_model || '-'}</span></div>
            <div class="settings-info-row"><span>Fallback:</span><span>${data.fallback_model || '-'}</span></div>
            <div class="settings-info-row"><span>Configured:</span><span>${data.gemini_configured ? 'Yes' : 'No'}</span></div>
            ${data.last_error_type ? `<div class="settings-info-row warning"><span>Last error:</span><span>${data.last_error_type}</span></div>` : ''}
        `;
    } catch (e) {
        document.getElementById('settingsLLMInfo').textContent = 'Failed to load';
    }

    // Desktop info
    const desktopInfo = document.getElementById('settingsDesktopInfo');
    if (window.misakaDesktop && window.misakaDesktop.isAvailable) {
        desktopInfo.innerHTML = '<span class="online">Desktop bridge available</span>';
    } else {
        desktopInfo.innerHTML = '<span>Web mode (no desktop bridge)</span>';
    }

    // Android info
    try {
        const response = await fetch(`${API_BASE}/android/status`);
        const data = await response.json();
        const androidInfo = document.getElementById('settingsAndroidInfo');
        if (data.enabled) {
            androidInfo.innerHTML = `
                <span class="${data.connected ? 'online' : ''}">${data.connected ? 'Connected' : 'Disconnected'}</span>
                <span>${data.pending_actions} pending actions</span>
            `;
        } else {
            androidInfo.innerHTML = '<span>Not configured</span>';
        }
    } catch (e) {
        document.getElementById('settingsAndroidInfo').textContent = 'Failed to load';
    }
}

// ==================== Wake Word ====================
function initWakeWord() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        btnWakeWord.style.display = 'none';
        return;
    }

    if (!wakeWordEnabled) return;

    startWakeWord();
}

function startWakeWord() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    wakeRecognition = new SpeechRecognition();
    wakeRecognition.continuous = true;
    wakeRecognition.interimResults = true;
    wakeRecognition.lang = 'pt-BR';

    let wakeDetected = false;

    wakeRecognition.onresult = (event) => {
        const last = event.results[event.results.length - 1];
        const transcript = last[0].transcript.toLowerCase().trim();

        if (!wakeDetected) {
            if (transcript.includes('misaka')) {
                wakeDetected = true;
                wakeIndicator.style.display = 'flex';
                setCoreState('thinking');
                showToast('Wake word detected! Fale seu comando.', 'info');

                setTimeout(() => {
                    wakeDetected = false;
                }, 5000);
            }
        } else if (last.isFinal) {
            const command = transcript.replace(/(?:ei\s+|ok\s+)?misaka\s*/i, '').trim();
            if (command) {
                messageInput.value = command;
                sendMessage();
            }
            wakeDetected = false;
            wakeIndicator.style.display = 'none';
            setCoreState(null);
        }
    };

    wakeRecognition.onerror = (event) => {
        if (event.error !== 'no-speech') {
            console.error('Wake word error:', event.error);
        }
    };

    wakeRecognition.onend = () => {
        if (wakeWordEnabled) {
            try { wakeRecognition.start(); } catch (e) {}
        }
    };

    try {
        wakeRecognition.start();
    } catch (e) {
        console.error('Failed to start wake word:', e);
    }
}

function stopWakeWord() {
    if (wakeRecognition) {
        wakeRecognition.onend = null;
        wakeRecognition.stop();
        wakeRecognition = null;
    }
    wakeIndicator.style.display = 'none';
}

// ==================== Confirmation Modal ====================
function showConfirmation(title, message, payload) {
    modalOverlay.style.display = 'flex';
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalMessage').textContent = message;
    pendingConfirmation = payload;
}

function hideConfirmation() {
    modalOverlay.style.display = 'none';
    pendingConfirmation = null;
}

// ==================== Event Listeners ====================
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
    showToast(voiceEnabled ? 'Voz ativada.' : 'Voz desativada.', 'info');
});

btnHUD.addEventListener('click', () => {
    hudMode = !hudMode;
    localStorage.setItem('misaka_hud_mode', hudMode);
    updateHUDButton();
    showToast(hudMode ? 'HUD ativado.' : 'HUD desativado.', 'info');
});

btnCopyLast.addEventListener('click', () => {
    if (lastResponse) copyToClipboard(lastResponse);
});

btnSpeakLast.addEventListener('click', () => {
    if (lastResponse) speak(lastResponse);
});

btnTestVoice.addEventListener('click', testVoice);
btnStopVoice.addEventListener('click', stopVoice);

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

// Settings listeners
btnSettings.addEventListener('click', openSettings);
btnCloseSettings.addEventListener('click', closeSettings);
settingsOverlay.addEventListener('click', closeSettings);

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeSettings();
        hideConfirmation();
    }
});

// Alert filters
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentAlertFilter = btn.dataset.filter;
        loadAlerts();
    });
});

document.getElementById('btnAckAll').addEventListener('click', ackAllAlerts);
document.getElementById('btnRefreshAlerts').addEventListener('click', loadAlerts);

// Wake word
btnWakeWord.addEventListener('click', () => {
    wakeWordEnabled = !wakeWordEnabled;
    localStorage.setItem('misaka_wake_word', wakeWordEnabled);
    if (wakeWordEnabled) {
        startWakeWord();
        showToast('Wake word ativado. Diga "Misaka" para acionar.', 'info');
    } else {
        stopWakeWord();
        showToast('Wake word desativado.', 'info');
    }
    btnWakeWord.style.color = wakeWordEnabled ? 'var(--color-primary)' : 'var(--color-muted)';
});

// Settings toggles
document.getElementById('speakSuffixToggle').addEventListener('change', (e) => {
    localStorage.setItem('misaka_speak_suffix', e.target.checked);
});

document.getElementById('desktopNotificationsToggle').addEventListener('change', (e) => {
    desktopNotificationsEnabled = e.target.checked;
    localStorage.setItem('misaka_desktop_notifications', desktopNotificationsEnabled);
    if (desktopNotificationsEnabled && 'Notification' in window) {
        Notification.requestPermission();
    }
});

document.getElementById('settingsHUDToggle').addEventListener('change', (e) => {
    hudMode = e.target.checked;
    localStorage.setItem('misaka_hud_mode', hudMode);
    updateHUDButton();
});

document.getElementById('compactModeToggle').addEventListener('change', (e) => {
    compactMode = e.target.checked;
    localStorage.setItem('misaka_compact_mode', compactMode);
    document.body.classList.toggle('compact-mode', compactMode);
});

document.getElementById('wakeWordToggle').addEventListener('change', (e) => {
    wakeWordEnabled = e.target.checked;
    localStorage.setItem('misaka_wake_word', wakeWordEnabled);
    if (wakeWordEnabled) {
        startWakeWord();
    } else {
        stopWakeWord();
    }
});

document.getElementById('btnClearAllData').addEventListener('click', () => {
    if (confirm('Tem certeza? Isso vai limpar todos os dados locais.')) {
        localStorage.clear();
        showToast('Dados locais limpos.', 'success');
        location.reload();
    }
});

// Modal listeners
document.getElementById('btnModalApprove').addEventListener('click', () => {
    if (pendingConfirmation) {
        showToast('Ação aprovada.', 'success');
    }
    hideConfirmation();
});

document.getElementById('btnModalDeny').addEventListener('click', () => {
    hideConfirmation();
    showToast('Ação negada.', 'info');
});

modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) hideConfirmation();
});

// ==================== Initialize ====================
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Load saved settings
document.getElementById('speakSuffixToggle').checked = localStorage.getItem('misaka_speak_suffix') !== 'false';
document.getElementById('desktopNotificationsToggle').checked = desktopNotificationsEnabled;
document.getElementById('settingsHUDToggle').checked = hudMode;
document.getElementById('compactModeToggle').checked = compactMode;
document.getElementById('wakeWordToggle').checked = wakeWordEnabled;
if (compactMode) document.body.classList.add('compact-mode');
if (hudMode) document.body.classList.add('hud-mode');

loadStatus();
loadAlerts();
initVoiceControls();
updateVoiceButton();
updateHUDButton();
messageInput.focus();
if (wakeWordEnabled) initWakeWord();

// Update wake word button color
btnWakeWord.style.color = wakeWordEnabled ? 'var(--color-primary)' : 'var(--color-muted)';

setInterval(loadStatus, MISAKA_CONFIG.POLL_INTERVAL_MS || 15000);
setInterval(loadAlerts, MISAKA_CONFIG.ALERTS_POLL_INTERVAL_MS || 10000);
