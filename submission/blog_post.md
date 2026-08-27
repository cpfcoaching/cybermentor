---
title: "I Built an AI Cybersecurity Career Coach in a Weekend — Here's Exactly How"
published: true
description: "How I used the Google Antigravity SDK, Gemini 3.5, Veo, Lyria, and Gemma to build CyberMentor — a persistent AI career coach for breaking into cybersecurity. Built for the All Things Agentic Hackathon."
tags: google, ai, cybersecurity, hackathon
cover_image: https://breakingintocyber.com/cybermentor-cover.png
canonical_url: https://dev.to/cfoulon/cybermentor-ai-career-coach
---

> **Note:** This project was built for the [All Things Agentic Hackathon](https://allthingsagentichackathon.devpost.com) hosted by Google Cloud. Track: **The Collaborative Partner**.

---

Every week, someone DMs me some version of the same question:

*"I want to break into cybersecurity. Where do I start?"*

I've answered this hundreds of times on [Breaking Into Cybersecurity](https://breakingintocyberscurity.org) — through YouTube videos, podcast episodes, mentorship calls. The answer is always personalized: it depends on your background, your goals, how many hours you have, and which role actually excites you.

The problem is I can't personally coach everyone. So I built the next best thing: **CyberMentor**, an AI agent that coaches people through their cybersecurity career journey the same way I would — asking the right questions, remembering the answers, and giving structured, actionable guidance.

Here's exactly how I built it.

---

## The Stack

| Layer | Technology |
|---|---|
| AI Agent | Google Antigravity SDK |
| Main Model | Gemini 3.5 Flash |
| Video Generation | Google Veo (via Vertex AI) |
| Music Generation | Google Lyria (via Vertex AI) |
| Fast Classification | Google Gemma 3 27B (via Vertex AI) |
| Memory | Google Cloud Firestore |
| Deployment | Google Cloud Run |
| Backend | Python 3.12 + FastAPI |
| Frontend | Vanilla HTML/CSS/JS |

---

## Why the Google Antigravity SDK?

I evaluated several agent frameworks before settling on the Antigravity SDK, and the decision came down to one thing: **tool docstrings as routing logic**.

In the Antigravity SDK, you give the agent Python functions with clear docstrings, and Gemini figures out when to call each one. This sounds simple, but it's the key insight for building a specialized coaching agent. When I wrote:

```python
def generate_study_plan(
    target_cert: str,
    hours_per_week: int,
    current_level: str = "beginner",
) -> str:
    """Generate a week-by-week study plan for a cybersecurity certification.

    Use this tool when a user asks how to study for a specific certification,
    wants a study schedule, or asks "how long will it take to get my [cert]?"
    ...
    """
```

Gemini reliably invokes `generate_study_plan()` every time a user asks about studying for a cert — without any custom routing code. The docstrings ARE the routing logic. This kept the codebase clean and the behavior predictable.

---

## The 6 Core Coaching Tools

I built each coaching capability as an isolated Python function:

### 1. `query_knowledge_base()` — RAG over curated cybersecurity data
Searches a curated JSON knowledge base covering 9 certifications (Security+, CISSP, OSCP, eJPT, etc.) and 5 career paths. Every entry includes Breaking Into Cyber-specific notes: opinionated, real-world guidance, not just Wikipedia summaries.

```python
def query_knowledge_base(topic: str, category: Optional[str] = None) -> str:
    """Search the CyberMentor knowledge base for information on a cybersecurity topic."""
    # Fuzzy search across certifications.json, career_paths.json, interview_questions.json
    ...
```

### 2. `generate_study_plan()` — Personalized week-by-week schedules
Takes a certification name, weekly hours, and experience level, then outputs a phased plan: foundations → domain study → practice exams → final review. It adjusts total hours based on level (beginners need ~30% more time than intermediate learners).

### 3. `analyze_resume()` — Cybersecurity-specific gap analysis
Parses resume text for cert keywords, tool names, quantified achievements, and cybersecurity-specific language. Returns a score out of 100 with prioritized action items. The scoring weights are calibrated to what I actually see employers care about.

### 4. `get_interview_question()` + `evaluate_answer()` — Full mock interview loop
Questions are drawn from a role-specific bank (SOC Analyst, Pen Tester, GRC, general). Each question has a rubric of key points. `evaluate_answer()` scores the user's response by checking coverage of those key points, penalizes overly brief answers, and returns a model answer template.

### 5. `recommend_certifications()` — Role-specific roadmaps
Recommends certs in order for 5 career tracks, calibrated to experience level. The data includes salary ranges and time-to-hire estimates — information I've verified through years of community mentorship.

### 6. `save/get_user_progress()` — Persistent memory via Firestore
This is what makes CyberMentor a **collaborative partner** rather than a stateless chatbot. Every milestone is written to Firestore. At session start, `get_user_progress()` loads the user's history and injects it into the agent context — so returning users are immediately recognized and coached based on what was previously discussed.

---

## The Bonus Model Integrations

The hackathon offered bonus points for integrating additional Google AI models. I added three:

### Veo — Visual Career Previews

When users ask "what does a SOC analyst actually do all day?" — text answers are fine, but a video is better. I integrated Veo via Vertex AI to generate short cinematic clips of different cybersecurity roles:

```python
operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt=(
        "A cybersecurity SOC analyst monitoring multiple screens showing SIEM dashboards, "
        "alert queues, and network traffic graphs. Dark operations center environment..."
    ),
    config=types.GenerateVideoConfig(
        aspect_ratio="16:9",
        number_of_videos=1,
        duration_seconds=8,
        enhance_prompt=True,
    ),
)
```

The video generation is async, so the agent polls the operation until completion and streams the result URL back. I also use Veo to generate short explainer clips for certifications — think of it as a visual "what is Security+?" answer.

### Lyria — Focus Music for Study Sessions

Study science is clear: the right background music improves focus. I integrated Lyria to generate custom ambient tracks when users start a study session:

```python
# When a user says "I'm about to start studying for CISSP, give me something to listen to"
generate_study_music(mood="focus", duration_seconds=180, cert_context="CISSP")
```

Five moods available: `focus`, `energized`, `exam_crunch`, `winding_down`, and `cyber` (synthwave for terminal-based lab work). There's also a celebratory jingle for when users announce they passed their exam.

### Gemma — Fast Intent Classification

Here's the architectural insight that surprised me most: **not every inference call needs Gemini**.

For high-frequency, low-complexity tasks — "what does this message mean?" — a smaller model is faster and cheaper. I use Gemma 3 27B (via Vertex AI) for three specific tasks:

1. **Intent classification**: Route user messages to the right tool before Gemini even sees them
2. **Resume skill extraction**: Pull structured JSON (certs, tools, years of experience) from raw resume text
3. **Skill gap scoring**: Score a candidate's readiness for a target role

```python
def classify_user_intent(message: str) -> str:
    """Rapidly classify intent using Gemma for fast routing."""
    # Gemma returns: {"intent": "study_plan", "confidence": 0.94, "key_entities": ["CISSP"]}
```

This pattern — **Gemma for classification, Gemini for generation** — is something I'll use in future agent projects. It creates a two-tier inference architecture that's both faster and more cost-efficient.

---

## The Frontend: Glassmorphism Cybersecurity UI

I deliberately chose vanilla HTML/CSS/JS for the frontend (no React, no build step). The reasoning: for a hackathon demo, time-to-demo matters more than code elegance. A `python -m http.server` and `open index.html` is all you need to run it.

The UI is built around a dark navy/cyan/teal glassmorphism aesthetic — fitting for a cybersecurity product. Key features:

- **SSE streaming**: Responses stream token-by-token using Server-Sent Events, not polling
- **Sidebar progress panel**: Real-time milestone display from Firestore
- **Quick action buttons**: One-click prompts for career path, study plan, resume review, and interview prep
- **Markdown rendering**: A custom lightweight parser (no dependencies) handles headers, bold, code blocks, tables, and checkboxes

---

## Memory Architecture: The Key to "Collaborative Partner"

The session persistence pattern is worth documenting carefully, because it's what separates a smart chatbot from a genuine coaching relationship.

**Firestore schema:**
```
users/{user_id}
├── profile: {career_goal, experience_level, target_certs[], updated_at}
└── progress/{milestone_id}
      ├── milestone: "Completed Security+ week 3 study plan"
      └── timestamp: "2026-08-26T14:00:00Z"

sessions/{session_id}
└── messages/{message_id}
      ├── role: "user" | "agent"
      └── content: "..."
```

**At session start:**
```python
# The agent automatically calls this tool at session start
progress = get_user_progress(user_id)
# Returns: "Milestone 1: [2026-08-15] Set goal: SOC Analyst
#           Milestone 2: [2026-08-20] Completed Security+ week 1..."
```

This context is injected into the conversation, and Gemini uses it to craft a personalized opening: *"Welcome back! Last time we set up your Security+ study plan. You're in week 3 — how did the domain review go?"*

**Local fallback:** For local development without GCP credentials, all Firestore calls fall back to JSON files in `sessions/progress/`. The agent works fully offline — just without cloud persistence.

---

## What I Learned

**1. Persona files are underrated.** The single biggest quality improvement came from writing a detailed `persona.txt` rather than a short system prompt. Specifying tone, scope, refusal criteria, and response structure in prose produced dramatically more consistent outputs than trying to encode these in code.

**2. Streaming UX changes the perceived quality.** Users rated their experience significantly higher when responses streamed vs. appeared all at once — even when the total content was identical. The agent *feels* more thoughtful when you can watch it construct a response.

**3. Tool docstrings are your routing logic.** Don't write a router. Write better docstrings. The "Use this tool when..." section of each docstring is the most important few sentences in the codebase.

**4. The two-tier model pattern works.** Gemma for classification + Gemini for generation is a pattern worth adopting broadly. The latency improvement is measurable and the cost savings are real.

**5. Graceful degradation is non-negotiable.** Every external dependency (Firestore, Veo, Lyria, Gemma) has a fallback. The agent degrades gracefully — never breaking, always providing value — even when cloud services are unavailable.

---

## Running It Yourself

```bash
git clone https://github.com/christophe-foulon/cybermentor
cd cybermentor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your GEMINI_API_KEY
uvicorn api.main:app --reload --port 8080
open web/index.html
```

Or deploy to Cloud Run in one command:

```bash
gcloud config set project YOUR_PROJECT_ID
./deploy.sh
```

---

## What's Next

CyberMentor is a hackathon project, but the use case is real. A few things I want to build next:

- **Full RAG pipeline**: Ingest all Breaking Into Cyber YouTube transcripts into Vertex AI Vector Search for true semantic retrieval over 7+ years of content
- **Voice mode**: Replace the text input with real-time audio using the Gemini Live API
- **Progress dashboard**: A dedicated analytics view showing study streak, cert readiness scores over time, and interview performance trends
- **Community features**: Anonymous progress sharing — see what certs people are working toward, celebrate milestones together

---

## The Verdict

The Google Antigravity SDK made building a production-quality agentic application genuinely fast. The pattern of tools-as-docstrings, combined with Firestore persistence and the SSE streaming API, produces a user experience that feels meaningfully different from a chat window.

CyberMentor solves a real problem I care about. That's the only kind of project worth building.

→ **[Try CyberMentor](https://cybermentor-1019457807345.us-central1.run.app)**
→ **[GitHub Repository](https://github.com/christophe-foulon/cybermentor)**
→ **[Breaking Into Cybersecurity](https://breakingintocybersecurity.org)**

*Built for the All Things Agentic Hackathon by Google Cloud | #AllThingsAgenticHackathon*
