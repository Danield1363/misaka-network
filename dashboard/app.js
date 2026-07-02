const API_BASE = MISAKA_CONFIG.API_BASE_URL;

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const btnSend = document.getElementById('btnSend');
const btnClear = document.getElementById('btnClear');
const typingIndicator = document.getElementById('typingIndicator');

let conversationId = null;

async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        document.getElementById('version').textContent = `v${data.version}`;
        document.getElementById('llmProvider').textContent = data.llm_provider;
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

function addMessage(text, type, suffix = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    messageDiv.appendChild(contentDiv);
    
    if (suffix) {
        const suffixDiv = document.createElement('div');
        suffixDiv.className = 'message-suffix';
        suffixDiv.textContent = suffix;
        messageDiv.appendChild(suffixDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    messageInput.value = '';
    
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
        
        addMessage(data.response, 'assistant', 'diz Misaka Misaka.');
    } catch (error) {
        addMessage('Erro ao conectar com o servidor.', 'system');
    } finally {
        typingIndicator.classList.remove('active');
        btnSend.disabled = false;
        messageInput.focus();
    }
}

function clearChat() {
    chatMessages.innerHTML = '';
    conversationId = null;
    addMessage('Conversa reiniciada. Como posso ajudar?', 'system', 'diz Misaka Misaka.');
}

btnSend.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
btnClear.addEventListener('click', clearChat);

loadStatus();
messageInput.focus();