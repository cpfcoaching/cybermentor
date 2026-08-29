# 🛡️ CyberMentor — Autonomous AI Cybersecurity Career Coach

> **Google Cloud All Things Agentic Hackathon** | Track: **The Collaborative Partner**  
> Built by **Christophe Foulon** | [Breaking Into Cybersecurity](https://breakingintocybersecurity.org)  
> Powered by **Google Antigravity SDK** · **Gemini 3.7** · **Google Cloud Run** · **Cloud Firestore**

[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-blue?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Google Cloud Firestore](https://img.shields.io/badge/Database-Cloud%20Firestore-orange?logo=firebase&logoColor=white)](https://firebase.google.com/docs/firestore)
[![Google Antigravity SDK](https://img.shields.io/badge/Agent%20SDK-Google%20Antigravity-teal)](https://github.com/google)
[![Gemini 3.7 Flash](https://img.shields.io/badge/AI%20Model-Gemini%203.7%20Flash-4285F4?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Zero External API Fees](https://img.shields.io/badge/Voice%20Engine-Zero%20API%20Cost-success)](docs/GOOGLE_VOICE_CLONING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌐 Live Production Links

| Resource | Live Link |
| :--- | :--- |
| **🚀 Live AI Coach Studio** | [`https://client.breakingintocybersecurity.org`](https://client.breakingintocybersecurity.org) |
| **🌐 Marketing Homepage** | [`https://client.breakingintocybersecurity.org/home.html`](https://client.breakingintocybersecurity.org/home.html) |
| **📚 Interactive API Docs (Swagger)** | [`https://client.breakingintocybersecurity.org/docs`](https://client.breakingintocybersecurity.org/docs) |
| **🎬 Master 5-Minute Demo Video** | [Watch on YouTube](https://youtu.be/ucU61U_IQ0w) |
| **📱 YouTube Social Shorts** | [Short 1: Tuition Savings](https://youtu.be/FemcUl7NHMI) · [Short 2: Security+ Roadmap](https://youtu.be/rcnGlY_Gv5o) · [Short 3: Skills Mindmap](https://youtu.be/0OLpHcjJyYE) · [Short 4: SOC Mock Interview](https://youtu.be/j5DPnaWebQo) |

---

## 📖 The Story & Mission

### The Mentorship Bottleneck in Cybersecurity

Every single week on the **Breaking Into Cybersecurity** podcast and community channels, aspiring security professionals ask the same question: *"I want to break into cybersecurity. Where do I start?"*

Over **7+ years, 1,164 podcast episodes, and hundreds of 1-on-1 coaching sessions**, the answer is always tailored to each person's specific background:

- An IT helpdesk technician should take a radically different path than an accountant moving into GRC.
- Generic advice on Reddit or social media is contradictory and overwhelming.
- Predatory bootcamps charge **$15,000+** for generic video playlists.
- Realistic mock interview drills with scored technical feedback are completely out of reach for self-taught learners.

### The Solution: An Autonomous Collaborative Partner

**CyberMentor** transforms 7+ years of real-world coaching methodology into a **persistent, evolving AI Collaborative Partner**. It is not a stateless chatbot. It is a 24/7 autonomous coach that:

1. Understands your technical and non-technical background.
2. Identifies adjacent transferable skills you forgot to list.
3. Calibrates customized week-by-week certification study plans to your available hours.
4. Drills you through realistic technical SOC incidents and behavioral interviews with objective rubric-based grading.
5. Remembers your progress across sessions using **Google Cloud Firestore**.
6. Speaks with a signature **Zero-Cost Island Boy neural voice profile** self-hosted directly on **Google Cloud Run**.

---

## 🏗️ Architecture & System Design

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER (Browser SPA & PWA)                       │
│    • Vanilla JS (Zero Framework Bloat)       • Glassmorphism Dark Theme         │
│    • Real-time SSE Token Streaming           • Interactive Skills Mindmap       │
│    • In-App Focus Audio Synthesizer          • Cloud SSO & MFA Device Check     │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ HTTPS / SSE (Cloudflare Edge Proxy)
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                   BACKEND API LAYER (Google Cloud Run Serverless)                │
│    • FastAPI + Uvicorn Async Server          • OWASP LLM01 Security Guardrails  │
│    • 8-Hour Session TTL & Fingerprint Check  • Sub-250ms Voice Synthesis Engine │
│                                                                                 │
│   ┌────────────────────────────────────────────────────────────────────────┐   │
│   │                      GOOGLE ANTIGRAVITY SDK AGENT                      │   │
│   │                         (agent/cybermentor.py)                         │   │
│   │                                                                        │   │
│   │   Deterministic Tool Execution Engine:                                 │   │
│   │   ├── query_knowledge_base()        ── 1,164-Episode YouTube RAG       │   │
│   │   ├── generate_study_plan()         ── Hour-Calibrated Cert Roadmaps   │   │
│   │   ├── analyze_resume()              ── NIST NICE Framework Skill Audit │   │
│   │   ├── get_interview_question()      ── Technical & Behavioral Scenarios│   │
│   │   ├── evaluate_answer()             ── 4-Pillar Rubric Scoring (0-10)  │   │
│   │   ├── ace_memory_recorder()         ── Cognitive Strategy Reflection   │   │
│   │   └── save/get_user_progress()      ── Lifelong Firestore Memory Sync  │   │
│   └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────┬──────────────────────────────────┬──────────────────────┘
                        │                                  │
            ┌───────────▼───────────┐          ┌───────────▼───────────┐
            │   GEMINI 3.7 FLASH    │          │ GOOGLE CLOUD FIRESTORE│
            │  (via Antigravity SDK)│          │  • User Profiles      │
            │  Deep Coaching Engine │          │  • Milestones & Notes │
            │  Mock Interview Scorer│          │  • Global Heuristics  │
            └───────────────────────┘          └───────────────────────┘
```

---

## 🌟 Key Capabilities & Innovations

### 1. 🗺️ Career Path Architect & Transferable Skills Mindmap

- Analyzes your unique background (IT, software, military, law, accounting, or non-technical).
- Translates non-security experience into **NIST NICE Framework Work Roles** (SOC Analyst, Penetration Tester, Cloud Security Engineer, GRC Specialist, CISO).
- Features an interactive **SVG Skills & Certifications Mindmap Explorer**.

### 2. 📅 Hour-Calibrated Study Planner

- Generates week-by-week certification schedules for **Security+, CySA+, CASP+, CEH, CISSP, eJPT, OSCP, AWS Security, and GCP Security**.
- Calibrates automatically to your exact available study hours per week (e.g. 5 hrs/wk vs 20 hrs/wk) with phase-by-phase resource breakdowns and buffer weeks.

### 3. 📄 NIST-Aligned Resume Analyzer & Document Parser

- Supports direct client-side parsing of **PDF, Microsoft Word (.docx), Markdown, and Plain Text resumes**.
- Performs automated gap analysis: detects missing tool keywords (Wireshark, Splunk, Linux, Python, NIST 800-53) and provides prioritized action items with an overall Readiness Score.

### 4. 🎤 Live Mock Interview Drills with Scored Rubrics

- Simulates realistic Tier 1/2 SOC incident triage scenarios (phishing escalation, malware beaconing, ransomware isolation) and behavioral leadership questions.
- Scores your response across four pillars: **Technical Accuracy, Methodology & Frameworks, Communication Clarity, and Security Mindset**.

### 5. 🎙️ Zero-Cost Cloud Run Voice Engine (Island Boy)

- Replaced costly third-party voice APIs with a self-hosted serverless neural voice engine running on Google Cloud Run.
- Delivers **sub-250ms voice streaming** at **$0.00 recurring external API fees**.
- In-app toggle: `🔊 Voice: ON (Island Boy)` speaks coaching responses in real time.

### 6. 🧠 Autonomous Agent with Continual Evolution (ACE Memory)

- Employs structured metacognitive memory reflection notes in Cloud Firestore.
- Remembers candidate certifications, study progress, and past interview weak spots across sessions.

### 7. 🎧 Focus Audio Synthesizer Studio

- Built-in Web Audio API binaural beats and ambient study soundscapes (Deep Focus Alpha 10Hz, Exam Crunch Beta 14Hz, Cyber SOC Schumann 7.83Hz, Cooldown Theta 6Hz).

---

## 🔐 Enterprise Security & Privacy Charter

- **Google SSO with Multi-Factor Authentication (MFA)**: Enforced OAuth 2.0 with biometric/hardware MFA support.
- **8-Hour Maximum Session Persistence**: Strict session TTL prevents unauthorized access on shared devices.
- **New Device Fingerprint Detection**: Connecting from an unrecognized device or browser fingerprint triggers an MFA challenge.
- **Automated 90-Day Dormant Profile Purge**: Profiles inactive for >90 days are permanently purged from Firestore to minimize storage costs and eliminate stale PII.
- **Anonymized System Learning**: Prior to purging, abstract non-PII pedagogical heuristics are preserved in `global_ace_heuristics` to continuously improve mentoring quality for future students.
- **OWASP LLM01–LLM10 Guardrails**: Input sandboxing, prompt injection barriers, and strict Firestore isolation rules (`request.auth.uid == userId`).

---

## 🚀 Quick Start & Local Setup

### Prerequisites

- Python 3.11 or 3.12
- Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/api-keys)

### 1. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/cpfcoaching/cybermentor.git
cd cybermentor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

*(Google Cloud Firestore automatically falls back to local JSON storage for zero-cloud local testing)*.

### 3. Start the Backend API

```bash
uvicorn api.main:app --reload --port 8080
```

### 4. Launch the Web Studio

```bash
# Open directly in your browser
open web/index.html

# Or serve locally
python -m http.server 3000 --directory web
# Visit http://localhost:3000
```

---

## ☁️ Deploying to Google Cloud Run

Deploy the entire containerized architecture with a single command:

```bash
# 1. Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Store your Gemini key in Secret Manager
echo -n "YOUR_GEMINI_API_KEY" | \
  gcloud secrets create cybermentor-gemini-key \
  --data-file=- \
  --project=YOUR_PROJECT_ID

# 3. Deploy
./deploy.sh
```

The script automatically:

- Enables Google Cloud Run, Cloud Build, and Cloud Firestore APIs.
- Builds the multi-stage Docker container with non-root security.
- Deploys the service to `us-central1` with automatic scale-to-zero.

---

## 📱 App Store Packaging & Distribution

CyberMentor is ready for distribution across all platforms:

- **Progressive Web App (PWA)**: Standalone installable app via Safari (*Add to Home Screen*) and Chrome (*Install App*).
- **Google Play Store**: Packaged via Bubblewrap / Trusted Web Activity (`.aab`) with **Closed Testing tracks for registered users only**.
- **Apple App Store**: Packaged via Capacitor / Xcode with **TestFlight & Unlisted Distribution for registered users only**.

👉 Full packaging instructions: [`docs/APP_STORE_PACKAGING_AND_GATING.md`](docs/APP_STORE_PACKAGING_AND_GATING.md)

---

## 🏆 Hackathon Submission Verification

| Requirement | Implementation Details | Status |
| :--- | :--- | :--- |
| **Gemini 3.5 / 3.7** | Vertex AI & Google Antigravity SDK default model | ✅ Verified |
| **Google Agent Framework** | Google Antigravity SDK with deterministic tool routing | ✅ Verified |
| **Google Cloud Services** | Google Cloud Run + Google Cloud Firestore | ✅ Live |
| **Hosted Project URL** | `https://client.breakingintocybersecurity.org` | ✅ Live |
| **Demo Video (~5 min)** | `https://youtu.be/ucU61U_IQ0w` | ✅ Uploaded |
| **4 Social Shorts (9:16)** | YouTube Shorts uploaded & linked in submission | ✅ Uploaded |
| **Veo & Lyria Bonus** | Ambient focus study synthesizer + video generation scripts | ✅ Implemented |
| **Gemma Bonus** | Fast resume skill extraction & two-tier pre-routing pipeline | ✅ Implemented |

---

## 📚 Co-Authored & Contributed Books by Christophe Foulon

The core coaching rubrics, career roadmaps, interview preparation scenarios, and risk quantification frameworks inside CyberMentor are directly derived from the published literature co-authored, authored, and contributed by Christophe Foulon:

1. **Develop Your Cybersecurity Career Path: How to Break into Cybersecurity at Any Level** *(Co-Author)*  
   📖 [Available on Amazon (Paperback & Kindle)](https://www.amazon.com/dp/1955976007/) — Practical roadmap for transitioning from non-traditional or IT backgrounds into cybersecurity.
2. **Hack the Cybersecurity Interview: A complete interview preparation guide for jumpstarting your cybersecurity career** *(Co-Author)*  
   📖 [Available on Amazon (Packt Publishing)](https://www.amazon.com/Hack-Cybersecurity-Interview-Interviews-Entry-level/dp/1835461298/) — Master technical, behavioral, and situational cybersecurity interviews.
3. **Understand, Manage, and Measure Cyber Risk: Practical Solutions for Creating a Sustainable Cyber Program** *(Contributing Author)*  
   📖 [Available on Springer Nature / Apress](https://link.springer.com/book/10.1007/978-1-4842-9319-5) — Enterprise risk frameworks, executive communication, and practical FAIR risk quantification.
4. **Hacker Inc.: Mindset For Your Career** *(Co-authored with Renee Small)*  
   📖 [Available on Amazon](https://www.amazon.com/Hacker-Inc-Mindset-Your-Career/dp/B0DKTK1R93/) — Cultivating curiosity, adaptability, offensive thinking, and long-term career resilience.
5. **The Cybersecurity Advantage: How SMB Leaders Leverage Fractional Executive Guidance to Build Trust, Win Business, and Drive Growth** *(Author)*  
   📖 [Available on Leanpub](https://leanpub.com/the-cybersecurity-advantage) — Fractional CISO advisory, executive trust, and strategic cyber program leadership for growth.

---

## 👤 Author & Acknowledgments

Built with ❤️ by **Christophe Foulon**  
Founder & Host, [Breaking Into Cybersecurity](https://breakingintocybersecurity.org)  
Coaching & Mentorship: [CPF Coaching](https://www.buymeacoffee.com/cpf_coaching)

*Dedicated to helping aspiring cybersecurity professionals break in, level up, and thrive.*
