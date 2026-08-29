/**
 * CyberMentor Master 5-Minute Walkthrough Video Recorder & Audio-Video Synchronizer
 * Uses Playwright Chromium (1920x1080) with live, choreographed UI actions
 * and FFmpeg to produce a production-grade 1080p demo walkthrough with timed voice narration.
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const BASE_URL = 'https://cybermentor-1019457807345.us-central1.run.app';
const AUDIO_DIR = path.resolve('submission/demo_video/audio_scenes');
const OUT_DIR = path.resolve('submission/demo_video');
const MANIFEST_PATH = path.join(AUDIO_DIR, 'manifest_full.json');

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function smoothScroll(page, targetY, durationMs = 1500) {
  await page.evaluate(async ({ targetY, durationMs }) => {
    const startY = window.scrollY;
    const diff = targetY - startY;
    const startTime = performance.now();

    return new Promise(resolve => {
      function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / durationMs, 1);
        const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
        window.scrollTo(0, startY + diff * ease);
        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          resolve();
        }
      }
      requestAnimationFrame(step);
    });
  }, { targetY, durationMs });
  await sleep(400);
}

async function typeNaturally(page, selector, text, totalDurationMs = 2500) {
  const delay = Math.max(15, Math.floor(totalDurationMs / text.length));
  await page.click(selector);
  for (const char of text) {
    await page.keyboard.type(char, { delay: Math.floor(delay * (0.8 + Math.random() * 0.4)) });
  }
}

function runSubprocess(cmd) {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd[0], cmd.slice(1), { stdio: 'inherit' });
    proc.on('close', code => {
      if (code === 0) resolve();
      else reject(new Error(`Process exited with code ${code}`));
    });
  });
}

async function main() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
  console.log('📋 Loaded 5-scene audio manifest:');
  manifest.forEach(m => console.log(`  Scene ${m.id}: ${m.duration.toFixed(2)}s — ${m.title}`));

  // Clean old raw videos
  const rawDir = path.join(OUT_DIR, 'raw_video');
  if (fs.existsSync(rawDir)) {
    fs.rmSync(rawDir, { recursive: true, force: true });
  }
  fs.mkdirSync(rawDir, { recursive: true });

  console.log('\n🚀 Launching Playwright Chromium (1920x1080 60fps)...');
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: {
      dir: rawDir,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();

  // ───────────────────────────────────────────────────────────────────────────
  // SCENE 1: Introduction, Problem Statement & Homepage Tour (Target: ~56s)
  // ───────────────────────────────────────────────────────────────────────────
  console.log('\n🎬 Recording Scene 1: Homepage, ROI Statements & Value Pillars...');
  const scene1Start = Date.now();
  await page.goto(`${BASE_URL}/home.html`, { waitUntil: 'networkidle' });
  await sleep(3000);

  // Smooth scroll down to 6 Capability Cards
  await smoothScroll(page, 750, 2500);
  await sleep(5000);

  // Smooth scroll to ROI Comparison Matrix
  await smoothScroll(page, 1550, 2500);
  await sleep(7000);

  // Smooth scroll to Product Tour & Architecture Section
  await smoothScroll(page, 2450, 2500);
  await sleep(7000);

  // Smooth scroll to FAQ & Hackathon Story
  await smoothScroll(page, 3450, 2500);
  await sleep(7000);

  // Smooth scroll back to Hero
  await smoothScroll(page, 0, 2000);
  await sleep(2500);

  const scene1Elapsed = (Date.now() - scene1Start) / 1000;
  const scene1Target = manifest[0].duration;
  if (scene1Elapsed < scene1Target) {
    await sleep((scene1Target - scene1Elapsed) * 1000);
  }

  // ───────────────────────────────────────────────────────────────────────────
  // SCENE 2: Entering Studio, NIST NICE Mapping & Study Plan (Target: ~57s)
  // ───────────────────────────────────────────────────────────────────────────
  console.log('\n🎬 Recording Scene 2: Entering Studio, Google SSO & Study Plan...');
  const scene2Start = Date.now();
  await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
  await sleep(2500);

  // Authenticate with Google SSO
  console.log('  → Signing in with Google SSO account...');
  const googleBtn = await page.$('#google-sso-btn');
  if (googleBtn) {
    await googleBtn.click();
    await sleep(1500);
    const chrisAccountBtn = await page.$('#btn-sso-chris');
    if (chrisAccountBtn) {
      await chrisAccountBtn.click();
      await sleep(2500);
    }
  }

  // Trigger Career Path Roadmap prompt
  console.log('  → Triggering Career Path Roadmap prompt...');
  const careerBtn = await page.$('#btn-career-path');
  if (careerBtn && await careerBtn.isVisible()) {
    await careerBtn.click();
  } else {
    await typeNaturally(page, '#message-input', 'I have 2 years of IT helpdesk experience and want to transition to a SOC Analyst role. What is my roadmap?', 2000);
    await page.click('#send-btn');
  }
  await sleep(14000);

  // Send Study Plan request
  console.log('  → Requesting Certification Study Planner for Security+...');
  await typeNaturally(page, '#message-input', 'Generate an hour-calibrated 6-week study plan for CompTIA Security+ SY0-701 with lab recommendations.', 2500);
  await page.click('#send-btn');
  await sleep(14000);

  const scene2Elapsed = (Date.now() - scene2Start) / 1000;
  const scene2Target = manifest[1].duration;
  if (scene2Elapsed < scene2Target) {
    await sleep((scene2Target - scene2Elapsed) * 1000);
  }

  // ───────────────────────────────────────────────────────────────────────────
  // SCENE 3: Antigravity SDK, Gemma Routing & Interactive Mindmap (Target: ~49s)
  // ───────────────────────────────────────────────────────────────────────────
  console.log('\n🎬 Recording Scene 3: Antigravity SDK Routing & Mindmap Modal...');
  const scene3Start = Date.now();

  // Open Mindmap Modal
  const mindmapBtn = await page.$('#btn-mindmap');
  if (mindmapBtn) {
    await mindmapBtn.click();
    await sleep(3000);

    // Switch across tabs inside mindmap modal
    const tabs = await page.$$('.mindmap-tab');
    for (const tab of tabs) {
      await tab.click();
      await sleep(3000);
    }

    const closeBtn = await page.$('#close-mindmap-btn');
    if (closeBtn) await closeBtn.click();
    await sleep(2000);
  }

  // Open Analytics Modal
  const analyticsBtn = await page.$('#btn-analytics');
  if (analyticsBtn) {
    await analyticsBtn.click();
    await sleep(4000);
    const closeAnalytics = await page.$('#close-analytics-btn');
    if (closeAnalytics) await closeAnalytics.click();
    await sleep(2000);
  }

  const scene3Elapsed = (Date.now() - scene3Start) / 1000;
  const scene3Target = manifest[2].duration;
  if (scene3Elapsed < scene3Target) {
    await sleep((scene3Target - scene3Elapsed) * 1000);
  }

  // ───────────────────────────────────────────────────────────────────────────
  // SCENE 4: 1,164-Episode RAG & Scored Mock Interview Drill (Target: ~51s)
  // ───────────────────────────────────────────────────────────────────────────
  console.log('\n🎬 Recording Scene 4: 1,164-Episode RAG Insights & Scored Mock Interview...');
  const scene4Start = Date.now();

  // Ask mock interview scenario
  await typeNaturally(page, '#message-input', 'Can you drill me on a Tier 1 SOC phishing incident response interview question?', 2200);
  await page.click('#send-btn');
  await sleep(14000);

  // Submit candidate answer
  await typeNaturally(page, '#message-input', 'I inspect email headers for SPF/DKIM, analyze the attachment in a sandbox, extract IOCs, block malicious IPs on the firewall, and purge related emails across all inboxes.', 3000);
  await page.click('#send-btn');
  await sleep(16000);

  const scene4Elapsed = (Date.now() - scene4Start) / 1000;
  const scene4Target = manifest[3].duration;
  if (scene4Elapsed < scene4Target) {
    await sleep((scene4Target - scene4Elapsed) * 1000);
  }

  // ───────────────────────────────────────────────────────────────────────────
  // SCENE 5: Cloud Run Serverless, Firestore Persistence & Outro (Target: ~36s)
  // ───────────────────────────────────────────────────────────────────────────
  console.log('\n🎬 Recording Scene 5: Ambient Audio Player, Firestore Persistence & Outro...');
  const scene5Start = Date.now();

  // Toggle ambient focus beats
  const audioBtn = await page.$('#btn-focus-music');
  if (audioBtn) {
    await audioBtn.click();
    await sleep(3000);
  }

  // Scroll smoothly through entire session history to showcase persistent state
  await page.evaluate(() => {
    const messages = document.querySelector('#messages');
    if (messages) messages.scrollTo({ top: 0, behavior: 'smooth' });
  });
  await sleep(3500);

  await page.evaluate(() => {
    const messages = document.querySelector('#messages');
    if (messages) messages.scrollTo({ top: messages.scrollHeight, behavior: 'smooth' });
  });
  await sleep(4000);

  const scene5Elapsed = (Date.now() - scene5Start) / 1000;
  const scene5Target = manifest[4].duration;
  if (scene5Elapsed < scene5Target) {
    await sleep((scene5Target - scene5Elapsed) * 1000);
  }

  // Close browser
  console.log('🛑 Finalizing browser recording session...');
  await page.close();
  await context.close();
  await browser.close();

  // Get raw recorded video
  const files = fs.readdirSync(rawDir).filter(f => f.endsWith('.webm'));
  if (files.length === 0) {
    throw new Error('No raw webm video found in raw_video directory.');
  }

  const rawVideoPath = path.join(rawDir, files[0]);
  console.log('📹 Raw video recorded successfully:', rawVideoPath);

  // Mux video and audio
  await muxMasterAudioVideo(rawVideoPath, manifest);
}

async function muxMasterAudioVideo(rawVideoPath, manifest) {
  const finalOutput = path.join(OUT_DIR, 'cybermentor_walkthrough.mp4');

  const audioFiles = manifest.map(m => path.resolve(m.file));
  const concatAudioList = path.join(AUDIO_DIR, 'audio_concat_full.txt');
  fs.writeFileSync(concatAudioList, audioFiles.map(p => `file '${p}'`).join('\n'));

  const fullNarration = path.join(AUDIO_DIR, 'full_narration_5min.mp3');
  console.log('🎵 Stitching 5-scene narration audio...');
  await runSubprocess([
    '/usr/local/bin/ffmpeg', '-y',
    '-f', 'concat', '-safe', '0',
    '-i', concatAudioList,
    '-c', 'copy',
    fullNarration
  ]);

  const bgMusic = path.resolve('web/audio/track1_deep_focus_alpha.wav');

  console.log('\n🎞️ Rendering master 1080p 60fps MP4 walkthrough with timed narration & ambient focus beats...');
  const ffmpegCmd = [
    '/usr/local/bin/ffmpeg', '-y',
    '-i', rawVideoPath,
    '-i', fullNarration,
    '-i', bgMusic,
    '-filter_complex',
    '[1:a]volume=1.0[voice];[2:a]volume=0.10,aloop=loop=-1:size=2e+09[bg];[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]',
    '-map', '0:v:0',
    '-map', '[aout]',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-shortest',
    finalOutput
  ];

  await runSubprocess(ffmpegCmd);
  const sizeMb = (fs.statSync(finalOutput).size / (1024 * 1024)).toFixed(2);
  console.log(`\n🎉 MASTER 5-MINUTE WALKTHROUGH PRODUCED: ${finalOutput} (${sizeMb} MB)`);
}

main().catch(err => {
  console.error('❌ Master recording error:', err);
  process.exit(1);
});
