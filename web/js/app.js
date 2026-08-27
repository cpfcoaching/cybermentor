/**
 * CyberMentor — Frontend Application
 *
 * Handles: onboarding, SSE chat streaming, markdown rendering,
 * progress sidebar, and quick action shortcuts.
 */

'use strict';

// ── Config ────────────────────────────────────────────────────────────────
const API_BASE_URL = window.CYBERMENTOR_API_URL || (window.location.protocol.startsWith('http') && !window.location.host.includes('localhost') && !window.location.host.includes('127.0.0.1') ? window.location.origin : 'http://localhost:8080');

// ── State ─────────────────────────────────────────────────────────────────
let currentUser = null;
let sessionId   = null;
let isStreaming  = false;

// ── DOM References ────────────────────────────────────────────────────────
const onboardingOverlay = document.getElementById('onboarding-overlay');
const usernameInput     = document.getElementById('username-input');
const startBtn          = document.getElementById('start-btn');
const appLayout         = document.getElementById('app');
const messagesEl        = document.getElementById('messages');
const messageInput      = document.getElementById('message-input');
const sendBtn           = document.getElementById('send-btn');
const clearBtn          = document.getElementById('clear-btn');
const sidebarUsername   = document.getElementById('sidebar-username');
const userAvatar        = document.getElementById('user-avatar');
const statusDot         = document.getElementById('status-dot');
const statusText        = document.getElementById('status-text');
const progressList      = document.getElementById('progress-list');

// ── Onboarding ────────────────────────────────────────────────────────────
usernameInput.addEventListener('input', () => {
  const val = usernameInput.value.trim();
  startBtn.disabled = val.length < 2;
});

usernameInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !startBtn.disabled) startSession();
});

startBtn.addEventListener('click', startSession);

function startSession() {
  const username = usernameInput.value.trim().replace(/[^a-zA-Z0-9_-]/g, '');
  if (!username) return;

  currentUser = username;
  sessionId   = null;

  // Persist user for next visit
  localStorage.setItem('cybermentor_user', username);

  // Update UI
  sidebarUsername.textContent = username;
  userAvatar.textContent      = username.slice(0, 2).toUpperCase();

  // Show app, hide onboarding
  onboardingOverlay.classList.remove('active');
  appLayout.classList.remove('hidden');

  // Show welcome message
  addAgentMessage(getWelcomeMessage(username));

  // Load progress
  loadProgress(username);

  // Focus input
  setTimeout(() => messageInput.focus(), 300);
}

// Restore session from localStorage
window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('cybermentor_user');
  if (saved) {
    usernameInput.value = saved;
    startBtn.disabled = false;
  }
});

function getWelcomeMessage(name) {
  return `🛡️ **Welcome back, ${name}!**

I'm CyberMentor — your AI-powered career coach for breaking into cybersecurity.

Here's what I can help you with today:

- **🗺️ Career Path** — Figure out which cybersecurity role is right for you
- **📅 Study Plan** — Get a personalized week-by-week cert study schedule  
- **📄 Resume Review** — Identify gaps and strengthen your resume
- **🎤 Interview Prep** — Practice with real interview questions and get scored feedback

What would you like to work on today? Or if you're new, just tell me a bit about your background and I'll guide you from there.`;
}

// ── Chat ──────────────────────────────────────────────────────────────────
messageInput.addEventListener('input', () => {
  // Auto-resize textarea
  messageInput.style.height = 'auto';
  messageInput.style.height = Math.min(messageInput.scrollHeight, 180) + 'px';

  sendBtn.disabled = messageInput.value.trim().length === 0 || isStreaming;
});

messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) sendMessage();
  }
});

sendBtn.addEventListener('click', sendMessage);

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text || isStreaming) return;

  // Add user message
  addUserMessage(text);

  // Clear input
  messageInput.value = '';
  messageInput.style.height = 'auto';
  sendBtn.disabled = true;

  // Stream response
  await streamAgentResponse(text);
}

async function streamAgentResponse(userMessage) {
  isStreaming = true;
  setStatus('thinking', 'CyberMentor is thinking...');

  // Show typing indicator
  const typingEl = addTypingIndicator();

  let agentEl = null;
  let rawText  = '';

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id:    currentUser,
        message:    userMessage,
        session_id: sessionId || undefined,
      }),
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);

    // Remove typing indicator once first chunk arrives
    let firstChunk = true;

    const reader  = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const dataStr = line.slice(6).trim();
        if (!dataStr) continue;

        try {
          const data = JSON.parse(dataStr);

          if (data.error) {
            typingEl.remove();
            addAgentMessage(`❌ **Error:** ${data.error}\n\nPlease try again.`);
            break;
          }

          if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem('cybermentor_session_' + currentUser, sessionId);
          }

          if (data.done) break;

          if (data.token) {
            if (firstChunk) {
              typingEl.remove();
              agentEl = createStreamingMessage();
              firstChunk = false;
            }
            rawText += data.token;
            updateStreamingMessage(agentEl, rawText);
          }
        } catch (_) {
          // Non-JSON line, skip
        }
      }
    }

    // Finalize with full markdown render
    if (agentEl) {
      finalizeStreamingMessage(agentEl, rawText);
    }

    // Reload progress after message (agent may have saved a milestone)
    setTimeout(() => loadProgress(currentUser), 1500);

  } catch (err) {
    typingEl.remove();
    addAgentMessage(
      `❌ **Connection Error**\n\nI couldn't reach the CyberMentor backend. ` +
      `Make sure the API server is running at \`${API_BASE_URL}\`.\n\n` +
      `Error: ${err.message}`
    );
  } finally {
    isStreaming = false;
    setStatus('ready', 'CyberMentor Ready');
    sendBtn.disabled = messageInput.value.trim().length === 0;
    scrollToBottom();
  }
}

// ── Quick Actions ─────────────────────────────────────────────────────────
document.querySelectorAll('.quick-action-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const prompt = btn.dataset.prompt;
    if (prompt && !isStreaming) {
      messageInput.value = prompt;
      messageInput.dispatchEvent(new Event('input'));
      sendMessage();
    }
  });
});

// ── Clear ─────────────────────────────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  messagesEl.innerHTML = '';
  sessionId = null;
  localStorage.removeItem('cybermentor_session_' + currentUser);
  addAgentMessage(getWelcomeMessage(currentUser));
});

// ── Progress Sidebar ──────────────────────────────────────────────────────
async function loadProgress(userId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(userId)}`);
    if (!res.ok) return;
    const data = await res.json();

    if (data.milestones && data.milestones.length > 0) {
      progressList.innerHTML = '';
      // Show last 10 in reverse order (most recent first)
      const recent = [...data.milestones].reverse().slice(0, 10);
      for (const m of recent) {
        const date = m.timestamp ? m.timestamp.slice(0, 10) : '';
        const el   = document.createElement('div');
        el.className = 'milestone-item';
        el.innerHTML = `
          <div>${escapeHtml(m.milestone)}</div>
          <div class="milestone-date">${date}</div>
        `;
        progressList.appendChild(el);
      }
    }
  } catch (_) {
    // Progress endpoint may not be reachable locally — that's fine
  }
}

// ── Message Helpers ───────────────────────────────────────────────────────
function addUserMessage(text) {
  const el = document.createElement('div');
  el.className = 'message user';
  el.setAttribute('role', 'listitem');
  el.innerHTML = `
    <div class="message-avatar" aria-hidden="true">${currentUser ? currentUser.slice(0,2).toUpperCase() : 'ME'}</div>
    <div class="message-bubble">${escapeHtml(text).replace(/\n/g, '<br>')}</div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
}

function addAgentMessage(markdown) {
  const el = document.createElement('div');
  el.className = 'message agent';
  el.setAttribute('role', 'listitem');
  el.innerHTML = `
    <div class="message-avatar" aria-label="CyberMentor">🛡️</div>
    <div class="message-bubble">${renderMarkdown(markdown)}</div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
  return el;
}

function addTypingIndicator() {
  const el = document.createElement('div');
  el.className = 'message agent';
  el.innerHTML = `
    <div class="message-avatar" aria-hidden="true">🛡️</div>
    <div class="message-bubble">
      <div class="typing-indicator" aria-label="CyberMentor is typing">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
  return el;
}

function createStreamingMessage() {
  const el = document.createElement('div');
  el.className = 'message agent';
  el.setAttribute('role', 'listitem');
  el.innerHTML = `
    <div class="message-avatar" aria-hidden="true">🛡️</div>
    <div class="message-bubble streaming"></div>
  `;
  messagesEl.appendChild(el);
  return el;
}

function updateStreamingMessage(el, text) {
  const bubble = el.querySelector('.message-bubble');
  // Show plain text during streaming for performance
  bubble.textContent = text;
  scrollToBottom();
}

function finalizeStreamingMessage(el, markdown) {
  const bubble = el.querySelector('.message-bubble');
  bubble.classList.remove('streaming');
  bubble.innerHTML = renderMarkdown(markdown);
  scrollToBottom();
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatus(state, text) {
  statusDot.className  = 'status-dot' + (state === 'thinking' ? ' thinking' : '');
  statusText.textContent = text;
}

// ── Markdown Renderer (lightweight) ──────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return '';

  let html = escapeHtml(text);

  // Code blocks (must come before inline code)
  html = html.replace(/```[\w]*\n?([\s\S]*?)```/g, (_, code) =>
    `<pre><code>${code.trim()}</code></pre>`
  );

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>');

  // Bold and italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Horizontal rule
  html = html.replace(/^---+$/gm, '<hr>');

  // Checkboxes
  html = html.replace(/- \[ \] (.+)/g, '<li>☐ $1</li>');
  html = html.replace(/- \[x\] (.+)/gi, '<li>☑ $1</li>');

  // Unordered lists
  html = html.replace(/^[\*\-•] (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`);

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Paragraphs (double newlines → paragraphs)
  html = html.split(/\n\n+/).map(block => {
    if (block.startsWith('<h') || block.startsWith('<ul') ||
        block.startsWith('<ol') || block.startsWith('<pre') ||
        block.startsWith('<hr')) {
      return block;
    }
    return `<p>${block.replace(/\n/g, '<br>')}</p>`;
  }).join('\n');

  return html;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
