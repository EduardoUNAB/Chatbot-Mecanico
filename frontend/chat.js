/* MecánicaBot · Frontend logic */

const messagesEl = document.getElementById('messages');
const formEl = document.getElementById('chat-form');
const inputEl = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

// ---------------- Health ----------------

async function refreshHealth() {
    try {
        const r = await fetch('/health');
        const data = await r.json();
        toggleStatus('status-ollama', data.ollama_ok);
        toggleStatus('status-rag', data.rag_ok);
        document.getElementById('status-chunks').textContent = data.indexed_chunks;
        document.getElementById('model-tag').textContent = data.model;
    } catch (e) {
        toggleStatus('status-ollama', false);
        toggleStatus('status-rag', false);
    }
}

function toggleStatus(id, ok) {
    const el = document.getElementById(id);
    el.classList.remove('online', 'offline');
    el.classList.add(ok ? 'online' : 'offline');
}

// ---------------- Render ----------------

function renderUser(text) {
    const div = document.createElement('div');
    div.className = 'msg msg-user';
    div.innerHTML = `<div class="bubble"></div>`;
    div.querySelector('.bubble').textContent = text;
    messagesEl.appendChild(div);
    scrollDown();
}

function renderBotPlaceholder() {
    const div = document.createElement('div');
    div.className = 'msg msg-bot';
    div.innerHTML = `
        <div class="bubble">
            <div class="bot-tag">MECÁNICABOT</div>
            <div class="content"><div class="typing"><span></span><span></span><span></span></div></div>
        </div>
    `;
    messagesEl.appendChild(div);
    scrollDown();
    return div;
}

function fillBot(div, answer, sources, elapsedMs) {
    const content = div.querySelector('.content');
    content.innerHTML = '';
    content.textContent = answer;

    if (sources && sources.length) {
        const srcEl = document.createElement('div');
        srcEl.className = 'sources';
        const unique = [...new Set(sources.map(s => s.source))];
        srcEl.innerHTML = `<strong>FUENTES:</strong> ` +
            unique.map(s => `<span class="src-pill">${escapeHtml(s)}</span>`).join('') +
            ` <span style="float:right">${elapsedMs} ms</span>`;
        div.querySelector('.bubble').appendChild(srcEl);
    }
    scrollDown();
}

function fillBotError(div, message) {
    const content = div.querySelector('.content');
    content.innerHTML = '';
    content.style.color = 'var(--signal-red)';
    content.textContent = `⚠ ${message}`;
}

function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}

function scrollDown() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function clearWelcome() {
    const w = messagesEl.querySelector('.welcome');
    if (w) w.remove();
}

// ---------------- Send ----------------

async function sendMessage(text) {
    if (!text.trim()) return;

    clearWelcome();
    renderUser(text);
    const placeholder = renderBotPlaceholder();
    sendBtn.disabled = true;

    try {
        const r = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });
        if (!r.ok) {
            const err = await r.json().catch(() => ({detail: 'Error desconocido'}));
            fillBotError(placeholder, err.detail || `HTTP ${r.status}`);
            return;
        }
        const data = await r.json();
        fillBot(placeholder, data.answer, data.sources, data.elapsed_ms);
    } catch (e) {
        fillBotError(placeholder, `Error de red: ${e.message}`);
    } finally {
        sendBtn.disabled = false;
        inputEl.focus();
    }
}

// ---------------- Event listeners ----------------

formEl.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = '';
    sendMessage(text);
});

document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
        sendMessage(chip.dataset.query);
    });
});

// Init
refreshHealth();
setInterval(refreshHealth, 30000);
inputEl.focus();
