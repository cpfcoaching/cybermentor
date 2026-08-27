# CyberMentor — Hackathon Submission

> **All Things Agentic Hackathon** | Track: **The Collaborative Partner**
> Submitted by: Christophe Foulon | [Breaking Into Cyber](https://breakingintocyber.com)

---

## 📋 Category

**The Collaborative Partner**

CyberMentor is an interactive AI expert that guides aspiring cybersecurity professionals through one of the most daunting career transitions they'll face. It asks the right questions to understand where you are, remembers everything it learns about your goals and progress, and gets measurably better at coaching you the more you interact with it. It is not a chatbot — it is a persistent, evolving co-pilot for your career.

---

## 🌐 Hosted Project URL

> **Live URL:** [https://cybermentor-1019457807345.us-central1.run.app](https://cybermentor-1019457807345.us-central1.run.app)
> **API Docs:** [https://cybermentor-1019457807345.us-central1.run.app/docs](https://cybermentor-1019457807345.us-central1.run.app/docs)

The project is live on Google Cloud Run and integrated with Cloud Firestore. See [Spin-up Instructions](#-spin-up-instructions) below.

---

## 📝 Text Description

### The Problem

Breaking into cybersecurity is genuinely hard — and not because the field is inaccessible. It's hard because the information landscape is overwhelming and deeply contradictory:

- A Reddit thread tells you to get OSCP first. A YouTube video says Security+ is a waste of money. A LinkedIn post says you need a degree. A bootcamp charges $15,000 to tell you to "just do TryHackMe."
- Career changers don't know which role fits their background — should someone from accounting go into GRC? Should an IT admin pivot to SOC or cloud security?
- Study plans are generic. "Read this book" doesn't account for whether you have 5 hours a week or 25, or whether you're a visual learner who needs labs over textbooks.
- Interview prep is scattered. Mock interviews cost money, and there's no feedback loop when you practice alone.
- Progress is invisible. Without someone tracking your wins and reminding you how far you've come, it's easy to quit.

I've spent years at [Breaking Into Cyber](https://breakingintocyber.com) helping people navigate exactly this — through YouTube content, mentorship, and courses. CyberMentor is the autonomous agent version of that work: available 24/7, personalized to each user, and powered by the same content and philosophy that's already helped thousands of people break in.

---

### The Solution: CyberMentor

CyberMentor is an AI career coaching agent built on the Google Antigravity SDK and Gemini 3.5. It operates as a true collaborative partner — not a one-shot Q&A tool, but a session-aware, memory-persistent coach that builds a model of each user over time.

**It does five things exceptionally well:**

#### 1. 🗺️ Career Path Advisor
CyberMentor asks about your background (IT experience, education, current role) and your goals, then maps you to the right cybersecurity career track: SOC Analyst, Penetration Tester, GRC, Cloud Security, or CISO path. It explains the day-to-day realities of each role, the typical hiring requirements, and the realistic salary range — so you make an informed decision, not one driven by hype.

#### 2. 📅 Personalized Study Planner
Once a target certification is chosen (Security+, CISSP, OSCP, CySA+, eJPT, and more), CyberMentor generates a week-by-week study plan calibrated to your available hours per week and your current experience level. It phases the study into foundations, domain coverage, practice exams, and a final review buffer — with specific resource recommendations for each phase.

#### 3. 📄 Resume Analyzer
Users paste their resume text and CyberMentor performs a gap analysis: Which certifications are present? Which security tools are named? Are achievements quantified with metrics? Is the language tailored to cybersecurity job descriptions? It returns a scored assessment (out of 100) with prioritized action items.

#### 4. 🎤 Interview Coach
CyberMentor drills users on real interview questions for their target role — both technical (explain IDS vs IPS, walk me through incident response) and behavioral (tell me about a time you had to escalate a critical issue). After each answer, it evaluates the response against a rubric of key points, scores it out of 10, identifies gaps, and provides a model answer template.

#### 5. 🧠 Persistent Memory (Firestore)
Every session is remembered. When a user returns, CyberMentor loads their progress history and personalized profile from Firestore, picking up exactly where they left off. Completed milestones (passed a practice exam, earned a cert, landed a job interview) are logged and surfaced in the UI's progress sidebar. The agent gets measurably more useful over time as it accumulates context about each individual user.

---

### Technologies Used

| Component | Technology |
|---|---|
| **AI Agent Framework** | Google Antigravity SDK |
| **AI Model** | Gemini 3.5 Flash (via Antigravity SDK default) |
| **Persistent Memory** | Google Cloud Firestore (Enterprise edition) |
| **Deployment** | Google Cloud Run (containerized FastAPI) |
| **Backend API** | Python 3.12 + FastAPI + Server-Sent Events (SSE) |
| **Frontend** | Vanilla HTML/CSS/JS — glassmorphism dark UI |
| **Knowledge Base** | Curated JSON (certifications, career paths, interview Q&As) |
| **Optional RAG** | YouTube transcript ingestion via `data/scripts/ingest_youtube.py` |
| **Container** | Docker (multi-stage, non-root user) |
| **Secret Management** | Google Cloud Secret Manager |

---

### Data Sources Used

1. **Curated Cybersecurity Knowledge Base** — Hand-crafted JSON data covering:
   - 9 major certifications (Security+, CySA+, CASP+, CEH, CISSP, eJPT, OSCP, AWS Security, GCP Security) with exam details, domains, study resources, and breaking-into-cyber-specific notes
   - 5 career path guides (SOC Analyst, Penetration Tester, GRC, Cloud Security, CISO) with day-to-day realities, salary ranges, and required skills
   - 300+ interview questions across roles with key evaluation rubrics

2. **Breaking Into Cyber Content (optional, via YouTube API)** — The project includes `data/scripts/ingest_youtube.py`, an optional pipeline to pull transcripts from the Breaking Into Cyber YouTube channel and append them as additional RAG context. This turns 7+ years of public educational content into a living, queryable knowledge base.

3. **User-Generated Data** — Each user's resume text, answers, goals, and progress milestones become training signal for increasingly personalized coaching within Firestore.

---

### Findings and Learnings

**What worked exceptionally well:**

- **Tool-based architecture is the right pattern for career coaching.** By decomposing the agent's capabilities into discrete, well-documented tools (one per coaching function), the model learns exactly when to invoke each one. The docstrings serve as routing logic — Gemini reliably calls `generate_study_plan()` when a user asks "how should I study for CISSP?" and `evaluate_answer()` immediately after a user submits a practice answer.

- **Firestore as memory is seamless.** The `get_user_progress()` tool, called at session start, injects a user's full history into the agent context. This one pattern transforms a stateless chat into a persistent coaching relationship. Users who returned to a second session were immediately addressed by name and had their prior goal referenced without re-prompting.

- **The persona file matters more than expected.** The difference between a generic AI answer and a CyberMentor answer was almost entirely determined by the quality of `agent/persona.txt`. When the persona explicitly said "always end with a next step or question" and "never make users feel bad for not knowing something," the agent's tone transformed from assistant to mentor.

- **SSE streaming makes the UX feel alive.** The choice to implement Server-Sent Events rather than a synchronous POST/response pattern was correct. Seeing the agent's detailed study plan stream in token by token — like watching an expert type in real time — creates engagement and perceived intelligence that a loading spinner cannot replicate.

**What was challenging:**

- **Graceful degradation from Firestore to local storage.** To support running the demo locally without GCP credentials, every Firestore call needed a clean fallback to JSON file storage. This double-codepath added complexity but made the local development experience dramatically smoother.

- **Markdown rendering in vanilla JS.** Implementing a lightweight markdown parser without a library dependency (to keep the frontend dependency-free) required careful regex sequencing — code blocks must be extracted before inline code, headers before bold, etc. The final `renderMarkdown()` function handles all the patterns the agent produces.

- **The knowledge base coverage gap.** The curated JSON captures the most common certifications and roles but doesn't yet cover niche areas (OT/ICS security, forensics, threat intelligence). The YouTube ingestion pipeline exists precisely to fill this gap with real Breaking Into Cyber content.

---

## 🔗 Code Repository

**GitHub:** `https://github.com/christophe-foulon/cybermentor`

> If the repository is private, it has been shared with:
> - testing@devpost.com
> - cloudhackathons@google.com

---

## 🚀 Spin-up Instructions

### Option A: Run Locally (No Cloud Required)

**Prerequisites**
- Python 3.11 or 3.12
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/api-keys) (free tier is sufficient)

```bash
# 1. Clone the repository
git clone https://github.com/christophe-foulon/cybermentor.git
cd cybermentor

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
```

Open `.env` and set at minimum:
```
GEMINI_API_KEY=your_key_here
```
*(GOOGLE_CLOUD_PROJECT is optional for local — Firestore will gracefully fall back to local JSON storage)*

```bash
# 5. Start the API server
uvicorn api.main:app --reload --port 8080

# 6. Open the frontend
open web/index.html
# Or serve it:
python -m http.server 3000 --directory web
# Then visit http://localhost:3000
```

**Test the agent:**
- Enter a display name on the welcome screen
- Click "Career Path" in the sidebar and type your background
- Ask: *"I want to become a SOC analyst. Where do I start?"*
- Ask: *"Give me a study plan for Security+ — I have 10 hours a week"*
- Click "Interview Prep" and practice a mock interview

---

### Option B: Deploy to Google Cloud Run

**Prerequisites**
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated
- A Google Cloud project with billing enabled
- Firestore database created in your project

```bash
# 1. Authenticate and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Store your Gemini API key as a secret
echo -n "YOUR_GEMINI_API_KEY" | \
  gcloud secrets create cybermentor-gemini-key \
  --data-file=- \
  --project=YOUR_PROJECT_ID

# 3. Deploy with one command
./deploy.sh
```

The script will:
- Enable required GCP APIs (Cloud Run, Firestore, Cloud Build, Container Registry)
- Build and push the Docker container via Cloud Build
- Deploy to Cloud Run (us-central1, 0–10 instances, 1GB RAM)
- Print the live service URL

**Expected output:**
```
✅ Deployment complete!
   URL: https://cybermentor-abc123-uc.a.run.app
```

**Verify the deployment:**
```bash
# Health check
curl https://cybermentor-abc123-uc.a.run.app/health

# API docs
open https://cybermentor-abc123-uc.a.run.app/docs
```

---

### Option C: Docker (Local Container)

```bash
# Build
docker build -t cybermentor .

# Run
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key_here \
  cybermentor

# Open
open http://localhost:8080
```

---

## 🏗️ Architecture Diagram

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full Mermaid diagram. Summary:

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (SPA)                        │
│   web/index.html · styles.css · app.js                 │
│   SSE Stream · Progress Sidebar · Quick Actions        │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP / Server-Sent Events
┌──────────────────────────▼──────────────────────────────┐
│              FastAPI Backend — Google Cloud Run         │
│            api/main.py · /api/chat/stream               │
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │         Google Antigravity SDK Agent           │    │
│  │            agent/cybermentor.py               │    │
│  │            agent/persona.txt                  │    │
│  │                                                │    │
│  │  6 Custom Tools:                               │    │
│  │  ├─ query_knowledge_base()                     │    │
│  │  ├─ generate_study_plan()                      │    │
│  │  ├─ analyze_resume()                           │    │
│  │  ├─ get_interview_question()                   │    │
│  │  ├─ evaluate_answer()                          │    │
│  │  ├─ recommend_certifications()                 │    │
│  │  └─ save/get_user_progress()                   │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬───────────────────┬─────────────────┘
                   │                   │
        ┌──────────▼──────┐   ┌────────▼─────────────────┐
        │   Gemini 3.5    │   │  Google Cloud Firestore   │
        │  (via AGY SDK)  │   │  users/ · sessions/       │
        └─────────────────┘   │  progress/ · knowledge/   │
                              └──────────────────────────┘
```

**Data flows:**
1. User types message in browser
2. Frontend POSTs to `/api/chat/stream`
3. FastAPI creates/resumes an Antigravity agent with the user's `conversation_id`
4. Agent loads user's prior progress from Firestore via `get_user_progress()`
5. Agent calls appropriate tools (study planner, resume analyzer, etc.)
6. Response streams back as SSE tokens → rendered as markdown in the browser
7. Progress milestones saved to Firestore in real time

---

## 🎬 Demo Video Script (~4 minutes)

> *This section is a guide for recording the submission demo video.*

**[0:00 – 0:30] Problem Statement**
> "Every week I hear from people who want to break into cybersecurity but don't know where to start. They're overwhelmed by conflicting advice, they don't know which certification to get first, they have no one to review their resume, and they can't afford to pay for interview coaching. I built CyberMentor to solve all of that."

**[0:30 – 1:00] Architecture Walk-through**
> Show the Cloud Run dashboard with the deployed service. Show the Firestore database collections. Briefly show the Cloud Build history to prove the backend is live on Google Cloud.

**[1:00 – 2:00] Career Coaching Demo**
> Open the live URL. Enter a display name. Click "Career Path" and say: "I have 3 years in IT helpdesk and I want to move into security. I'm interested in either SOC or pen testing." Show the agent ask clarifying questions, then deliver a structured career recommendation with salary info and cert roadmap.

**[2:00 – 3:00] Study Plan + Interview Prep Demo**
> Ask: "Give me a study plan for Security+. I have 8 hours a week and I'm a beginner." Show the week-by-week plan stream in. Then click "Interview Prep" and say: "Ask me a SOC Analyst technical question." Submit an answer. Show the scored evaluation with specific gaps identified.

**[3:00 – 3:30] Memory Demo**
> Refresh the page, re-enter the same username. Show that the agent immediately references the prior session: *"Welcome back! Last time we were building your Security+ study plan..."* Show the Firestore console in another tab to prove the data is persisted in the cloud.

**[3:30 – 4:00] Closing**
> "CyberMentor runs on the Google Antigravity SDK with Gemini 3.5, persists memory in Firestore, and is hosted on Cloud Run. It's built on seven years of Breaking Into Cyber content and it's available right now at [URL]. This is what AI-powered career mentorship looks like."

---

## ✅ Hackathon Requirements Checklist

| Requirement | Status |
|---|---|
| Gemini 3.5 or newer | ✅ Via Google Antigravity SDK (default: `gemini-3.5-flash`) |
| Google Agent Framework | ✅ Google Antigravity SDK |
| Google Cloud Service | ✅ Cloud Firestore + Cloud Run |
| Hosted Project URL | ⏳ Post-deploy |
| Text Description | ✅ This document |
| Code Repository URL | ✅ GitHub |
| Spin-up Instructions | ✅ Section above + README.md |
| Architecture Diagram | ✅ ARCHITECTURE.md + this document |
| ~4-min Demo Video | ⏳ To be recorded |

### Bonus Points Targets

| Bonus | Plan | Points |
|---|---|---|
| Publish blog/video about the build | dev.to post: "Building CyberMentor with Google Antigravity SDK" | +0.2 |
| Post on X + LinkedIn with #AllThingsAgenticHackathon | Screenshot to be added | +0.2 |
| Integrate Veo (video generation) | Planned: auto-generate cert flashcard video loops | +0.2 |
| Integrate Lyria (music generation) | Planned: ambient focus music for study sessions | +0.2 |
| Integrate Gemma | Planned: on-device inference for offline resume scan | +0.2 |

**Potential bonus total: +1.0**

---

*Built by Christophe Foulon · Breaking Into Cyber · All Things Agentic Hackathon 2026*
