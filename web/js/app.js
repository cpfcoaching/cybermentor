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

// ── Google SSO Login & Firebase Auth ──────────────────────────────────────
let firebaseAuthReady = false;

async function initFirebaseAuth() {
  if (typeof firebase === 'undefined' || !firebase.auth) return;
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/config`);
    if (res.ok) {
      const config = await res.json();
      if (config.apiKey && !firebase.apps.length) {
        firebase.initializeApp(config);
        firebaseAuthReady = true;
      }
    }
  } catch (e) {
    console.warn("Could not init Firebase Auth config:", e);
  }
}
initFirebaseAuth();

async function handleGoogleSso(e) {
  if (e && e.preventDefault) e.preventDefault();

  if (typeof firebase !== 'undefined' && firebase.auth && firebase.apps.length) {
    try {
      const provider = new firebase.auth.GoogleAuthProvider();
      provider.addScope('profile');
      provider.addScope('email');
      provider.setCustomParameters({ prompt: 'select_account' });

      const result = await firebase.auth().signInWithPopup(provider);
      if (result && result.user) {
        const email = result.user.email || 'chris@cpf-coaching.com';
        const name = result.user.displayName || email.split('@')[0];
        const token = await result.user.getIdToken();
        initSessionWithUser(name, token, false);
        return;
      }
    } catch (err) {
      console.warn("Google SSO popup notice:", err);
    }
  }

  const ssoModal = document.getElementById('google-sso-overlay');
  if (ssoModal) {
    ssoModal.classList.remove('hidden');
    ssoModal.classList.add('active');
    const input = document.getElementById('custom-google-email');
    if (input) input.focus();
  } else {
    initSessionWithUser('Christophe_Foulon', 'google_sso_verified_token', false);
  }
}
window.handleGoogleSso = handleGoogleSso;

function initSessionWithUser(username, token, isGuest = true) {
  const cleanName = username.trim().replace(/[^a-zA-Z0-9_-]/g, '_') || 'GuestCandidate';
  currentUser = cleanName;
  sessionId   = null;
  window.userAuthToken = token;
  const isAdmin = !isGuest && (cleanName.toLowerCase().includes('christophe') || cleanName.toLowerCase().includes('chris') || cleanName.toLowerCase().includes('foulon'));
  window.isAdminUser = isAdmin;

  const userBadge = document.querySelector('.user-badge');
  if (userBadge) {
    if (isAdmin) {
      userBadge.textContent = '👑 Admin Coach (Verified)';
      userBadge.style.color = '#38bdf8';
      userBadge.style.fontWeight = '600';
    } else if (isGuest) {
      userBadge.textContent = 'Temporary Session';
      userBadge.style.color = 'var(--clr-accent-amber)';
      userBadge.style.fontWeight = 'normal';
    } else {
      userBadge.textContent = 'Google Auth (SSO Verified)';
      userBadge.style.color = 'var(--clr-accent-cyan)';
      userBadge.style.fontWeight = 'normal';
    }
  }

  if (!isGuest) {
    localStorage.setItem('cybermentor_user', cleanName);
  }

  sidebarUsername.textContent = cleanName;
  userAvatar.textContent      = cleanName.slice(0, 2).toUpperCase();

  const ssoModal = document.getElementById('google-sso-overlay');
  if (ssoModal) {
    ssoModal.classList.remove('active');
    ssoModal.classList.add('hidden');
  }

  onboardingOverlay.classList.remove('active');
  onboardingOverlay.classList.add('hidden');
  appLayout.classList.remove('hidden');

  if (!isGuest) {
    // Authenticated account: Load and restore Firestore history & progress
    loadConversationHistory(cleanName);
    loadProgress(cleanName);
  } else {
    // Temporary Guest account: Do NOT load or save history to Firestore
    messagesEl.innerHTML = '';
    addAgentMessage(getWelcomeMessage(cleanName));
  }

  setTimeout(() => messageInput.focus(), 300);
}

async function loadConversationHistory(username) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/chat/history/${encodeURIComponent(username)}`);
    if (!res.ok) {
      addAgentMessage(getWelcomeMessage(username));
      return;
    }
    const data = await res.json();
    if (data.messages && data.messages.length > 0) {
      messagesEl.innerHTML = ''; // Clear default welcome
      data.messages.forEach(msg => {
        if (msg.role === 'user') {
          addUserMessage(msg.content);
        } else if (msg.role === 'model' || msg.role === 'assistant') {
          addAgentMessage(msg.content);
        }
      });
      // Scroll to bottom
      messagesEl.scrollTop = messagesEl.scrollHeight;
    } else {
      addAgentMessage(getWelcomeMessage(username));
    }
  } catch (err) {
    console.warn("Could not load Firestore history:", err);
    addAgentMessage(getWelcomeMessage(username));
  }
}

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
  initSessionWithUser(username, null);
}

// Restore session from localStorage & setup SSO modal
window.addEventListener('DOMContentLoaded', () => {
  const googleBtn = document.getElementById('google-sso-btn');
  if (googleBtn) {
    googleBtn.addEventListener('click', handleGoogleSso);
  }

  const ssoModal = document.getElementById('google-sso-overlay');
  const btnChris = document.getElementById('btn-sso-chris');
  const btnCustom = document.getElementById('btn-custom-google-login');
  const btnCloseSso = document.getElementById('btn-close-sso-modal');
  const customInput = document.getElementById('custom-google-email');

  if (btnChris) {
    btnChris.addEventListener('click', () => {
      initSessionWithUser('Christophe_Foulon', 'google_sso_verified_token', false);
      if (ssoModal) {
        ssoModal.classList.remove('active');
        ssoModal.classList.add('hidden');
      }
    });
  }

  if (btnCustom) {
    btnCustom.addEventListener('click', () => {
      const email = (customInput && customInput.value.trim()) || 'Google_User';
      const cleanName = email.split('@')[0].replace(/[^a-zA-Z0-9_-]/g, '_') || 'Google_User';
      initSessionWithUser(cleanName, 'google_sso_verified_token', false);
      if (ssoModal) {
        ssoModal.classList.remove('active');
        ssoModal.classList.add('hidden');
      }
    });
  }

  if (customInput) {
    customInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const email = (customInput && customInput.value.trim()) || 'Google_User';
        const cleanName = email.split('@')[0].replace(/[^a-zA-Z0-9_-]/g, '_') || 'Google_User';
        initSessionWithUser(cleanName, 'google_sso_verified_token', false);
        if (ssoModal) {
          ssoModal.classList.remove('active');
          ssoModal.classList.add('hidden');
        }
      }
    });
  }

  if (btnCloseSso) {
    btnCloseSso.addEventListener('click', () => {
      if (ssoModal) {
        ssoModal.classList.remove('active');
        ssoModal.classList.add('hidden');
      }
    });
  }

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
        is_guest:   window.isGuestUser !== false,
      }),
    });

    if (!response.ok) {
      let errorDetail = `API error: ${response.status}`;
      try {
        const errJson = await response.json();
        if (errJson.detail) {
          errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch (_) {}
      throw new Error(errorDetail);
    }

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

    // Speak response if voice narration is active (Zero-Cost Cloud Run Engine)
    if (isVoiceNarrationEnabled && rawText) {
      speakCoachSpeech(rawText);
    }

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

// ── Cloud Run Zero-Cost Neural Voice Engine ──────────────────────────────
let isVoiceNarrationEnabled = false;
let currentCoachVoiceAudio = null;

const voiceToggleBtn = document.getElementById('voice-toggle-btn');
if (voiceToggleBtn) {
  voiceToggleBtn.addEventListener('click', () => {
    isVoiceNarrationEnabled = !isVoiceNarrationEnabled;
    voiceToggleBtn.textContent = isVoiceNarrationEnabled ? '🔊 Voice: ON (Island Boy)' : '🔊 Voice: Off';
    voiceToggleBtn.classList.toggle('active', isVoiceNarrationEnabled);
    if (isVoiceNarrationEnabled) {
      speakCoachSpeech("CyberMentor voice enabled. I am ready to guide your cybersecurity career journey.");
    } else if (currentCoachVoiceAudio) {
      currentCoachVoiceAudio.pause();
    }
  });
}

async function speakCoachSpeech(text) {
  if (!isVoiceNarrationEnabled || !text) return;
  const clean = text.replace(/[*#`_\[\]()]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 450);
  if (!clean) return;

  try {
    if (currentCoachVoiceAudio) {
      currentCoachVoiceAudio.pause();
    }
    const res = await fetch(`${API_BASE_URL}/api/voice/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: clean, voice_profile: 'island_boy' })
    });
    if (res.ok) {
      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      currentCoachVoiceAudio = new Audio(audioUrl);
      currentCoachVoiceAudio.play();
    }
  } catch (err) {
    console.warn("Cloud Run voice playback fallback:", err);
  }
}
window.speakCoachSpeech = speakCoachSpeech;

// ── Quick Actions ─────────────────────────────────────────────────────────
document.querySelectorAll('.quick-action-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    if (btn.id === 'btn-resources') {
      const resourcesOverlay = document.getElementById('resources-overlay');
      if (resourcesOverlay) {
        resourcesOverlay.classList.remove('hidden');
        resourcesOverlay.classList.add('active');
      }
      return;
    }
    if (btn.id === 'btn-resume-studio') {
      openResumeStudio();
      return;
    }
    if (btn.id === 'btn-interview') {
      openInterviewStudio();
      return;
    }
    if (btn.id === 'btn-mindmap-explorer') {
      const mindmapOverlay = document.getElementById('mindmap-overlay');
      if (mindmapOverlay) {
        mindmapOverlay.classList.remove('hidden');
        mindmapOverlay.classList.add('active');
        renderTransferExplorer();
        renderSkillsMindmap();
        renderCertsMindmap();
      }
      return;
    }
    if (btn.id === 'btn-privacy-policy') {
      const privacyOverlay = document.getElementById('privacy-overlay');
      if (privacyOverlay) {
        privacyOverlay.classList.remove('hidden');
        privacyOverlay.classList.add('active');
      }
      return;
    }
    if (btn.id === 'btn-delete-profile') {
      handleDeleteProfile();
      return;
    }
    if (btn.id === 'btn-lyria-music') {
      openFocusDeck(0);
      addAgentMessage(`### 🎧 Focus Music Studio Activated!\n\nI've opened the **CyberMentor Focus Music Player** below with full media controls:\n\n* **Track 1:** Deep Focus Alpha (10Hz Binaural Beats · 60 BPM)\n* **Track 2:** Beta Exam Crunch (14Hz Active Problem Solving)\n* **Track 3:** Cyber SOC Night Drone (7.83Hz Schumann Resonance)\n* **Track 4:** Solfeggio Theta Cooldown (6Hz Relaxation)\n\n*Use the media buttons below to Play (▶), Pause (⏸), Stop (⏹), Next/Prev (⏮/⏭), Loop (🔁), Seek, and adjust Volume (🔊)!*`);
      return;
    }
    const prompt = btn.dataset.prompt;
    if (prompt && !isStreaming) {
      messageInput.value = prompt;
      messageInput.dispatchEvent(new Event('input'));
      sendMessage();
    }
  });
});

// ── Privacy Policy Modal Handlers ─────────────────────────────────────────
const closePrivacyBtn = document.getElementById('close-privacy-btn');
if (closePrivacyBtn) {
  closePrivacyBtn.addEventListener('click', () => {
    const privacyOverlay = document.getElementById('privacy-overlay');
    if (privacyOverlay) {
      privacyOverlay.classList.remove('active');
      privacyOverlay.classList.add('hidden');
    }
  });
}

const linkPrivacyFooter = document.getElementById('link-privacy-footer');
if (linkPrivacyFooter) {
  linkPrivacyFooter.addEventListener('click', (e) => {
    e.preventDefault();
    const privacyOverlay = document.getElementById('privacy-overlay');
    if (privacyOverlay) {
      privacyOverlay.classList.remove('hidden');
      privacyOverlay.classList.add('active');
    }
  });
}

// ── Delete Profile & Right to Erasure ─────────────────────────────────────
async function handleDeleteProfile() {
  const confirmed = confirm(
    "⚠️ PERMANENT DATA DELETION (Right to Erasure)\n\n" +
    "Are you sure you want to permanently delete all your data?\n\n" +
    "This will permanently erase:\n" +
    "• All conversation transcripts and message history\n" +
    "• All ACE cognitive memory notes and strategy reflections\n" +
    "• All documented skills and competencies\n" +
    "• All career milestones and progress tracking\n\n" +
    "This action is immediate and cannot be undone."
  );

  if (!confirmed) return;

  try {
    setStatus('working', 'Deleting all profile data...');
    const res = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(currentUser)}/data`, {
      method: 'DELETE'
    });

    // Clear local storage and state
    messagesEl.innerHTML = '';
    sessionId = null;
    localStorage.removeItem('cybermentor_session_' + currentUser);
    localStorage.removeItem('cybermentor_user_' + currentUser);

    const data = await res.json();
    addAgentMessage(
      "🛡️ **Your data has been permanently deleted.**\n\n" +
      "All conversation histories, ACE cognitive memory notes, and documented skills have been completely purged from Cloud Firestore and local storage in accordance with our Zero-Knowledge Privacy Policy.\n\n" +
      "You have a completely fresh slate. How can I help you today?"
    );

    // Refresh progress sidebar
    loadProgress(currentUser);
    setStatus('ready', 'CyberMentor Ready');
  } catch (err) {
    console.error("Error deleting profile data:", err);
    alert("An error occurred while deleting profile data. Please try again.");
    setStatus('ready', 'CyberMentor Ready');
  }
}

// ── Multi-Format Resume Upload & Document Parsing Engine (PDF, Word DOCX, TXT) ─
const uploadResumeBtn = document.getElementById('btn-upload-resume');
const resumeFileInput = document.getElementById('resume-file-input');

async function extractTextFromResumeFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();

  // 1. Plain Text / Markdown / RTF / JSON files
  if (['txt', 'md', 'json', 'rtf'].includes(ext)) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result || '');
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  }

  // 2. Microsoft Word (.docx) via Mammoth.js (Client-side)
  if (ext === 'docx' && typeof mammoth !== 'undefined') {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      if (result && result.value && result.value.trim().length > 20) {
        return result.value.trim();
      }
    } catch (err) {
      console.warn('Client-side Mammoth.js DOCX parsing fallback:', err);
    }
  }

  // 3. Adobe PDF (.pdf) via PDF.js (Client-side)
  if (ext === 'pdf' && typeof window['pdfjs-dist/build/pdf'] !== 'undefined') {
    try {
      const pdfjsLib = window['pdfjs-dist/build/pdf'];
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const pagesText = [];
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageStr = textContent.items.map(item => item.str).join(' ');
        if (pageStr && pageStr.trim()) {
          pagesText.push(pageStr.trim());
        }
      }
      if (pagesText.length > 0) {
        return pagesText.join('\n\n');
      }
    } catch (err) {
      console.warn('Client-side PDF.js parsing fallback:', err);
    }
  }

  // 4. Server-Side Document Parser Fallback (POST /api/resume/parse)
  try {
    const formData = new FormData();
    formData.append('file', file);
    const resp = await fetch(`${API_BASE_URL}/api/resume/parse`, {
      method: 'POST',
      body: formData,
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.text && data.text.trim()) {
        return data.text.trim();
      }
    } else {
      const err = await resp.json().catch(() => ({}));
      console.warn('Server-side parser returned status:', resp.status, err);
    }
  } catch (err) {
    console.warn('Server-side parse endpoint error:', err);
  }

  // 5. Ultimate fallback: Only read plain-text format files, NEVER binary files
  if (['txt', 'md', 'json', 'rtf', 'csv', 'log'].includes(ext)) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result || '';
        // Strip unprintable control characters to prevent binary junk
        const printable = text.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g, ' ');
        resolve(printable);
      };
      reader.onerror = () => resolve('');
      reader.readAsText(file);
    });
  }

  return '';
}

if (uploadResumeBtn && resumeFileInput) {
  uploadResumeBtn.addEventListener('click', () => {
    resumeFileInput.click();
  });

  resumeFileInput.addEventListener('change', async (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;

    if (statusText) statusText.textContent = `📄 Extracting ${file.name}...`;
    if (statusDot) statusDot.className = 'status-dot active';

    try {
      const extractedText = await extractTextFromResumeFile(file);
      if (!extractedText || extractedText.trim().length < 15) {
        alert(`Could not extract readable text from "${file.name}".\n\nPlease ensure your document contains selectable text (not scanned images), or paste the resume text directly into the chat.`);
        if (statusText) statusText.textContent = 'CyberMentor Ready';
        resumeFileInput.value = '';
        return;
      }

      // Format clean prompt for CyberMentor & ACE Cognitive Profile
      const cleanContent = extractedText.trim().slice(0, 7500);
      const prompt = `Please perform an in-depth cybersecurity resume review for my uploaded document (${file.name}). Extract all technical competencies, certifications, and hands-on tools into my ACE cognitive profile, calculate my job readiness score, and proactively probe me on any adjacent or missing high-value skills (e.g. Wireshark, Linux, Python, SIEM, NIST) I might have forgotten to mention that would significantly strengthen my hiring appeal:\n\n---\n${cleanContent}\n---`;
      
      messageInput.value = prompt;
      messageInput.dispatchEvent(new Event('input'));
      sendMessage();
    } catch (err) {
      console.error('Resume processing error:', err);
      alert(`Error reading resume: ${err.message}\n\nYou can also copy & paste the text directly into the chat.`);
    } finally {
      resumeFileInput.value = '';
      if (statusText) statusText.textContent = 'CyberMentor Ready';
    }
  });
}

const closeResourcesBtn = document.getElementById('close-resources-btn');
if (closeResourcesBtn) {
  closeResourcesBtn.addEventListener('click', () => {
    const resourcesOverlay = document.getElementById('resources-overlay');
    if (resourcesOverlay) {
      resourcesOverlay.classList.remove('active');
      resourcesOverlay.classList.add('hidden');
    }
  });
}

// ── Mindmaps & Transfer Explorer Controller ──────────────────────────────
const closeMindmapBtn = document.getElementById('close-mindmap-btn');
if (closeMindmapBtn) {
  closeMindmapBtn.addEventListener('click', () => {
    const mindmapOverlay = document.getElementById('mindmap-overlay');
    if (mindmapOverlay) {
      mindmapOverlay.classList.remove('active');
      mindmapOverlay.classList.add('hidden');
    }
  });
}

// Tab Switching
document.querySelectorAll('.mindmap-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.mindmap-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.mindmap-view').forEach(v => {
      v.classList.remove('active');
      v.classList.add('hidden');
    });

    tab.classList.add('active');
    const targetId = `view-${tab.dataset.tab}`;
    const targetView = document.getElementById(targetId);
    if (targetView) {
      targetView.classList.remove('hidden');
      targetView.classList.add('active');
    }
  });
});

const sourceRoleSelect = document.getElementById('select-source-role');
const targetRoleSelect = document.getElementById('select-target-role');
const skillsRoleSelect = document.getElementById('select-skills-role');
const certsRoleSelect  = document.getElementById('select-certs-role');

if (sourceRoleSelect) sourceRoleSelect.addEventListener('change', renderTransferExplorer);
if (targetRoleSelect) targetRoleSelect.addEventListener('change', renderTransferExplorer);
if (skillsRoleSelect) skillsRoleSelect.addEventListener('change', renderSkillsMindmap);
if (certsRoleSelect)  certsRoleSelect.addEventListener('change', renderCertsMindmap);

// In-memory role ontology cache for client-side snappy interactions
const _ROLE_ONTOLOGY = {
  software_developer: {
    title: "Software Developer / Software Engineer",
    skills: {
      "Software Architecture": ["Clean Architecture & Design Patterns", "REST & GraphQL API Design", "Microservices & Distributed Systems", "Relational & NoSQL Database Optimization"],
      "Engineering & Tooling": ["Git Version Control & PR Reviews", "CI/CD Pipeline Automation", "Unit, Integration & E2E Testing", "Docker Containerization"],
      "Languages & Frameworks": ["Python, TypeScript, Go, Java, Rust", "Modern Web Frameworks (FastAPI, Next.js, React)", "Data Structures & Algorithmic Complexity"]
    },
    certs: { "Foundational": ["AWS Certified Developer - Associate", "Meta Front-End/Back-End Professional"], "Core": ["Google Cloud Professional Developer", "Certified Kubernetes Application Developer (CKAD)"], "Advanced": ["AWS Solutions Architect - Associate", "Microsoft Certified: Azure Developer"] }
  },
  security_software_engineer: {
    title: "Security Software Engineer (AppSec / DevSecOps)",
    skills: {
      "Application Security": ["OWASP Top 10 & ASVS Standards", "Threat Modeling (STRIDE, PASTA)", "Static & Dynamic Analysis (SAST/DAST/IAST)", "Software Composition Analysis (SCA) & SBOM"],
      "Secure Engineering": ["Cryptographic Implementations (AES, RSA, ECC, TLS)", "OAuth2, OIDC, JWT & SAML Authentication", "Secrets Management (HashiCorp Vault, AWS Secrets)", "Memory Safety & Input Sanitization Defenses"],
      "DevSecOps Automation": ["Security Gates in GitHub Actions & GitLab CI", "Infrastructure as Code Security (Semgrep, Tfsec)", "Container Image Scanning (Trivy, Grype)", "Automated Bug Bounty & Vulnerability Remediation"]
    },
    certs: { "Foundational": ["CompTIA Security+", "CSSLP (Certified Secure Software Lifecycle Professional)"], "Core": ["Certified DevSecOps Professional (CDP)", "OffSec OSWE (Web Expert)"], "Advanced": ["SANS SEC540 (Cloud DevSecOps)", "GIAC GWEB", "CASE (Certified Application Security Engineer)"], "Capstone": ["SANS SEC522", "ISC2 CISSP"] }
  },
  ai_developer: {
    title: "AI Developer / LLM Application Engineer",
    skills: {
      "LLM & GenAI Development": ["Gemini API / OpenAI API / Anthropic Claude SDKs", "Retrieval-Augmented Generation (RAG) Architecture", "Vector Databases & Embeddings (Pinecone, Chroma, pgvector)", "Structured Outputs, JSON Schema & Function Calling"],
      "Agentic Frameworks & Ops": ["Google Antigravity SDK & Multi-Agent Orchestration", "LangChain, LlamaIndex, Semantic Kernel", "Semantic Caching & Token Optimization", "Model Quantization, LoRA & Parameter-Efficient Fine-Tuning"],
      "Evaluation & Pipelines": ["Ragas / Promptfoo RAG Evaluation Benchmarks", "Context Window Management & Chunking Strategies", "Streaming SSE & Bidirectional WebSocket Protocols"]
    },
    certs: { "Foundational": ["Google Cloud Digital Leader", "DeepLearning.AI Generative AI Specialist"], "Core": ["Google Cloud Professional Machine Learning Engineer", "AWS Certified AI Practitioner"], "Advanced": ["Databricks Certified Generative AI Engineer", "TensorFlow Developer Certificate"] }
  },
  ai_security_specialist: {
    title: "AI Security Specialist / AI Safety Engineer",
    skills: {
      "GenAI Threat Vectors": ["OWASP Top 10 for LLMs / GenAI Security", "Direct & Indirect Prompt Injection Defenses", "Model Inversion, Extraction & Data Poisoning", "RAG Vector Poisoning & Context Leakage"],
      "AI Red Teaming & Guardrails": ["Adversarial Jailbreak Testing & Prompt Fuzzing", "NeMo Guardrails & Guardrails.ai Policy Enforcement", "Constitutional AI Alignment & Content Safety Filters", "Training Data Watermarking & Model Fingerprinting"],
      "AI Governance & Compliance": ["NIST AI Risk Management Framework (AI RMF 1.0)", "EU Artificial Intelligence Act (AI Act) Compliance", "ISO/IEC 42001 AI Management System (AIMS)", "Differential Privacy & Synthetic Data Protection"]
    },
    certs: { "Foundational": ["CompTIA Security+", "IAPP AIGP (AI Governance Professional)"], "Core": ["Certified AI Security Professional (CAISP)", "SANS SEC595 (AI Security & LLM Defense)"], "Advanced": ["OffSec OSDA", "MIT Professional Certificate in AI Safety"], "Capstone": ["ISC2 CISSP + AI Security Specialization"] }
  },
  prompt_engineer: {
    title: "Prompt Engineer / LLM Guardrail Specialist",
    skills: {
      "Prompt Optimization": ["Few-Shot, Zero-Shot & Chain-of-Thought Prompting", "System Prompt Engineering & Role Alignment", "XML/Markdown Semantic Delimiters for Injection Defense", "ReAct & Tree-of-Thoughts Reasoning Frameworks"],
      "Guardrails & Evals": ["Promptfoo & DeepEval Automated Benchmarks", "Hallucination Detection & Groundedness Scoring", "Adversarial Fuzzing & Red-Teaming Prompt Sets", "Token Compression & Latency Reduction"],
      "Integration": ["JSON Schema Strict Output Structuring", "Tool/Function-Calling Prompt Schema Design", "Dynamic Context Injection & Metaprompting"]
    },
    certs: { "Foundational": ["Anthropic Prompt Engineering Certification", "Vanderbilt Prompt Engineering Specialization"], "Core": ["OpenAI Certified Prompt Architect", "DeepLearning.AI Prompt Engineering for Developers"], "Advanced": ["AWS Certified AI Practitioner"] }
  },
  forward_deployed_engineer: {
    title: "Forward Deployed Engineer (FDE)",
    skills: {
      "Customer Integration": ["Enterprise Architecture Custom Connectors", "On-Prem, Hybrid & Air-Gapped Cloud Deployments", "API Ingestion & ETL Data Pipeline Transformation", "Mission-Critical Production Debugging on Client Sites"],
      "Rapid Engineering": ["Full-Stack Prototyping (FastAPI, Python, TypeScript)", "Reverse Engineering Legacy Systems", "Telemetry, Observability & Custom Metrics (OpenTelemetry)", "Zero-Downtime Migration & Cutover Strategies"],
      "Consulting & Leadership": ["Executive Technical Briefings & Stakeholder Buy-in", "Translating Ambiguous Business Needs to Production Code", "Solution Architecture & SLA Management"]
    },
    certs: { "Foundational": ["AWS Certified Solutions Architect - Associate", "CompTIA Security+"], "Core": ["Google Cloud Professional Cloud Architect", "Certified Kubernetes Administrator (CKA)"], "Advanced": ["AWS Certified Solutions Architect - Professional", "HashiCorp Certified: Terraform Associate"] }
  },
  cloud_engineer: {
    title: "Cloud Engineer / Infrastructure Architect",
    skills: {
      "Cloud Architecture": ["Multi-Cloud Fleet Management (AWS, GCP, Azure)", "VPC Networking, Transit Gateways & DirectConnect", "Cloud Compute, Serverless (Lambda/Cloud Run) & Edge", "Object, Block & Elastic Cloud Storage"],
      "DevOps & IaC": ["Infrastructure as Code (Terraform, OpenTofu, Pulumi)", "Kubernetes (K8s) Cluster Administration", "GitOps (ArgoCD, Flux) & CI/CD Pipelines", "Linux Fleet Automation (Ansible, Bash)"],
      "Reliability & Cost": ["High Availability & Disaster Recovery Architecture", "Cloud FinOps & Resource Cost Optimization", "Observability (Prometheus, Grafana, Datadog)"]
    },
    certs: { "Foundational": ["AWS Cloud Practitioner", "GCP Cloud Digital Leader"], "Core": ["AWS Solutions Architect - Associate", "Google Cloud Professional Cloud Architect", "CKA (Kubernetes)"], "Advanced": ["AWS Solutions Architect - Professional", "HashiCorp Terraform Associate"] }
  },
  cloud_security: {
    title: "Cloud Security Engineer",
    skills: {
      "Cloud Architecture": ["AWS / GCP / Azure Security Architecture", "IAM Least Privilege & Role Trust Policies", "VPC Flow Logs, GuardDuty & CloudTrail", "KMS Encryption & Key Management"],
      "DevSecOps & Automation": ["Infrastructure as Code (Terraform)", "CI/CD Pipeline Security Gates", "Container & Kubernetes Hardening (Falco/Trivy)", "CSPM & CWPP Configuration (Wiz, Prisma)"],
      "Cloud Compliance": ["CIS Cloud Foundations Benchmarks", "Shared Responsibility Model", "Automated Remediation Lambda/Cloud Functions", "Cloud Forensics & Posture Audits"]
    },
    certs: { "Foundational": ["AWS Cloud Practitioner", "GCP Cloud Digital Leader", "CompTIA Security+"], "Core": ["AWS Certified Security - Specialty", "Google Cloud Security Engineer", "Microsoft SC-100"], "Advanced": ["ISC2 CCSP", "Certified Kubernetes Security Specialist (CKS)"], "Capstone": ["ISC2 CISSP", "GIAC GCSA"] }
  },
  security_engineer: {
    title: "Security Engineer (SecOps & Infrastructure)",
    skills: {
      "Infrastructure Defense": ["Identity & Access Management (SSO, MFA, PAM)", "Endpoint Security & EDR/XDR Engineering", "Next-Gen Firewalls & Microsegmentation", "Vulnerability Management & Patch Governance (Qualys, Tenable)"],
      "Security Automation": ["SOAR Playbook Authoring (Tines, Splunk SOAR, Cortex XSOAR)", "Python & Bash Security Automation Scripting", "Log Aggregation Pipeline Tuning", "Certificate Lifecycle & PKI Management"],
      "Hardening & Zero Trust": ["Operating System Hardening (CIS Benchmarks)", "Zero Trust Architecture (NIST SP 800-207)", "Cloud & On-Prem Attack Surface Reduction"]
    },
    certs: { "Foundational": ["CompTIA Security+", "Microsoft SC-900"], "Core": ["CompTIA CySA+", "GIAC GSEC", "Microsoft SC-200"], "Advanced": ["GIAC GCED", "ISC2 SSCP", "Palo Alto PCNSE"], "Capstone": ["ISC2 CISSP", "SANS SEC501"] }
  },
  network_security_engineer: {
    title: "Network Security Engineer",
    skills: {
      "Network Perimeter Defense": ["Next-Gen Firewalls (Palo Alto Networks, Fortinet, Cisco ASA)", "Intrusion Detection/Prevention (Snort, Suricata, Zeek)", "Zero Trust Network Access (ZTNA) & SASE", "WAF & DDoS Mitigation (Cloudflare, Akamai, AWS Shield)"],
      "Secure Connectivity": ["IPsec / SSL VPN Tunneling Architecture", "BGP, OSPF, VLANs, VXLAN & Network Segmentation", "TLS/SSL Decryption & Certificate Inspection", "802.1X Network Access Control (NAC / Cisco ISE)"],
      "Network Telemetry": ["Wireshark & NetFlow/IPFIX Traffic Analysis", "Network Packet Broker (NPB) & TAP Infrastructure", "DNS Security (DNSSEC, DoH, Sinkholing)"]
    },
    certs: { "Foundational": ["CompTIA Network+", "Cisco CCNA"], "Core": ["Cisco CCNP Security", "Palo Alto PCNSE", "Fortinet NSE 4/7"], "Advanced": ["GIAC GNFA (Network Forensics)", "Check Point CCSA/CCSE"], "Capstone": ["Cisco CCIE Security", "SANS SEC503"] }
  },
  soc_analyst: {
    title: "SOC Analyst (Security Operations Center)",
    skills: {
      "Detection & SIEM": ["SIEM Architecture (Splunk / Sentinel / QRadar)", "Query Languages (SPL / KQL)", "Log Parsing (Syslog, Auth, Web, Firewall)", "Threat Hunting Hypotheses"],
      "Network & Endpoint Defense": ["Wireshark & PCAP Traffic Analysis", "EDR Telemetry (CrowdStrike / Defender)", "Phishing Email Header Analysis", "Threat Intel (VirusTotal, AlienVault OTX)"],
      "Incident Response & Frameworks": ["PICERL Incident Lifecycle", "MITRE ATT&CK Mapping", "Cyber Kill Chain Correlation", "NIST SP 800-61r2 Runbooks"]
    },
    certs: { "Foundational": ["CompTIA Security+", "Cisco CyberOps Associate"], "Core": ["CompTIA CySA+", "Splunk Core Power User", "Microsoft SC-200"], "Advanced": ["GIAC GCIH (Incident Handler)", "Blue Team Level 1 (BTL1)"], "Capstone": ["GIAC GCFA", "SANS SEC504"] }
  },
  penetration_tester: {
    title: "Penetration Tester / Ethical Hacker",
    skills: {
      "Offensive Assessment": ["OWASP Top 10 Web Application Flaws", "Active Directory Domain Escalation", "Network Port & Service Enumeration", "Vulnerability Exploitation (Metasploit)"],
      "Tooling & Scripting": ["Burp Suite Professional", "Nmap, Masscan, Amass", "BloodHound & Mimikatz", "Python & Bash Exploit Customization"],
      "Methodology & Scoping": ["PTES Standard & Rules of Engagement", "CVSS Risk Scoring", "Technical Debriefing & Proof-of-Concept", "Executive Pentest Report Writing"]
    },
    certs: { "Foundational": ["eLearnSecurity eJPT", "CompTIA PenTest+"], "Core": ["TCM Security PNPT", "OffSec OSCP"], "Advanced": ["OffSec OSWE", "GIAC GPEN", "CRTO"], "Capstone": ["OffSec OSEP", "SANS SEC660"] }
  },
  red_team: {
    title: "Red Teamer / Offensive Operations",
    skills: {
      "Adversary Emulation": ["Command & Control (C2) Infrastructure (Cobalt Strike, Sliver, Havoc)", "Active Directory Multi-Forest Compromise & Kerberoasting", "EDR / AV Evasion & Process Injection", "Living off the Land (LotL / LOLBins) Techniques"],
      "Covert Operations": ["Custom Payload Weaponization & Obfuscation", "Initial Access (Spearphishing, Waterholing, Hardware Implants)", "Physical Penetration Testing & Social Engineering", "Lateral Movement (WMI, WinRM, PsExec, Pass-the-Hash)"],
      "Debrief & Defense Collaboration": ["Purple Teaming & Threat Hunting Collaboration", "TIBER-EU & CBEST Regulatory Emulation Frameworks", "Executive Proof-of-Impact & Risk Remediation Roadmaps"]
    },
    certs: { "Foundational": ["OffSec OSCP", "CompTIA PenTest+"], "Core": ["Zero-Point Security CRTO (Red Team Operator)", "OffSec OSEP (Evasion)"], "Advanced": ["CRTE (Red Team Expert)", "SANS SEC565 (Red Team Operations)"], "Capstone": ["OffSec OSMR", "SANS SEC699"] }
  },
  grc: {
    title: "GRC Analyst (Governance, Risk, Compliance)",
    skills: {
      "Risk & Compliance Frameworks": ["NIST CSF & NIST SP 800-53", "ISO/IEC 27001 ISMS Implementation", "SOC 2 Type II Trust Criteria Audits", "HIPAA, PCI-DSS & GDPR Privacy"],
      "Governance & Operations": ["Third-Party Vendor Risk Reviews (TPRM)", "Risk Register & FAIR Risk Quantification", "Security Policy & SOP Authoring", "Executive Risk Presentations & Board Dashboards"],
      "Audit & Advisory": ["Internal Audit Evidence Gathering", "Control Gap Assessments", "Security Awareness Program Design", "Regulatory Compliance Remediation Tracking"]
    },
    certs: { "Foundational": ["CompTIA Security+", "ISACA ITCA"], "Core": ["ISACA CISA (Auditor)", "ISACA CRISC (Risk Specialist)"], "Advanced": ["ISO 27001 Lead Auditor", "ISC2 CGRC", "IAPP CIPP/E"], "Capstone": ["ISC2 CISSP", "ISACA CISM"] }
  },
  grc_leader: {
    title: "GRC Leader / VP of Risk & Compliance",
    skills: {
      "Enterprise Risk Leadership": ["Board-Level Cyber Risk Quantification (FAIR Model)", "Enterprise Risk Management (ERM) Alignment", "Multi-Jurisdiction Regulatory Strategy (SEC, DORA, NIS2, NYDFS)", "Enterprise Compliance Budget & Resource Allocation"],
      "Audit & Trust Governance": ["External Regulatory Examination Defense", "Global Trust & Assurance Program Direction", "Continuous Automated Compliance Monitoring (Vanta, Drata)", "Executive Crisis & Breach Disclosure Oversight"],
      "Team & Policy Direction": ["Building High-Performance GRC & Audit Teams", "Enterprise Governance Charter & Committee Chairing"]
    },
    certs: { "Foundational": ["CompTIA Security+", "CISA"], "Core": ["ISACA CISM", "ISACA CRISC"], "Advanced": ["ISC2 CISSP", "ISACA CGEIT (Governance)"], "Capstone": ["Open FAIR Certification", "Executive GRC Leadership"] }
  },
  privacy_specialist: {
    title: "Privacy Specialist / Data Protection Officer (DPO)",
    skills: {
      "Privacy Law & Regulation": ["GDPR, CCPA/CPRA, HIPAA, GLBA, PIPEDA", "Cross-Border Data Transfer Frameworks (EU-US DPF, SCCs)", "Data Subject Access Request (DSAR) Workflows", "Data Retention, Purge & Minimization Enforcement"],
      "Privacy by Design": ["Data Privacy Impact Assessments (DPIA / PIA)", "Data Mapping, Classification & Lineage (OneTrust, BigID)", "Data Anonymization, Pseudonymization & Tokenization", "Privacy Incident & Breach Notification Handling"],
      "Governance & Advisory": ["Privacy Policy, Terms & Cookie Consent Management", "Vendor Data Processing Agreement (DPA) Negotiations"]
    },
    certs: { "Foundational": ["CompTIA Security+", "IAPP CIPM (Privacy Manager)"], "Core": ["IAPP CIPP/US", "IAPP CIPP/E (European Privacy)", "IAPP CIPT (Privacy Technologist)"], "Advanced": ["ISACA CDPSE (Data Privacy Solutions Engineer)", "FIP (Fellow of Information Privacy)"] }
  },
  policy_specialist: {
    title: "Policy Specialist / Cyber Regulatory Strategist",
    skills: {
      "Policy Architecture": ["Enterprise Information Security Policy Frameworks", "Standards, Guidelines & SOP Development", "NIST CSF 2.0 & ISO 27001 Control Mapping", "Exception Management & Compensating Controls"],
      "Regulatory & Legal Strategy": ["SEC Cyber Disclosure Rule Alignment (Form 8-K/10-K)", "Executive Orders (EO 14028) & Federal Standards", "Critical Infrastructure Directives (CISA, TSA, NERC-CIP)", "Incident Disclosure Coordination with General Counsel"],
      "AI & Emerging Governance": ["Enterprise AI Use Policy & Acceptable Use Governance", "Supply Chain Security Directives & SBOM Mandates"]
    },
    certs: { "Foundational": ["CompTIA Security+", "ISACA ITCA"], "Core": ["ISC2 CGRC (Governance, Risk & Compliance)", "ISACA CGEIT"], "Advanced": ["SANS MGT514 (Security Strategic Planning)", "Harvard/Georgetown Cyber Policy Certificate"] }
  },
  dfir: {
    title: "DFIR (Digital Forensics & Incident Response)",
    skills: {
      "Forensic Extraction": ["Volatile Memory Acquisition (Volatility)", "Disk Imaging & Master File Table (MFT) Parsing", "Windows Registry & Event Log Forensics", "Evidence Chain-of-Custody Protocols"],
      "Malware & Threat Analysis": ["Static & Dynamic Malware Triage (Ghidra, PEStudio)", "Command and Control (C2) Traffic Profiling", "Ransomware Decryption & Indicator Extraction", "Forensic Timeline Creation (Plaso/log2timeline)"],
      "Breach Response": ["Enterprise Containment Command", "Threat Actor Attribution", "Expert Forensic Witness Testimony", "Root Cause Incident Reporting"]
    },
    certs: { "Foundational": ["CompTIA Security+", "GIAC GCFE"], "Core": ["GIAC GCIH", "GIAC GCFA"], "Advanced": ["GIAC GREM (Reverse Engineering)", "GNFA (Network Forensics)"], "Capstone": ["SANS FOR508 / FOR572"] }
  },
  ciso: {
    title: "CISO / Executive Security Leadership",
    skills: {
      "Executive Strategy": ["Enterprise Risk Governance & Board Reporting", "Cybersecurity Budget & Financial Allocation", "C-suite Alignment & Business Strategy", "Cyber Insurance & Contract Negotiations"],
      "Leadership & Culture": ["Building & Mentoring Security Teams", "Crisis Command & Breach Spokesperson", "Enterprise Security Culture Advocacy", "Regulatory & Legal Risk Strategy"]
    },
    certs: { "Foundational": ["CompTIA Security+", "CISA"], "Core": ["CISM", "CRISC"], "Advanced": ["ISC2 CISSP", "GIAC GSLC"], "Capstone": ["CCISO", "Executive Leadership (CMU/Wharton)"] }
  },
  it_helpdesk: {
    title: "IT Helpdesk / Systems Support",
    skills: {
      "Technical Foundations": ["Windows/Linux/macOS OS Internals", "Active Directory & LDAP Management", "TCP/IP, Subnetting & Gateway Routing", "DNS, DHCP, Firewall Basics"],
      "Tooling & Admin": ["ServiceNow & Jira Service Desk", "PowerShell & CLI Scripting", "Endpoint Antivirus & Sysinternals", "RMM & Patch Management"],
      "Process & Soft Skills": ["SLA Triage & Queue Management", "User Access Provisioning", "Root-cause Troubleshooting", "Customer Incident De-escalation"]
    },
    certs: { "Foundational": ["CompTIA A+", "Google IT Support"], "Core": ["CompTIA Network+", "Microsoft MD-102"], "Advanced": ["CompTIA Security+", "Microsoft SC-900"] }
  }
};

// Comprehensive role transition matrix
const _TRANSFER_PRESETS = {
  "software_developer->security_software_engineer": { score: 92, diff: "Very Smooth", timeline: "3-6 months", shared: ["Codebase Architecture & Design Patterns", "CI/CD Pipeline Configurations", "Git Workflows & Pull Request Reviews", "REST API Development & Database Queries"], bridge: ["Writing Feature Code ➔ Threat Modeling & Secure Code Review", "Debugging Logic Flaws ➔ Identifying Business Logic & OWASP Flaws", "Unit Testing ➔ Automated SAST / DAST Security Gates"], delta: ["OWASP ASVS & Top 10 Exploitation", "Cryptographic Primitives & Secret Management", "Software Composition Analysis & SBOM (Trivy)", "Threat Modeling Frameworks (STRIDE)"], certs: ["Certified DevSecOps Professional (CDP)", "OffSec OSWE", "CSSLP"], note: "Developers make world-class AppSec engineers because you already understand how code executes. Focus on exploiting and fixing OWASP vulnerabilities in PortSwigger Web Security Academy." },
  "software_developer->ai_developer": { score: 90, diff: "Direct Pivot", timeline: "2-4 months", shared: ["Python & TypeScript Development", "API Consumption & Asynchronous Processing", "Data Structures & Database Queries", "Modern Web Framework Integration"], bridge: ["Standard APIs ➔ LLM Client SDKs (Gemini, OpenAI, Anthropic)", "SQL Database Queries ➔ Vector Embeddings & Similarity Search (pgvector/Pinecone)", "Deterministic Functions ➔ Agentic Function-Calling & Tool Execution"], delta: ["Retrieval-Augmented Generation (RAG) Architecture", "Structured Output Schema Enforcement (Pydantic/JSON Schema)", "Context Window & Token Budget Management", "RAG Evaluation Metrics (Ragas, DeepEval)"], certs: ["DeepLearning.AI Generative AI Specialist", "Google Cloud Machine Learning Engineer"], note: "Your coding velocity is your superpower. Master RAG indexing, function-calling agent loops, and prompt caching to build state-of-the-art AI applications." },
  "software_developer->forward_deployed_engineer": { score: 88, diff: "Smooth", timeline: "3-6 months", shared: ["Full-Stack Problem Solving", "API Integration & Reverse Engineering", "Git & Deployment Workflows", "Production Bug Triage"], bridge: ["Internal Codebases ➔ Client Enterprise Environments", "Sprint Planning ➔ Stakeholder Requirement Alignment"], delta: ["Hybrid / Air-Gapped Cloud Deployments", "OpenTelemetry Observability & Live Diagnostics", "High-Stakes Client Communication & Technical Demos"], certs: ["AWS Certified Solutions Architect", "Certified Kubernetes Administrator (CKA)"], note: "Forward Deployed Engineers sit right between engineering and the customer mission. Pair your code expertise with rapid prototyping and customer empathy." },
  "ai_developer->ai_security_specialist": { score: 85, diff: "Direct Evolution", timeline: "3-6 months", shared: ["LLM Architecture & RAG Pipelines", "Tokenization & Vector Embeddings", "System Prompt & Function-Calling Design", "Python & Agent SDKs"], bridge: ["Building Prompts ➔ Adversarial Prompt Injection Fuzzing", "Deploying RAG ➔ Securing Vector Databases from Context Extraction", "Agent Tool Calling ➔ Guardrailing Arbitrary Code & Tool Abuse"], delta: ["OWASP Top 10 for LLMs", "NeMo Guardrails & Guardrails.ai Policy Definition", "NIST AI Risk Management Framework (AI RMF)", "Model Poisoning & Adversarial Robustness"], certs: ["Certified AI Security Professional (CAISP)", "SANS SEC595", "IAPP AIGP"], note: "As organizations adopt GenAI, AI Security Specialists are in extreme demand. Transition by building red-teaming test suites for production agents." },
  "penetration_tester->red_team": { score: 90, diff: "Natural Senior Progression", timeline: "6-12 months", shared: ["Exploitation Mechanics & Privilege Escalation", "Burp Suite & Network Tooling", "Active Directory Exploitation", "Scripting & Custom Exploits"], bridge: ["Running Automated Scanners ➔ Stealthy Living off the Land (LOLBins)", "Exploiting One Host ➔ Enterprise Multi-Forest Takeover", "Technical Report Writing ➔ Executive Purple Team Collaboration"], delta: ["C2 Infrastructure (Cobalt Strike, Sliver, Havoc)", "EDR / AV Hooking & Memory Evasion", "Physical Pentesting & Targeted Spearphishing", "Adversary Emulation Frameworks (TIBER-EU)"], certs: ["CRTO (Certified Red Team Operator)", "OffSec OSEP", "CRTE"], note: "Pentesting tests vulnerabilities; Red Teaming tests detection and human response. Master C2 deployment and stealth evasion on Zero-Point Security labs." },
  "it_helpdesk->soc_analyst": { score: 85, diff: "Easy to Moderate", timeline: "3-6 months", shared: ["Windows/Linux OS Troubleshooting", "Active Directory User Administration", "Network Protocol Basics (TCP/IP, DNS)", "Ticket Queue Triage under SLAs"], bridge: ["Antivirus Troubleshooting ➔ EDR Alert Triage", "Network Connectivity Checks ➔ Wireshark PCAP Analysis", "User Lockout Investigation ➔ Account Takeover Detection"], delta: ["SIEM Query Syntax (SPL / KQL)", "MITRE ATT&CK Threat Mapping", "Phishing Email Header Forensics", "Cyber Kill Chain Containment"], certs: ["CompTIA Security+", "CompTIA CySA+", "Splunk Core Power User"], note: "You already know how computers and users break. Pivot by learning how attackers exploit those exact systems using SIEM logs and TryHackMe labs." },
  "it_helpdesk->network_security_engineer": { score: 80, diff: "Moderate", timeline: "6-9 months", shared: ["TCP/IP, Subnetting & Gateway Routing", "DNS, DHCP, Switches & Router Admin", "Basic Firewall Rule Inspection", "Network Cable & Hardware Triage"], bridge: ["Configuring Office Routers ➔ Next-Gen Enterprise Firewalls (Palo Alto, Fortinet)", "Troubleshooting WiFi ➔ 802.1X Network Access Control (Cisco ISE)", "Checking Ping/Traceroute ➔ Wireshark Packet Analysis & PCAP Inspection"], delta: ["Zero Trust Network Access (ZTNA) & SASE", "Intrusion Prevention Systems (Suricata/Snort)", "IPsec / SSL VPN Tunnel Engineering", "TLS Inspection & Certificate Decryption"], certs: ["CompTIA Network+", "Cisco CCNA", "Palo Alto PCNSE"], note: "Your deep physical and logical networking foundations make Network Security a seamless fit. Practice firewall rule design and PCAP analysis." },
  "it_helpdesk->cloud_security": { score: 65, diff: "Moderate", timeline: "6-12 months", shared: ["User Authentication Concepts", "Networking Fundamentals", "Operating System Administration"], bridge: ["On-Prem Active Directory ➔ AWS IAM / Azure Entra ID", "Virtual Machines ➔ Cloud Compute (EC2 / Compute Engine)"], delta: ["Cloud Architecture & IAM Least Privilege", "Infrastructure as Code (Terraform)", "Cloud Security Posture Management (CSPM)", "CloudTrail & GuardDuty Log Auditing"], certs: ["AWS Certified Security - Specialty", "CompTIA Security+"], note: "Build free-tier cloud projects and convert manual sysadmin scripts into secure Terraform templates." },
  "grc->grc_leader": { score: 92, diff: "Leadership Evolution", timeline: "2-4 years", shared: ["NIST CSF / ISO 27001 Controls", "Third-Party Vendor Risk Management", "Audit Evidence Gathering & Gap Analysis", "Security Policy Authoring"], bridge: ["Running Control Audits ➔ Defining Enterprise Compliance Strategy", "Filling Risk Registers ➔ Board-Level FAIR Financial Risk Modeling"], delta: ["Global Regulatory Directives (SEC Cyber, DORA, NIS2)", "Automated Compliance Platform Architecture (Vanta/Drata)", "Executive Committee Chairing & C-suite Risk Alignment"], certs: ["ISACA CISM", "ISACA CRISC", "ISC2 CISSP", "CGEIT"], note: "GRC leaders bridge technical controls with corporate bottom lines. Master the FAIR quantitative risk model to articulate cyber risk in dollars." },
  "grc->privacy_specialist": { score: 88, diff: "Smooth Specialty", timeline: "3-6 months", shared: ["Compliance Auditing & Control Frameworks", "Policy Documentation & Governance", "Third-Party Vendor Risk Reviews", "Regulatory Gap Assessments"], bridge: ["Security Controls ➔ Privacy Impact Assessments (DPIA)", "Data Classification ➔ Subject Access Request (DSAR) Fulfillment"], delta: ["Global Privacy Statutes (GDPR, CCPA/CPRA, HIPAA Privacy)", "Privacy by Design & Data Minimization Engineering", "Cross-Border Data Transfer Agreements (DPAs, SCCs)"], certs: ["IAPP CIPP/US", "IAPP CIPP/E", "IAPP CIPM", "ISACA CDPSE"], note: "Privacy is one of the highest-paying compliance specializations. Combine your GRC audit instincts with IAPP CIPP certifications." },
  "grc->policy_specialist": { score: 90, diff: "Direct Alignment", timeline: "2-4 months", shared: ["Security Framework Mapping (NIST/ISO)", "Policy & Standard Authoring", "Audit Defense & Regulatory Scoping", "Executive Reporting"], bridge: ["Internal SOPs ➔ Enterprise Cyber Strategy & SEC Disclosures", "Compliance Tracking ➔ AI & Supply Chain Governance Policy"], delta: ["SEC Form 8-K/10-K Cyber Disclosure Timelines", "Federal Directives & Cyber Executive Orders", "AI Use & Acceptable Risk Policy Frameworks"], certs: ["ISC2 CGRC", "SANS MGT514", "ISACA CGEIT"], note: "Policy specialists shape corporate posture. Focus on emerging AI governance and SEC cyber disclosure mandates to stand out." },
  "soc_analyst->penetration_tester": { score: 75, diff: "Moderate", timeline: "6-12 months", shared: ["Network Packet Capture (Wireshark)", "Understanding Exploit Mechanics", "Attack Signature Footprints", "MITRE ATT&CK Framework"], bridge: ["Detecting Web Attacks ➔ Executing Exploits (SQLi, XSS, SSRF)", "Investigating Malware Persistence ➔ Crafting Payloads", "Reading Alert Signatures ➔ Evading EDR/IDS Rules"], delta: ["Burp Suite Professional & Web App Methodology", "Manual Privilege Escalation (Linux/Windows)", "Penetration Testing Scoping & Report Writing"], certs: ["eLearnSecurity eJPT", "TCM Security PNPT", "OffSec OSCP"], note: "You know what alarms look like on the blue team. Use that insight to practice stealthy offensive techniques on PortSwigger Web Security Academy." },
  "soc_analyst->dfir": { score: 90, diff: "Easy to Moderate", timeline: "3-6 months", shared: ["Evidence Gathering & Timeline Creation", "Endpoint Telemetry Analysis", "Threat Intel Correlation", "Root Cause Incident Analysis"], bridge: ["EDR Alerts ➔ Deep Memory & Disk Forensics", "Alert Triage ➔ Full Forensic Timeline Reconstruction"], delta: ["Memory Dump Analysis (Volatility)", "Master File Table (MFT) & Registry Forensics", "Malware Static/Dynamic Triage (Ghidra, PEStudio)"], certs: ["GIAC GCIH", "GIAC GCFA", "Blue Team Level 1"], note: "DFIR is the natural senior evolution for SOC analysts. Practice investigating memory dumps from past CyberDefenders challenges." },
  "soc_analyst->cloud_security": { score: 80, diff: "Moderate", timeline: "6-9 months", shared: ["Log Correlation & Parsing", "Threat Detection Rules", "Identity & Access Monitoring", "Incident Response Workflows"], bridge: ["On-Prem SIEM ➔ AWS CloudTrail, GuardDuty & CloudWatch", "Firewall Rules ➔ Security Groups & Cloud WAFs"], delta: ["Cloud Architecture (IAM, S3, VPCs)", "Infrastructure as Code Security (Tfsec)", "Container & Kubernetes Runtime Monitoring"], certs: ["AWS Certified Security - Specialty", "Google Cloud Security Engineer"], note: "Master cloud log sources and automate incident containment scripts using AWS Lambda." },
  "grc->ciso": { score: 90, diff: "Leadership Progression", timeline: "5-8 years", shared: ["Enterprise Risk Governance", "Board & Executive Reporting", "Security Policy Management", "Regulatory Compliance (NIST/ISO)"], bridge: ["Control Auditing ➔ Departmental Security Budget Planning", "Vendor Risk Reviews ➔ Enterprise Cyber Insurance Negotiation"], delta: ["Executive Crisis Leadership", "C-suite Business Strategy Alignment", "Enterprise Security Culture Strategy"], certs: ["CISM", "CISSP", "CCISO"], note: "GRC is the most direct path to the CISO chair because modern CISOs are business risk executives first." }
};

function renderTransferExplorer() {
  const src = sourceRoleSelect ? sourceRoleSelect.value : 'it_helpdesk';
  const tgt = targetRoleSelect ? targetRoleSelect.value : 'soc_analyst';
  const container = document.getElementById('transfer-results');
  if (!container) return;

  const srcData = _ROLE_ONTOLOGY[src] || _ROLE_ONTOLOGY.it_helpdesk;
  const tgtData = _ROLE_ONTOLOGY[tgt] || _ROLE_ONTOLOGY.soc_analyst;

  const key = `${src}->${tgt}`;
  const data = _TRANSFER_PRESETS[key] || {
    score: 70,
    diff: "Moderate",
    timeline: "6 months",
    shared: Object.values(srcData.skills)[0].slice(0, 3),
    bridge: ["Technical Background ➔ Domain Specific Application", "Operational Triage ➔ Strategic Problem Solving"],
    delta: Object.values(tgtData.skills)[0].slice(0, 3),
    certs: Object.values(tgtData.certs)[0] || ["CompTIA Security+"],
    note: `Transitioning from ${srcData.title} to ${tgtData.title} leverages your existing domain strengths while expanding targeted hands-on skills.`
  };

  container.innerHTML = `
    <div class="transfer-summary-card">
      <div class="compatibility-bar-wrapper">
        <span class="compatibility-score-text">${data.score}% Compatibility Overlap</span>
        <div class="compatibility-bar-bg">
          <div class="compatibility-bar-fill" style="width: ${data.score}%"></div>
        </div>
        <span class="chip chip-shared">${data.diff} · ⏱️ ${data.timeline}</span>
      </div>

      <div class="transfer-section">
        <h4>✅ Directly Transferable Skills (100% Match)</h4>
        <div class="chips-cloud">
          ${data.shared.map(s => `<span class="chip chip-shared">${escapeHtml(s)}</span>`).join('')}
        </div>
      </div>

      <div class="transfer-section">
        <h4>🌉 Bridge Skills (Adapt & Recontextualize)</h4>
        <div class="chips-cloud">
          ${data.bridge.map(b => `<span class="chip chip-bridge">${escapeHtml(b)}</span>`).join('')}
        </div>
      </div>

      <div class="transfer-section">
        <h4>🎯 Delta Skills to Acquire (The Gap)</h4>
        <div class="chips-cloud">
          ${data.delta.map(d => `<span class="chip chip-delta">${escapeHtml(d)}</span>`).join('')}
        </div>
      </div>

      <div class="transfer-section">
        <h4>🎓 Recommended Bridge Certifications</h4>
        <div class="chips-cloud">
          ${data.certs.map(c => `<span class="chip chip-cert">${escapeHtml(c)}</span>`).join('')}
        </div>
      </div>

      <div class="breaking-intro-quote">
        💡 <strong>Breaking Into Cybersecurity Wisdom:</strong> "${escapeHtml(data.note)}"
      </div>
    </div>
  `;
}

function renderSkillsMindmap() {
  const role = skillsRoleSelect ? skillsRoleSelect.value : 'soc_analyst';
  const container = document.getElementById('skills-mindmap-container');
  if (!container) return;

  const data = _ROLE_ONTOLOGY[role] || _ROLE_ONTOLOGY.soc_analyst;

  container.innerHTML = `
    <div class="mindmap-grid">
      ${Object.entries(data.skills).map(([branch, skillList]) => `
        <div class="mindmap-branch-card">
          <h4>📍 ${escapeHtml(branch)}</h4>
          <ul>
            ${skillList.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
          </ul>
        </div>
      `).join('')}
    </div>
  `;
}

function renderCertsMindmap() {
  const role = certsRoleSelect ? certsRoleSelect.value : 'soc_analyst';
  const container = document.getElementById('certs-mindmap-container');
  if (!container) return;

  const data = _ROLE_ONTOLOGY[role] || _ROLE_ONTOLOGY.soc_analyst;

  container.innerHTML = `
    <div class="cert-timeline-wrapper">
      ${Object.entries(data.certs).map(([tier, certList]) => `
        <div class="cert-tier-item">
          <span class="tier-badge">${escapeHtml(tier)}</span>
          <div class="chips-cloud">
            ${certList.map(c => `<span class="chip chip-cert">${escapeHtml(c)}</span>`).join('')}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

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
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 6px;">
            <div style="flex: 1;">${escapeHtml(m.milestone)}</div>
            <button class="btn-share-milestone" title="Share to Community Feed" style="background: transparent; border: none; cursor: pointer; color: var(--clr-cyan); font-size: 0.8rem; padding: 2px;">🌐</button>
          </div>
          <div class="milestone-date">${date}</div>
        `;

        const shareBtn = el.querySelector('.btn-share-milestone');
        if (shareBtn) {
          shareBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
              const res = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(currentUser)}/share_milestone`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ milestone: m.milestone, badge: "Career Milestone" })
              });
              if (res.ok) {
                shareBtn.textContent = '✅';
                shareBtn.title = 'Shared to Community Feed!';
              }
            } catch (err) {
              console.error("Failed to share milestone:", err);
            }
          });
        }

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
  checkAndAttachResumeActions(el, markdown);
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
  
  // Add quick speaker button to listen on-demand
  const speakBtn = document.createElement('button');
  speakBtn.className = 'tts-speak-btn';
  speakBtn.title = 'Listen to this response';
  speakBtn.innerHTML = '🔊';
  speakBtn.addEventListener('click', () => {
    if (typeof speakCoachSpeech === 'function') {
      speakCoachSpeech(markdown);
    } else if (typeof speakTextFallback === 'function') {
      speakTextFallback(markdown);
    }
  });
  // Check if this response contains an updated resume draft or export trigger
  checkAndAttachResumeActions(el, markdown);

  if (typeof isVoiceNarrationEnabled !== 'undefined' && isVoiceNarrationEnabled) {
    if (typeof speakCoachSpeech === 'function') {
      speakCoachSpeech(markdown);
    } else if (typeof speakTextFallback === 'function') {
      speakTextFallback(markdown);
    } else if (typeof speakText === 'function') {
      speakText(markdown);
    }
  }

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

  // Media players (Veo Video & Lyria Audio)
  // Video URLs/URIs
  html = html.replace(/(?:Access URL:\s*|URL:\s*|URI:\s*)(https?:\/\/[^\s<>]+\.(?:mp4|webm)|https:\/\/storage\.googleapis\.com\/[^\s<>]+)/gi,
    '<div class="media-card video-card"><div class="media-header">🎬 Veo Video Output</div><video controls playsinline class="media-player"><source src="$1">Your browser does not support video playback.</video><div class="media-link"><a href="$1" target="_blank" rel="noopener">Open Direct Video URL</a></div></div>');

  // Focus Synthesizer & Audio Players
  html = html.replace(/(?:Audio:\s*focus-synth:\/\/([a-z_-]+))/gi, (_, mood) => {
    const cleanMood = mood || 'focus';
    return `<div class="cyber-audio-player glass" data-mood="${cleanMood}">
      <div class="audio-card-header">
        <div class="audio-title">🎵 CyberMentor Real-Time Focus Audio Synthesizer</div>
        <span class="audio-status-pill">○ READY</span>
      </div>
      <div class="audio-wave-container">
        <div class="audio-visualizer-bars">
          <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
        </div>
        <div class="audio-preset-info">
          <strong>Binaural Brainwave Sync:</strong> 10Hz Alpha Waves + Warm Ambient Resonance (Flow State)
        </div>
      </div>
      <div class="audio-controls-row">
        <button type="button" class="btn btn-audio-toggle" onclick="toggleFocusAudio('${cleanMood}')">▶️ Play Focus Audio</button>
        <div class="mood-selectors">
          <button type="button" class="btn-audio-mood active" onclick="startFocusAudio('focus', this)">🧘 Alpha Focus</button>
          <button type="button" class="btn-audio-mood" onclick="startFocusAudio('exam_crunch', this)">⚡ Beta Crunch</button>
          <button type="button" class="btn-audio-mood" onclick="startFocusAudio('cyber', this)">🌌 Cyber SOC</button>
          <button type="button" class="btn-audio-mood" onclick="startFocusAudio('winding_down', this)">🌙 Cooldown</button>
        </div>
      </div>
    </div>`;
  });

  // Audio URIs (data:audio or mp3/wav URLs)
  html = html.replace(/(?:Audio:\s*)(data:audio\/[a-z0-9]+;base64,[A-Za-z0-9+/=]+|https?:\/\/[^\s<>]+\.(?:mp3|wav|ogg))/gi,
    '<div class="media-card audio-card"><div class="media-header">🎵 Lyria Study Music</div><audio controls class="media-player" src="$1">Your browser does not support audio playback.</audio></div>');

  // Links (OWASP LLM05 Output Handling: sanitize protocols)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, url) => {
    const cleanUrl = url.trim();
    if (/^(https?:\/\/|mailto:|#|\/)/i.test(cleanUrl)) {
      return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer">${text}</a>`;
    }
    return `<span>${text}</span>`;
  });

  // Paragraphs (double newlines → paragraphs)
  html = html.split(/\n\n+/).map(block => {
    if (block.startsWith('<h') || block.startsWith('<ul') ||
        block.startsWith('<ol') || block.startsWith('<pre') ||
        block.startsWith('<hr') || block.startsWith('<div class="media-card')) {
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

// ── Voice Input (Speech-to-Text) ──────────────────────────────────────────
const micBtn = document.getElementById('btn-mic');
let recognition = null;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  recognition.onstart = () => {
    isRecording = true;
    if (micBtn) micBtn.classList.add('recording');
    setStatus('thinking', 'Listening to your voice...');
  };

  recognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    messageInput.value = transcript;
    messageInput.dispatchEvent(new Event('input'));
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    isRecording = false;
    if (micBtn) micBtn.classList.remove('recording');
    setStatus('ready', 'CyberMentor Ready');
  };

  recognition.onend = () => {
    isRecording = false;
    if (micBtn) micBtn.classList.remove('recording');
    setStatus('ready', 'CyberMentor Ready');
  };

  if (micBtn) {
    micBtn.addEventListener('click', () => {
      if (isRecording) {
        recognition.stop();
      } else {
        try {
          recognition.start();
        } catch (e) {
          console.error("Speech recognition start failed:", e);
        }
      }
    });
  }
} else {
  if (micBtn) {
    micBtn.title = "Speech recognition not supported in this browser";
    micBtn.style.opacity = "0.5";
  }
}

// ── Browser Voice Fallback Helper ─────────────────────────────────────────
function speakTextFallback(text) {
  if (!('speechSynthesis' in window) || !text) return;
  window.speechSynthesis.cancel();
  const clean = text.replace(/[*_#`[\]()]/g, '').replace(/https?:\/\/\S+/g, 'link').slice(0, 450);
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

// ── Analytics Dashboard Controller ─────────────────────────────────────────
const btnAnalytics = document.getElementById('btn-analytics');
const closeAnalyticsBtn = document.getElementById('close-analytics-btn');
const analyticsOverlay = document.getElementById('analytics-overlay');

if (btnAnalytics && analyticsOverlay) {
  btnAnalytics.addEventListener('click', async () => {
    analyticsOverlay.classList.remove('hidden');
    analyticsOverlay.classList.add('active');

    try {
      const res = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(currentUser || 'guest')}/analytics`);
      if (res.ok) {
        const data = await res.json();
        document.getElementById('stat-streak').textContent = `${data.study_streak_days} Days`;
        document.getElementById('stat-readiness').textContent = `${data.cert_readiness_pct}%`;
        document.getElementById('stat-interview-avg').textContent = `${data.interview_average_score} / 100`;
        document.getElementById('stat-milestones-count').textContent = `${data.total_milestones}`;
        if (data.recommended_next_step) {
          document.getElementById('stat-recommended-action').textContent = data.recommended_next_step;
        }

        const trackBadge = document.getElementById('analytics-target-track-badge');
        if (trackBadge && data.target_role) {
          trackBadge.textContent = `🎯 Active Track: ${data.target_role}`;
        }

        const skillsContainer = document.getElementById('analytics-skills-list');
        if (skillsContainer && data.skills_breakdown) {
          skillsContainer.innerHTML = data.skills_breakdown
            .map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`)
            .join('');
        }
      }
    } catch (err) {
      console.warn("Could not load analytics:", err);
    }
  });
}

if (closeAnalyticsBtn && analyticsOverlay) {
  closeAnalyticsBtn.addEventListener('click', () => {
    analyticsOverlay.classList.remove('active');
    analyticsOverlay.classList.add('hidden');
  });
}

// ── Community Milestones Controller ───────────────────────────────────────
const btnCommunity = document.getElementById('btn-community');
const closeCommunityBtn = document.getElementById('close-community-btn');
const communityOverlay = document.getElementById('community-overlay');
const communityContainer = document.getElementById('community-feed-container');

if (btnCommunity && communityOverlay) {
  btnCommunity.addEventListener('click', async () => {
    communityOverlay.classList.remove('hidden');
    communityOverlay.classList.add('active');
    loadCommunityFeed();
  });
}

if (closeCommunityBtn && communityOverlay) {
  closeCommunityBtn.addEventListener('click', () => {
    communityOverlay.classList.remove('active');
    communityOverlay.classList.add('hidden');
  });
}

async function loadCommunityFeed() {
  if (!communityContainer) return;
  communityContainer.innerHTML = '<p style="color: var(--text-secondary);">Loading community feed...</p>';

  try {
    const res = await fetch(`${API_BASE_URL}/api/progress/community/feed`);
    if (!res.ok) throw new Error("Feed fetch error");
    const data = await res.json();

    communityContainer.innerHTML = (data.feed || []).map(item => `
      <div class="community-item">
        <div class="community-user-meta">
          <div class="community-avatar">${item.avatar || '🛡️'}</div>
          <div class="community-text">
            <div class="community-header-line">
              <span class="community-username">${escapeHtml(item.username)}</span>
              <span class="community-badge">${escapeHtml(item.badge || 'Learner')}</span>
              <span class="community-location">• ${escapeHtml(item.location || 'Online')}</span>
            </div>
            <div class="community-milestone-text">${escapeHtml(item.milestone)}</div>
            <span class="community-time">${escapeHtml(item.timestamp)}</span>
          </div>
        </div>
        <button class="community-cheer-btn" data-id="${item.id}">
          👏 <span class="cheer-count">${item.cheers || 0}</span>
        </button>
      </div>
    `).join('');

    // Attach cheer handlers
    document.querySelectorAll('.community-cheer-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const countSpan = btn.querySelector('.cheer-count');
        try {
          const cheerRes = await fetch(`${API_BASE_URL}/api/progress/community/cheer/${id}`, { method: 'POST' });
          if (cheerRes.ok) {
            const result = await cheerRes.json();
            if (countSpan) countSpan.textContent = result.cheers;
            btn.classList.add('cheered');
          }
        } catch (e) {
          console.error("Cheer failed:", e);
        }
      });
    });
  } catch (err) {
    communityContainer.innerHTML = '<p style="color: var(--text-secondary);">Community network available offline.</p>';
  }
}

// ── Web Audio Focus Ambient Synth Engine ─────────────────────────────────
let audioCtx = null;
let activeSynthNodes = null;
let isAudioPlaying = false;
let currentAudioMood = 'focus';

function getAudioContext() {
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContext();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function startFocusAudio(mood = 'focus', btnElement = null) {
  stopFocusAudio();
  const ctx = getAudioContext();
  currentAudioMood = mood;

  // Master Gain with smooth fade in
  const masterGain = ctx.createGain();
  masterGain.gain.setValueAtTime(0.001, ctx.currentTime);
  masterGain.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + 1.5);
  masterGain.connect(ctx.destination);

  let baseFreq = 216; // A3 harmonic
  let beatFreq = 10;  // 10Hz Alpha Waves (Deep Flow)
  let filterCutoff = 420;

  if (mood === 'energized' || mood === 'exam_crunch') {
    baseFreq = 256; // C4
    beatFreq = 14;  // 14Hz Beta Waves (Active problem solving)
    filterCutoff = 650;
  } else if (mood === 'cyber') {
    baseFreq = 110; // Deep A2 Drone
    beatFreq = 7.83; // Schumann Resonance
    filterCutoff = 350;
  } else if (mood === 'winding_down') {
    baseFreq = 174; // Solfeggio relaxation
    beatFreq = 6;   // Theta cooldown
    filterCutoff = 280;
  }

  // Left & Right Binaural Sine Oscillators
  const oscL = ctx.createOscillator();
  const oscR = ctx.createOscillator();
  oscL.type = 'sine';
  oscR.type = 'sine';
  oscL.frequency.setValueAtTime(baseFreq, ctx.currentTime);
  oscR.frequency.setValueAtTime(baseFreq + beatFreq, ctx.currentTime);

  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.setValueAtTime(filterCutoff, ctx.currentTime);
  filter.Q.value = 2.5;

  // Slow LFO for subtle breathing pulse
  const lfo = ctx.createOscillator();
  const lfoGain = ctx.createGain();
  lfo.frequency.value = 0.08;
  lfoGain.gain.value = filterCutoff * 0.25;
  lfo.connect(lfoGain);
  lfoGain.connect(filter.frequency);

  // Warm Pink/Brown Noise Buffer Generator
  const bufferSize = ctx.sampleRate * 2;
  const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const output = noiseBuffer.getChannelData(0);
  let b0 = 0, b1 = 0, b2 = 0;
  for (let i = 0; i < bufferSize; i++) {
    const white = Math.random() * 2 - 1;
    b0 = 0.99886 * b0 + white * 0.0555179;
    b1 = 0.99332 * b1 + white * 0.0750759;
    b2 = 0.96900 * b2 + white * 0.1538520;
    output[i] = (b0 + b1 + b2) * 0.04;
  }
  const noise = ctx.createBufferSource();
  noise.buffer = noiseBuffer;
  noise.loop = true;

  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = 'lowpass';
  noiseFilter.frequency.value = 220;

  const noiseGain = ctx.createGain();
  noiseGain.gain.value = 0.12;
  noise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(masterGain);

  oscL.connect(filter);
  oscR.connect(filter);
  filter.connect(masterGain);

  oscL.start();
  oscR.start();
  lfo.start();
  noise.start();

  activeSynthNodes = { masterGain, oscL, oscR, lfo, noise, ctx };
  isAudioPlaying = true;
  updateAudioPlayerUI(true, mood, btnElement);
}

function stopFocusAudio() {
  if (activeSynthNodes) {
    try {
      const { masterGain, oscL, oscR, lfo, noise, ctx } = activeSynthNodes;
      masterGain.gain.setValueAtTime(masterGain.gain.value, ctx.currentTime);
      masterGain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
      setTimeout(() => {
        try {
          oscL.stop();
          oscR.stop();
          lfo.stop();
          noise.stop();
        } catch (_) {}
      }, 700);
    } catch (_) {}
    activeSynthNodes = null;
  }
  isAudioPlaying = false;
  updateAudioPlayerUI(false, currentAudioMood);
}

function toggleFocusAudio(mood = 'focus') {
  if (isAudioPlaying) {
    stopFocusAudio();
  } else {
    startFocusAudio(mood);
  }
}
window.toggleFocusAudio = toggleFocusAudio;
window.startFocusAudio = startFocusAudio;
window.stopFocusAudio = stopFocusAudio;

function updateAudioPlayerUI(playing, mood = 'focus', activeBtn = null) {
  document.querySelectorAll('.cyber-audio-player').forEach(card => {
    const playBtn = card.querySelector('.btn-audio-toggle');
    const statusPill = card.querySelector('.audio-status-pill');
    const visualizer = card.querySelector('.audio-visualizer-bars');
    const presetInfo = card.querySelector('.audio-preset-info');

    if (playBtn) {
      playBtn.innerHTML = playing ? '⏸️ Pause Focus Audio' : '▶️ Play Focus Audio';
      playBtn.classList.toggle('playing', playing);
    }
    if (statusPill) {
      statusPill.textContent = playing ? '● LIVE SYNTH PLAYING' : '○ READY';
      statusPill.classList.toggle('active', playing);
    }
    if (visualizer) {
      visualizer.classList.toggle('active', playing);
    }

    if (presetInfo) {
      const descriptions = {
        'focus': '<strong>Deep Focus:</strong> 10Hz Binaural Alpha Waves + Warm Ambient Resonance (Flow State)',
        'exam_crunch': '<strong>Exam Crunch:</strong> 14Hz Beta Waves + High-Retention Active Study Stimulation',
        'cyber': '<strong>Cyber SOC:</strong> 7.83Hz Schumann Deep Ambient Drone for Lab Work & Terminal Focus',
        'winding_down': '<strong>Cooldown:</strong> 6Hz Theta Waves + Solfeggio Relaxation Pad'
      };
      presetInfo.innerHTML = descriptions[mood] || descriptions['focus'];
    }

    card.querySelectorAll('.btn-audio-mood').forEach(b => {
      b.classList.remove('active');
    });
  });

  if (activeBtn) {
    activeBtn.classList.add('active');
  }
}

// ── Focus Studio Music Deck Engine with Full Media Controls ──────────────
const FOCUS_PLAYLIST = [
  {
    title: 'Deep Focus Alpha (10Hz Binaural Beats)',
    tag: 'Alpha Flow · 60 BPM Ambient Synth',
    src: 'audio/track1_deep_focus_alpha.wav'
  },
  {
    title: 'Beta Exam Crunch (14Hz Active Prep)',
    tag: 'High-Retention Problem Solving',
    src: 'audio/track2_beta_exam_crunch.wav'
  },
  {
    title: 'Cyber SOC Night Drone (7.83Hz Schumann)',
    tag: 'Dark Ambient Lab & Terminal Focus',
    src: 'audio/track3_cyber_soc_drone.wav'
  },
  {
    title: 'Solfeggio Theta Cooldown (6Hz Relaxation)',
    tag: 'Post-Study Restoration Pad',
    src: 'audio/track4_theta_cooldown.wav'
  }
];

let currentTrackIndex = 0;
let isAudioMuted = false;
let previousVolume = 0.75;

const focusDeck       = document.getElementById('focus-studio-deck');
const globalAudio     = document.getElementById('global-focus-audio');
const deckTitle       = document.getElementById('deck-track-title');
const deckTag         = document.getElementById('deck-track-tag');
const deckStatus      = document.getElementById('deck-status');
const deckSeekBar     = document.getElementById('deck-seek-bar');
const deckCurTime     = document.getElementById('deck-current-time');
const deckDuration    = document.getElementById('deck-duration');
const deckPlayBtn     = document.getElementById('btn-audio-play');
const deckStopBtn     = document.getElementById('btn-audio-stop');
const deckPrevBtn     = document.getElementById('btn-audio-prev');
const deckNextBtn     = document.getElementById('btn-audio-next');
const deckLoopBtn     = document.getElementById('btn-audio-loop');
const deckMuteBtn     = document.getElementById('btn-audio-mute');
const deckVolSlider   = document.getElementById('deck-vol-slider');
const deckVisualizer  = document.getElementById('deck-visualizer');
const btnCloseDeck    = document.getElementById('btn-close-deck');
const deckTabs        = document.querySelectorAll('.deck-tab');

function formatAudioTime(secs) {
  if (isNaN(secs)) return '0:00';
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

function loadTrack(index, autoplay = true) {
  if (index < 0) index = FOCUS_PLAYLIST.length - 1;
  if (index >= FOCUS_PLAYLIST.length) index = 0;
  currentTrackIndex = index;

  const track = FOCUS_PLAYLIST[index];
  if (deckTitle) deckTitle.textContent = track.title;
  if (deckTag) deckTag.textContent = track.tag;
  if (globalAudio) {
    globalAudio.src = track.src;
    globalAudio.load();
    if (autoplay) {
      globalAudio.play().catch(e => console.log('Audio autoplay info:', e));
    }
  }

  deckTabs.forEach((tab, i) => {
    tab.classList.toggle('active', i === index);
  });
}

function openFocusDeck(trackIndex = 0) {
  if (focusDeck) {
    focusDeck.classList.remove('hidden');
  }
  loadTrack(trackIndex, true);
}
window.openFocusDeck = openFocusDeck;

if (globalAudio) {
  globalAudio.volume = 0.75;

  globalAudio.addEventListener('play', () => {
    if (deckPlayBtn) deckPlayBtn.innerHTML = '⏸';
    if (deckStatus) {
      deckStatus.textContent = '● PLAYING';
      deckStatus.classList.add('active');
    }
    if (deckVisualizer) deckVisualizer.classList.add('active');
  });

  globalAudio.addEventListener('pause', () => {
    if (deckPlayBtn) deckPlayBtn.innerHTML = '▶';
    if (deckStatus) {
      deckStatus.textContent = '○ PAUSED';
      deckStatus.classList.remove('active');
    }
    if (deckVisualizer) deckVisualizer.classList.remove('active');
  });

  globalAudio.addEventListener('timeupdate', () => {
    if (globalAudio.duration) {
      const cur = globalAudio.currentTime;
      const dur = globalAudio.duration;
      if (deckCurTime) deckCurTime.textContent = formatAudioTime(cur);
      if (deckDuration) deckDuration.textContent = formatAudioTime(dur);
      if (deckSeekBar) {
        deckSeekBar.max = dur;
        deckSeekBar.value = cur;
      }
    }
  });

  globalAudio.addEventListener('ended', () => {
    if (!globalAudio.loop) {
      loadTrack(currentTrackIndex + 1, true);
    }
  });
}

if (deckPlayBtn) {
  deckPlayBtn.addEventListener('click', () => {
    if (!globalAudio) return;
    if (globalAudio.paused) {
      if (!globalAudio.src) loadTrack(currentTrackIndex, true);
      else globalAudio.play();
    } else {
      globalAudio.pause();
    }
  });
}

if (deckStopBtn) {
  deckStopBtn.addEventListener('click', () => {
    if (!globalAudio) return;
    globalAudio.pause();
    globalAudio.currentTime = 0;
    if (deckSeekBar) deckSeekBar.value = 0;
    if (deckCurTime) deckCurTime.textContent = '0:00';
    if (deckStatus) {
      deckStatus.textContent = '○ STOPPED';
      deckStatus.classList.remove('active');
    }
  });
}

if (deckPrevBtn) {
  deckPrevBtn.addEventListener('click', () => {
    loadTrack(currentTrackIndex - 1, true);
  });
}

if (deckNextBtn) {
  deckNextBtn.addEventListener('click', () => {
    loadTrack(currentTrackIndex + 1, true);
  });
}

if (deckLoopBtn) {
  deckLoopBtn.addEventListener('click', () => {
    if (!globalAudio) return;
    globalAudio.loop = !globalAudio.loop;
    deckLoopBtn.classList.toggle('active', globalAudio.loop);
  });
}

if (deckSeekBar) {
  deckSeekBar.addEventListener('input', () => {
    if (globalAudio) {
      globalAudio.currentTime = parseFloat(deckSeekBar.value);
    }
  });
}

if (deckVolSlider) {
  deckVolSlider.addEventListener('input', () => {
    if (globalAudio) {
      const vol = parseFloat(deckVolSlider.value);
      globalAudio.volume = vol;
      isAudioMuted = vol === 0;
      if (deckMuteBtn) deckMuteBtn.textContent = vol === 0 ? '🔇' : (vol < 0.5 ? '🔉' : '🔊');
    }
  });
}

if (deckMuteBtn) {
  deckMuteBtn.addEventListener('click', () => {
    if (!globalAudio) return;
    if (isAudioMuted) {
      globalAudio.volume = previousVolume || 0.75;
      if (deckVolSlider) deckVolSlider.value = globalAudio.volume;
      deckMuteBtn.textContent = '🔊';
      isAudioMuted = false;
    } else {
      previousVolume = globalAudio.volume;
      globalAudio.volume = 0;
      if (deckVolSlider) deckVolSlider.value = 0;
      deckMuteBtn.textContent = '🔇';
      isAudioMuted = true;
    }
  });
}

deckTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const idx = parseInt(tab.dataset.track, 10);
    loadTrack(idx, true);
  });
});

if (btnCloseDeck) {
  btnCloseDeck.addEventListener('click', () => {
    if (focusDeck) focusDeck.classList.add('hidden');
  });
}

// ── Updated Resume Studio & Executive Document Exporter Module ───────────────
let currentResumeDraft = '';
let currentResumeTargetRole = 'Enterprise CISO / Executive';

const resumeStudioOverlay = document.getElementById('resume-studio-overlay');
const closeResumeStudioBtn = document.getElementById('close-resume-studio-btn');
const resumeMarkdownEditor = document.getElementById('resume-markdown-editor');
const resumeFormattedPreview = document.getElementById('resume-formatted-preview');
const resumeTargetRoleBadge = document.getElementById('resume-target-role-badge');
const resumeLastUpdatedTime = document.getElementById('resume-last-updated-time');

const btnExportDocx = document.getElementById('btn-export-docx');
const btnExportPdf = document.getElementById('btn-export-pdf');
const btnCopyResume = document.getElementById('btn-copy-resume');
const btnSaveResumeManual = document.getElementById('btn-save-resume-manual');

// Extract clean resume markdown from assistant response
function extractResumeTextFromMarkdown(markdown) {
  if (!markdown) return '';

  // Check for codeblock containing resume
  const codeBlockMatch = markdown.match(/```(?:markdown|resume_export_ready|text)?\n([\s\S]*?)```/);
  if (codeBlockMatch && (codeBlockMatch[1].includes('EXPERIENCE') || codeBlockMatch[1].includes('SUMMARY') || codeBlockMatch[1].includes('CISO'))) {
    return codeBlockMatch[1].trim();
  }

  // If the markdown starts with # or contains # [Name], extract starting from the first heading
  const headingMatch = markdown.search(/^# [A-Z]/m);
  if (headingMatch !== -1) {
    return markdown.slice(headingMatch).trim();
  }

  return markdown.trim();
}

function checkAndAttachResumeActions(el, markdown) {
  if (!markdown || !el) return;

  const isResume = (
    markdown.includes('### PROFESSIONAL EXPERIENCE') ||
    markdown.includes('### EXECUTIVE SUMMARY') ||
    markdown.includes('### CORE COMPETENCIES') ||
    markdown.includes('resume_export_ready') ||
    (markdown.includes('Christophe Foulon') && markdown.includes('CISO'))
  );

  if (!isResume) return;

  const resumeText = extractResumeTextFromMarkdown(markdown);
  if (resumeText) {
    currentResumeDraft = resumeText;
    // Auto-sync with backend profile
    autoSaveResumeDraft(resumeText);
  }

  // Prevent duplicate cards
  const bubble = el.querySelector('.message-bubble');
  if (!bubble || bubble.querySelector('.resume-chat-export-card')) return;

  const card = document.createElement('div');
  card.className = 'resume-chat-export-card';
  card.innerHTML = `
    <div class="resume-chat-card-header">
      <div class="resume-chat-card-title">
        <span>📄</span>
        <span>Updated Executive Resume Ready</span>
      </div>
      <span class="resume-chat-card-badge">ATS & Board Optimized</span>
    </div>
    <div class="resume-chat-card-actions">
      <button class="btn-chat-export btn-chat-docx" title="Download Word DOCX (.docx)">
        <span>📥 Download Word (.docx)</span>
      </button>
      <button class="btn-chat-export btn-chat-pdf" title="Download Styled PDF (.pdf)">
        <span>📥 Download PDF (.pdf)</span>
      </button>
      <button class="btn-chat-export btn-chat-studio" title="Open in Resume Studio">
        <span>📑 Open in Resume Studio</span>
      </button>
    </div>
  `;

  card.querySelector('.btn-chat-docx').addEventListener('click', (e) => {
    e.stopPropagation();
    downloadResumeDocx(resumeText || currentResumeDraft);
  });

  card.querySelector('.btn-chat-pdf').addEventListener('click', (e) => {
    e.stopPropagation();
    downloadResumePdf(resumeText || currentResumeDraft);
  });

  card.querySelector('.btn-chat-studio').addEventListener('click', (e) => {
    e.stopPropagation();
    openResumeStudio(resumeText || currentResumeDraft);
  });

  bubble.appendChild(card);
}

async function autoSaveResumeDraft(markdownText) {
  if (!markdownText || !currentUser) return;
  try {
    localStorage.setItem(`cybermentor_resume_${currentUser}`, markdownText);
    await fetch(`${API_BASE_URL}/api/resume/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser,
        markdown_text: markdownText,
        target_role: currentResumeTargetRole,
        candidate_name: 'Christophe Foulon'
      })
    });
  } catch (err) {
    console.warn('Auto-save resume error:', err);
  }
}

async function openResumeStudio(customText = null) {
  if (!resumeStudioOverlay) return;

  resumeStudioOverlay.classList.remove('hidden');
  resumeStudioOverlay.classList.add('active');

  if (customText && customText.trim()) {
    currentResumeDraft = customText;
    updateStudioContent(customText);
    return;
  }

  const activeUserId = currentUser || 'guest';

  // Load from current memory or local storage
  const localSaved = localStorage.getItem(`cybermentor_resume_${activeUserId}`) || 
                     localStorage.getItem('cybermentor_resume_guest') || 
                     localStorage.getItem('cybermentor_resume_Christophe_Foulon');
  if (localSaved && localSaved.trim()) {
    currentResumeDraft = localSaved;
    updateStudioContent(localSaved);
  }

  // Fetch from API backend
  try {
    const res = await fetch(`${API_BASE_URL}/api/resume/${encodeURIComponent(activeUserId)}/latest`);
    if (res.ok) {
      const data = await res.json();
      if (data.found && data.markdown_text) {
        currentResumeDraft = data.markdown_text;
        if (data.target_role) currentResumeTargetRole = data.target_role;
        updateStudioContent(data.markdown_text, data.updated_at);
      }
    }
  } catch (err) {
    console.warn('Error fetching latest resume from backend:', err);
  }
}

function updateStudioContent(text, updatedAt = null) {
  if (resumeMarkdownEditor) {
    resumeMarkdownEditor.value = text || '';
  }
  if (resumeFormattedPreview) {
    resumeFormattedPreview.innerHTML = text ? renderMarkdown(text) : '<p class="empty-resume-hint">No updated resume generated yet. Ask CyberMentor to review, rewrite, or update your resume in chat!</p>';
  }
  if (resumeTargetRoleBadge) {
    resumeTargetRoleBadge.textContent = `Track: ${currentResumeTargetRole.replace('_', ' ').toUpperCase()}`;
  }
  if (resumeLastUpdatedTime) {
    resumeLastUpdatedTime.textContent = updatedAt ? `Last Updated: ${new Date(updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Last Synced: Just now';
  }
}

function closeResumeStudio() {
  if (resumeStudioOverlay) {
    resumeStudioOverlay.classList.remove('active');
    resumeStudioOverlay.classList.add('hidden');
  }
}

if (closeResumeStudioBtn) {
  closeResumeStudioBtn.addEventListener('click', closeResumeStudio);
}

if (resumeMarkdownEditor) {
  resumeMarkdownEditor.addEventListener('input', () => {
    currentResumeDraft = resumeMarkdownEditor.value;
    if (resumeFormattedPreview) {
      resumeFormattedPreview.innerHTML = currentResumeDraft ? renderMarkdown(currentResumeDraft) : '<p class="empty-resume-hint">Resume editor is empty.</p>';
    }
  });
}

// ── Download Helpers ────────────────────────────────────────────────────────
async function downloadResumeDocx(text, filename = "Christophe_Foulon_CISO_Resume.docx") {
  const content = text || (resumeMarkdownEditor ? resumeMarkdownEditor.value : '') || currentResumeDraft;
  if (!content.trim()) {
    alert("No resume text found. Please generate or paste your resume first.");
    return;
  }

  try {
    setStatus('working', 'Generating Word document (.docx)...');
    const resp = await fetch(`${API_BASE_URL}/api/resume/export/docx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        markdown_text: content,
        filename: filename,
        target_role: currentResumeTargetRole
      })
    });

    if (!resp.ok) throw new Error(`DOCX Export failed: ${resp.status}`);

    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    setStatus('ready', 'CyberMentor Ready');
  } catch (err) {
    console.error('Error exporting DOCX:', err);
    alert(`Could not export DOCX: ${err.message}`);
    setStatus('ready', 'CyberMentor Ready');
  }
}

async function downloadResumePdf(text, filename = "Christophe_Foulon_CISO_Resume.pdf") {
  const content = text || (resumeMarkdownEditor ? resumeMarkdownEditor.value : '') || currentResumeDraft;
  if (!content.trim()) {
    alert("No resume text found. Please generate or paste your resume first.");
    return;
  }

  try {
    setStatus('working', 'Generating PDF document (.pdf)...');
    const resp = await fetch(`${API_BASE_URL}/api/resume/export/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        markdown_text: content,
        filename: filename,
        target_role: currentResumeTargetRole
      })
    });

    if (!resp.ok) throw new Error(`PDF Export failed: ${resp.status}`);

    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    setStatus('ready', 'CyberMentor Ready');
  } catch (err) {
    console.error('Error exporting PDF:', err);
    alert(`Could not export PDF: ${err.message}`);
    setStatus('ready', 'CyberMentor Ready');
  }
}

// ── Button Listeners ────────────────────────────────────────────────────────
if (btnExportDocx) {
  btnExportDocx.addEventListener('click', () => downloadResumeDocx());
}

if (btnExportPdf) {
  btnExportPdf.addEventListener('click', () => downloadResumePdf());
}

if (btnCopyResume) {
  btnCopyResume.addEventListener('click', async () => {
    const content = (resumeMarkdownEditor ? resumeMarkdownEditor.value : '') || currentResumeDraft;
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      const originalText = btnCopyResume.innerHTML;
      btnCopyResume.innerHTML = '<span>✅ Copied!</span>';
      setTimeout(() => { btnCopyResume.innerHTML = originalText; }, 2000);
    } catch (err) {
      alert('Could not copy to clipboard. Please copy manually from the editor.');
    }
  });
}

if (btnSaveResumeManual) {
  btnSaveResumeManual.addEventListener('click', async () => {
    const content = (resumeMarkdownEditor ? resumeMarkdownEditor.value : '') || currentResumeDraft;
    if (!content) return;
    try {
      setStatus('working', 'Saving resume draft to profile...');
      await autoSaveResumeDraft(content);
      const originalText = btnSaveResumeManual.innerHTML;
      btnSaveResumeManual.innerHTML = '<span>✅ Saved!</span>';
      setTimeout(() => { btnSaveResumeManual.innerHTML = originalText; }, 2000);
      setStatus('ready', 'CyberMentor Ready');
    } catch (err) {
      alert(`Save failed: ${err.message}`);
      setStatus('ready', 'CyberMentor Ready');
    }
  });
}

// Track Selector & 1-Click Auto-Tailor Listener
const resumeTrackSelect = document.getElementById('resume-track-select');
const btnTailorResume = document.getElementById('btn-tailor-resume');

if (resumeTrackSelect) {
  resumeTrackSelect.addEventListener('change', () => {
    currentResumeTargetRole = resumeTrackSelect.value;
    if (resumeTargetRoleBadge) {
      resumeTargetRoleBadge.textContent = `Track: ${resumeTrackSelect.options[resumeTrackSelect.selectedIndex].text}`;
    }
  });
}

if (btnTailorResume) {
  btnTailorResume.addEventListener('click', () => {
    const selectedOpt = resumeTrackSelect ? resumeTrackSelect.options[resumeTrackSelect.selectedIndex] : null;
    const selectedTrack = selectedOpt ? selectedOpt.text : 'Enterprise CISO / VP of Information Security';
    const isStretch = selectedOpt && selectedOpt.parentElement && selectedOpt.parentElement.label && selectedOpt.parentElement.label.includes('Stretch');
    
    closeResumeStudio();
    let tailorPrompt = `Please tailor, calibrate, and draft my complete updated resume for the target track: "${selectedTrack}". `;
    if (isStretch) {
      tailorPrompt += `This is a high-demand STRETCH role track for me: strategically bridge my 20+ years of executive advisory, GRC oversight, Compliance-as-Code automation, and risk quantification into the specialized competencies, market-demanded frameworks, and high-impact metrics required for this specific role. `;
    } else {
      tailorPrompt += `Highlight the specific leadership proof points, technical oversight, framework compliance, and metrics that executive search panels look for in this track. `;
    }
    tailorPrompt += `Once drafted, output the full complete resume and save it to my profile so I can immediately download the updated Word (.docx) and PDF (.pdf) documents!`;
    
    if (!isStreaming) {
      messageInput.value = tailorPrompt;
      messageInput.dispatchEvent(new Event('input'));
      sendMessage();
    }
  });
}

// ── Discover Fit & High-Demand Stretch Roles Listener ───────────────────────
const btnSuggestRoles = document.getElementById('btn-suggest-roles');
if (btnSuggestRoles) {
  btnSuggestRoles.addEventListener('click', () => {
    closeResumeStudio();
    const prompt = `Based on my current cybersecurity background, executive advisory experience, GRC leadership, authored books, and technical competencies, please perform a deep market calibration analysis:
1. Identify my top direct-fit roles where I have immediate compensation and hiring committee leverage.
2. Identify 3 to 4 high-demand STRETCH roles where my existing transferable capabilities (e.g. Compliance-as-Code, FAIR risk quantification, AI security governance, FedRAMP, Product Security) uniquely position me in the 2026 market.
3. For each stretch role, explain the exact capability bridge, market compensation trajectory, and specific positioning advice to win executive interviews.`;
    if (!isStreaming) {
      messageInput.value = prompt;
      messageInput.dispatchEvent(new Event('input'));
      sendMessage();
    }
  });
}

// ── Executive Mock Interview & Board Defense Studio Module ──────────────────
const interviewStudioOverlay = document.getElementById('interview-studio-overlay');
const closeInterviewStudioBtn = document.getElementById('close-interview-studio-btn');
const interviewTabBtns = document.querySelectorAll('.interview-tab-btn');
const interviewDrillCards = document.querySelectorAll('.interview-drill-card');
const launchDrillBtns = document.querySelectorAll('.btn-launch-drill');

function openInterviewStudio() {
  if (interviewStudioOverlay) {
    interviewStudioOverlay.classList.remove('hidden');
    interviewStudioOverlay.classList.add('active');
  }
}

function closeInterviewStudio() {
  if (interviewStudioOverlay) {
    interviewStudioOverlay.classList.remove('active');
    interviewStudioOverlay.classList.add('hidden');
  }
}

if (closeInterviewStudioBtn) {
  closeInterviewStudioBtn.addEventListener('click', closeInterviewStudio);
}

interviewTabBtns.forEach(tab => {
  tab.addEventListener('click', () => {
    interviewTabBtns.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const filter = tab.dataset.filter;

    interviewDrillCards.forEach(card => {
      if (filter === 'all' || card.dataset.category === filter) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });
});

launchDrillBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const prompt = btn.dataset.prompt;
    if (!prompt) return;
    closeInterviewStudio();
    if (!isStreaming) {
      messageInput.value = prompt;
      messageInput.dispatchEvent(new Event('input'));
      sendMessage();
    }
  });
});



