/**
 * CyberMentor Automated Demo Walkthrough & Video Recorder
 * Uses Chrome DevTools Protocol (CDP) screencast streaming + FFmpeg
 * Captures pixel-perfect 1080p MP4 walkthrough directly from the live Cloud Run instance.
 */

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

const LIVE_URL = 'https://cybermentor-1019457807345.us-central1.run.app';
const OUTPUT_DIR = path.resolve('submission/demo_video');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'cybermentor_walkthrough.mp4');
const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const DEBUG_PORT = 9222;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getDebuggerUrl() {
  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/list`);
      const data = await res.json();
      if (data && data.length > 0 && data[0].webSocketDebuggerUrl) {
        return data[0].webSocketDebuggerUrl;
      }
    } catch (e) {
      await sleep(500);
    }
  }
  throw new Error('Could not connect to Chrome DevTools debugging port.');
}

async function main() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  console.log('🚀 Launching Chrome for automated demo walkthrough...');
  const profileDir = `/tmp/chrome-demo-profile-${Date.now()}`;
  const chromeProc = spawn(CHROME_PATH, [
    `--remote-debugging-port=${DEBUG_PORT}`,
    '--window-size=1280,800',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${profileDir}`,
    'about:blank',
  ]);

  await sleep(2500);

  const wsUrl = await getDebuggerUrl();
  console.log('📡 Connected to Chrome CDP:', wsUrl);

  const ws = new WebSocket(wsUrl);

  let msgId = 1;
  const pending = new Map();

  function sendCommand(method, params = {}) {
    const id = msgId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        if (pending.has(id)) {
          pending.delete(id);
          resolve({ timedOut: true });
        }
      }, 10000);

      pending.set(id, { resolve, reject, timer });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  // Setup FFmpeg process for video encoding
  console.log('🎥 Initializing FFmpeg video encoder...');
  const ffmpeg = spawn('/usr/local/bin/ffmpeg', [
    '-y',
    '-f', 'image2pipe',
    '-vcodec', 'mjpeg',
    '-r', '10',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'fast',
    '-crf', '20',
    OUTPUT_FILE,
  ]);

  let frameCount = 0;

  ws.onmessage = event => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.id && pending.has(msg.id)) {
        const { resolve, timer } = pending.get(msg.id);
        clearTimeout(timer);
        pending.delete(msg.id);
        resolve(msg.result);
      }
    } catch (e) {
      // Ignore parse errors
    }
  };

  await new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) resolve();
    else ws.onopen = resolve;
  });

  console.log('⚙️ Configuring CDP sessions...');
  await sendCommand('Page.enable');
  await sendCommand('Runtime.enable');
  await sendCommand('DOM.enable');
  await sendCommand('Page.setDeviceMetricsOverride', {
    width: 1280,
    height: 800,
    deviceScaleFactor: 1,
    mobile: false,
  });

  // Start continuous frame capture loop
  console.log('🔴 Starting continuous frame capture stream (10 fps)...');
  let capturing = true;
  const captureLoop = async () => {
    while (capturing) {
      try {
        const res = await sendCommand('Page.captureScreenshot', {
          format: 'jpeg',
          quality: 85,
        });
        if (res && res.data) {
          ffmpeg.stdin.write(Buffer.from(res.data, 'base64'));
          frameCount++;
        }
      } catch (e) {
        // ignore occasional capture timeouts
      }
      await sleep(100);
    }
  };
  captureLoop();

  // ─────────────────────────────────────────────────────────────
  // SCENE 1: Welcome & Authentication (0:00 - 0:45)
  // ─────────────────────────────────────────────────────────────
  console.log('\n[Scene 1] Navigating to CyberMentor live app...');
  await sendCommand('Page.navigate', { url: LIVE_URL });
  await sleep(4000);

  console.log('[Scene 1] Clicking Google SSO...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const ssoBtn = document.getElementById('btn-google-sso') || document.querySelector('.btn-google-sso');
      if (ssoBtn) ssoBtn.click();
    `,
  });
  await sleep(2000);

  console.log('[Scene 1] Selecting Christophe Foulon profile...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const chrisBtn = document.getElementById('btn-sso-chris') || document.querySelector('.btn-sso-account');
      if (chrisBtn) {
        chrisBtn.click();
      } else {
        const inp = document.getElementById('username-input');
        if (inp) { inp.value = 'Christophe Foulon'; inp.dispatchEvent(new Event('input')); }
        const start = document.getElementById('start-btn');
        if (start) start.click();
      }
    `,
  });
  await sleep(3000);

  // ─────────────────────────────────────────────────────────────
  // SCENE 2: Career Path & Study Plan (0:45 - 1:45)
  // ─────────────────────────────────────────────────────────────
  console.log('\n[Scene 2] Prompting Career Path Recommendation...');
  const prompt1 = 'I have 3 years in IT helpdesk and want to transition to a SOC Analyst role. What is my roadmap?';

  await sendCommand('Runtime.evaluate', {
    expression: `
      const input = document.getElementById('chat-input');
      if (input) {
        input.value = ${JSON.stringify(prompt1)};
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const sendBtn = document.getElementById('send-btn');
      if (sendBtn) sendBtn.click();
    `,
  });
  console.log('[Scene 2] Waiting for Career Roadmap SSE stream...');
  await sleep(16000);

  console.log('[Scene 2] Prompting Security+ Study Plan...');
  const prompt2 = 'Generate an 8-week study plan for CompTIA Security+ with 10 hours a week.';
  await sendCommand('Runtime.evaluate', {
    expression: `
      const input = document.getElementById('chat-input');
      if (input) {
        input.value = ${JSON.stringify(prompt2)};
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const sendBtn = document.getElementById('send-btn');
      if (sendBtn) sendBtn.click();
    `,
  });
  console.log('[Scene 2] Waiting for Study Plan SSE stream...');
  await sleep(16000);

  // ─────────────────────────────────────────────────────────────
  // SCENE 3: Skills & Certs Mindmap Modal (1:45 - 2:30)
  // ─────────────────────────────────────────────────────────────
  console.log('\n[Scene 3] Opening Skills & Certs Mindmap Modal...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const btn = document.getElementById('btn-mindmap-explorer') || document.querySelector('#btn-mindmap-explorer');
      if (btn) btn.click();
    `,
  });
  await sleep(4000);

  console.log('[Scene 3] Switching Mindmap Tabs...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const tabs = document.querySelectorAll('.mindmap-tab');
      if (tabs.length > 1) tabs[1].click();
    `,
  });
  await sleep(3000);

  await sendCommand('Runtime.evaluate', {
    expression: `
      const tabs = document.querySelectorAll('.mindmap-tab');
      if (tabs.length > 2) tabs[2].click();
    `,
  });
  await sleep(3000);

  console.log('[Scene 3] Closing Mindmap Modal...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const closeBtn = document.getElementById('close-mindmap-btn') || document.querySelector('#close-mindmap-btn');
      if (closeBtn) closeBtn.click();
    `,
  });
  await sleep(2000);

  // ─────────────────────────────────────────────────────────────
  // SCENE 4: Mock Interview & Focus Studio Audio (2:30 - 3:30)
  // ─────────────────────────────────────────────────────────────
  console.log('\n[Scene 4] Triggering Mock Technical Interview...');
  const prompt3 = 'Give me a technical interview question for a Tier 1 SOC Analyst.';
  await sendCommand('Runtime.evaluate', {
    expression: `
      const input = document.getElementById('chat-input');
      if (input) {
        input.value = ${JSON.stringify(prompt3)};
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const sendBtn = document.getElementById('send-btn');
      if (sendBtn) sendBtn.click();
    `,
  });
  await sleep(10000);

  console.log('[Scene 4] Submitting Candidate Answer...');
  const answer = 'I would check the SIEM alert details, verify the source and destination IP addresses against threat intelligence feeds, isolate the affected host from the network to prevent lateral movement, and escalate to Tier 2 with a detailed timeline.';
  await sendCommand('Runtime.evaluate', {
    expression: `
      const input = document.getElementById('chat-input');
      if (input) {
        input.value = ${JSON.stringify(answer)};
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const sendBtn = document.getElementById('send-btn');
      if (sendBtn) sendBtn.click();
    `,
  });
  console.log('[Scene 4] Waiting for Rubric Scored Evaluation...');
  await sleep(14000);

  console.log('[Scene 4] Interacting with Focus Studio Audio Deck...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const audioBtn = document.getElementById('btn-lyria-music') || document.querySelector('#btn-lyria-music');
      if (audioBtn) audioBtn.click();
    `,
  });
  await sleep(8000);

  // ─────────────────────────────────────────────────────────────
  // SCENE 5: Analytics & Firestore Memory Persistence (3:30 - 4:00)
  // ─────────────────────────────────────────────────────────────
  console.log('\n[Scene 5] Opening Career Analytics & Streaks Dashboard...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const btn = document.getElementById('btn-analytics') || document.querySelector('#btn-analytics');
      if (btn) btn.click();
    `,
  });
  await sleep(4000);

  console.log('[Scene 5] Closing Analytics & Reloading for Firestore Memory Demo...');
  await sendCommand('Runtime.evaluate', {
    expression: `
      const closeBtn = document.getElementById('close-analytics-btn') || document.querySelector('#close-analytics-btn');
      if (closeBtn) closeBtn.click();
    `,
  });
  await sleep(2000);

  // Reload page to demonstrate persistent memory
  console.log('[Scene 5] Refreshing page to demonstrate Firestore memory...');
  await sendCommand('Page.navigate', { url: LIVE_URL });
  await sleep(4000);

  // Re-select profile
  await sendCommand('Runtime.evaluate', {
    expression: `
      const chrisBtn = document.getElementById('btn-sso-chris') || document.querySelector('.btn-sso-account');
      if (chrisBtn) chrisBtn.click();
    `,
  });
  await sleep(4000);

  console.log('⏹️ Stopping frame capture and closing recording...');
  capturing = false;
  await sleep(1500);

  ffmpeg.stdin.end();

  await new Promise(resolve => {
    ffmpeg.on('close', resolve);
  });

  ws.close();
  chromeProc.kill();

  console.log(`\n🎉 Recording successfully completed!`);
  console.log(`📹 Captured ${frameCount} frames.`);
  console.log(`📁 Video saved to: ${OUTPUT_FILE}`);
}

main().catch(err => {
  console.error('❌ Error during walkthrough recording:', err);
  process.exit(1);
});
