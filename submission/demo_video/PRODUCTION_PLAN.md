# 🎬 CyberMentor Faceless Demo Video Production Plan

> **Format:** 100% Faceless Walkthrough & Screen Capture
> **Voiceover:** ElevenLabs "Island Boy" / Caribbean voice profile for Christophe Foulon
> **Video Production:** Google AI tools (Google Veo B-roll + Antigravity SDK UI live capture)
> **Target Run Time:** 4 minutes (240 seconds)

---

## 🎙️ 1. Voiceover Generation (ElevenLabs)

Generate audio files per scene using the exact text from [`narration_script.json`](narration_script.json):

| File | Scene Title | Duration | Voice Prompt / Text |
|---|---|---|---|
| `scene1_intro.mp3` | Introduction & Challenge | ~45s | *"Breaking into cybersecurity is tough because generic advice fails. Why did the router go to therapy? It had too many unresolved connections..."* |
| `scene2_study_resume.mp3` | Study Plans & Resume Audits | ~60s | *"CyberMentor delivers structured, actionable guidance rather than generic answers. When you share your background in IT helpdesk..."* |
| `scene3_sdk_routing.mp3` | Antigravity SDK & Gemma Routing | ~45s | *"CyberMentor runs on the Google Antigravity SDK, using explicit tool docstrings for deterministic routing instead of brittle prompt chains..."* |
| `scene4_podcast_rag.mp3` | 1,164-Episode RAG & Voice Drills | ~60s | *"CyberMentor is backed by seven years of real-world industry insights. Why do red teamers make terrible secret keepers? Because they always crack under pressure..."* |
| `scene5_cloudrun_cta.mp3` | Cloud Run & Live Call to Action | ~30s | *"CyberMentor runs completely serverless on Google Cloud Run with persistent cross-session memory in Cloud Firestore..."* |

---

## 🎥 2. Visual Layer & B-Roll Pipeline

| Scene | Visual Source | On-Screen Action |
|---|---|---|
| **Scene 1 (0:00–0:45)** | [`web/img/hero_banner.jpg`](../web/img/hero_banner.jpg) + Google Veo B-roll | Cyber operations center cinematic clip (`veo-2.0-generate-001`) with title overlay. |
| **Scene 2 (0:45–1:45)** | Live Web UI (`/`) | Live screen capture: Career Path selection $\rightarrow$ Security+ 8 hr/week study plan streaming $\rightarrow$ PDF/DOCX resume drag-and-drop audit. |
| **Scene 3 (1:45–2:30)** | Cloud Console + Architecture | Google Cloud Run dashboard + Cloud Firestore console + Antigravity SDK agent diagram showing Gemma 3 / Gemini 3.7 two-tier routing. |
| **Scene 4 (2:30–3:30)** | Live Web UI Mock Interview | Click microphone icon $\rightarrow$ voice answer prompt $\rightarrow$ instant rubric evaluation with score and model answer. |
| **Scene 5 (3:30–4:00)** | Web UI Refresh + Outro Card | Refresh browser $\rightarrow$ show persistent milestone recovery from Cloud Firestore $\rightarrow$ closing screen with live URL and GitHub links. |

---

## 🛠️ 3. Assembly & Export Checklist

- [ ] Generate 5 MP3 audio tracks in ElevenLabs.
- [ ] Record screen captures of the live Cloud Run application: `https://cybermentor-1019457807345.us-central1.run.app`.
- [ ] Add background focus music generated via Google Lyria (or the built-in CyberMentor synthwave track).
- [ ] Align audio cuts to scene timestamps (0:45, 1:45, 2:30, 3:30, 4:00).
- [ ] Export final video in 1080p 60fps (16:9 format).
- [ ] Upload to YouTube / Loom as a **Public** video and add the link into `SUBMISSION.md`.
