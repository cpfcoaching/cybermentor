---
title: "I Built an AI Cybersecurity Career Coach in a Weekend: Here Is Exactly How"
published: true
description: "How I used the Google Antigravity SDK, Gemini 3.7 Flash, Veo, Lyria, and Gemma to build CyberMentor: a persistent AI career coach for breaking into cybersecurity. Built for the All Things Agentic Hackathon."
tags: google, ai, cybersecurity, hackathon
cover_image: https://breakingintocyber.com/cybermentor-cover.png
canonical_url: https://dev.to/cfoulon/cybermentor-ai-career-coach
---

> **Note:** This project was built for the [All Things Agentic Hackathon](https://allthingsagentichackathon.devpost.com) hosted by Google Cloud under **The Collaborative Partner** track.

---

Generic advice is the primary reason candidates struggle to break into cybersecurity. Over seven years of producing [Breaking Into Cybersecurity](https://breakingintocybersecurity.org), I have answered thousands of career questions across podcasts, YouTube videos, and mentorship sessions. The winning strategy always requires a personalized roadmap tailored to each candidate's background, available study hours, and specific target role.

Because one-on-one mentorship does not scale infinitely, I built **CyberMentor** for the Google Cloud All Things Agentic Hackathon. CyberMentor is an autonomous, persistent AI coaching agent that guides candidates through discovery, study scheduling, resume audits, and mock interviews. It operates as a true collaborative partner: asking discovery questions, remembering every milestone in Cloud Firestore, and evolving with each user interaction.

Here is the exact architectural breakdown of how it was built.

---

## 🏗️ The System Architecture

| Layer | Technology | Operational Purpose |
| --- | --- | --- |
| **AI Agent Framework** | Google Antigravity SDK | Tool schema generation, reasoning loops, and multi-turn execution |
| **Primary Reasoning Engine** | Gemini 3.7 Flash (Vertex AI) | Core coaching logic, personalized evaluation, and tool orchestration |
| **Video Generation** | Google Veo (Vertex AI) | Role preview cinematic clips and certification explainer videos |
| **Focus Audio Generation** | Google Lyria (Vertex AI) | Ambient focus study tracks and milestone celebration fanfares |
| **Fast Inference Engine** | Google Gemma 3 27B (Vertex AI) | Low-latency intent classification and resume skill extraction |
| **Persistent Memory** | Google Cloud Firestore | Cross-session user profiles, progress milestones, and session logs |
| **Serverless Deployment** | Google Cloud Run | Zero-cost scale-to-zero container hosting in us-central1 |
| **Backend API** | Python 3.12 + FastAPI | Real-time Server-Sent Events (SSE) token streaming |
| **Frontend Interface** | Vanilla HTML, CSS, and JS | Glassmorphic dark UI with speech-to-text and zero build step |

---

## 🤖 The Core Engine: Google Antigravity SDK

CyberMentor is built around a single primary agent using the Google Antigravity SDK. The SDK pattern is exceptionally clean: you define standard Python functions with explicit docstrings and type annotations, and the framework automatically manages tool schemas, execution loops, and token streaming.

```python
from google_antigravity import Agent
from agent.cybermentor import CYBERMENTOR_TOOLS, CYBERMENTOR_SYSTEM_INSTRUCTION

agent = Agent(
    model="gemini-3.7-flash",
    system_instruction=CYBERMENTOR_SYSTEM_INSTRUCTION,
    tools=CYBERMENTOR_TOOLS,
)
```

The system instruction establishes the persona: an authoritative yet accessible cybersecurity career mentor rooted in the Breaking Into Cybersecurity methodology. It asks clarifying discovery questions before offering recommendations, references the NIST NICE Cybersecurity Workforce Framework (NIST SP 800-181), and maintains context across multi-day sessions.

---

## 🛠️ The Six Core Coaching Tools

Every coaching capability is implemented as an isolated, deterministic Python function:

### 1. `query_knowledge_base()`: RAG Over Curated Cybersecurity Data

Searches a curated JSON knowledge base covering 9 major certifications (Security+, CySA+, CASP+, CEH, CISSP, eJPT, OSCP, AWS Security, and GCP Security) and 5 distinct career tracks. Every entry includes Breaking Into Cyber notes with real-world hiring context rather than generic definitions.

```python
def query_knowledge_base(topic: str, category: Optional[str] = None) -> str:
    """Search the CyberMentor knowledge base for information on a cybersecurity topic."""
    # Fuzzy search across certifications.json, career_paths.json, interview_questions.json
    ...
```

### 2. `generate_study_plan()`: Calibrated Week-by-Week Roadmaps

Accepts a target certification, available weekly study hours, and current experience level. It generates a phased timeline: foundations, domain coverage, practice examinations, and final buffer review. It automatically adds 30 percent more study buffer for career changers entering from non-technical backgrounds.

### 3. `analyze_resume()`: NIST NICE Framework Skill Gap Audit

Parses raw resume text for certification keywords, named security tools, quantified operational achievements, and cybersecurity terminology. It returns a scored audit out of 100 with prioritized action items aligned with real hiring manager expectations.

### 4. `get_interview_question()` and `evaluate_answer()`: Mock Interview Feedback Loop

Questions are retrieved from role-specific banks (SOC Analyst, Penetration Tester, GRC Analyst, and Security Leadership). Each question contains a rubric of required technical and behavioral points. The evaluation tool scores the candidate's answer against these criteria, identifies blind spots, and provides a structured model response.

### 5. `recommend_certifications()`: Role-Specific Certification Roadmaps

Maps candidate backgrounds to specific cybersecurity roles. It provides realistic compensation ranges and time-to-hire expectations verified through community mentorship data.

### 6. `save_user_progress()` and `get_user_progress()`: Cloud Firestore Persistence

This tool transforms CyberMentor from a stateless chatbot into a genuine collaborative partner. Every completed practice exam, resume audit, and interview drill writes directly to Cloud Firestore. When a candidate returns for a new session, the agent automatically loads their progress and references their ongoing goals.

---

## ⚡ Multimodal Google AI Integrations

To enhance candidate engagement and optimize cloud runtime costs, CyberMentor incorporates three specialized Google AI models:

### 1. Google Veo: Cinematic Role Previews

When candidates ask what a SOC Analyst or Penetration Tester does on a daily basis, visual media delivers immediate clarity. Veo generates high-definition video previews illustrating realistic security operations center environments:

```python
operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt=(
        "A cybersecurity SOC analyst monitoring multiple screens showing SIEM dashboards, "
        "alert queues, and network traffic graphs in a modern operations center."
    ),
    config=types.GenerateVideoConfig(
        aspect_ratio="16:9",
        number_of_videos=1,
        duration_seconds=8,
        enhance_prompt=True,
    ),
)
```

### 2. Google Lyria: Study Focus Audio

Research indicates that consistent background audio improves cognitive retention during technical study. CyberMentor integrates Lyria to generate custom ambient soundscapes across five presets: `focus`, `energized`, `exam_crunch`, `wind_down`, and `cyberpunk` (designed for hands-on lab environments).

### 3. Google Gemma 3: Two-Tier Low-Cost Inference

Not every operational task requires the full parameter capacity of Gemini 3.7 Flash. CyberMentor adopts a two-tier inference pattern where Google Gemma 3 27B handles fast structured tasks before Gemini processes deep conversational context:

1. **Intent Classification**: Rapidly routes user inquiries to appropriate tools with sub-second latency.
2. **Resume Entity Extraction**: Parses structured technical tokens from unstructured resume documents.
3. **Skill Gap Scoring**: Computes objective readiness scores against baseline job requirements.

This two-tier structure dramatically reduces round-trip latency and keeps overall operational compute within Google Cloud free-tier allowances.

---

## 🖥️ Frontend Architecture and Real-Time SSE Streaming

The web application uses vanilla HTML5, CSS3, and JavaScript without external frameworks or build tooling. A simple local static server or Cloud Run container serves the entire application instantly.

Key frontend capabilities include:

- **Server-Sent Events (SSE)**: Streams agent reasoning token-by-token for responsive conversational feedback.
- **Persistent Progress Sidebar**: Connects directly to Firestore to display candidate milestone history.
- **Voice Mode**: Enables speech-to-text input and audio narration for hands-free mock interview practice.
- **Cross-Browser Styling**: Pure vanilla CSS design system featuring dark glassmorphism and universal scrollbar support.

---

## 🧠 Memory Persistence: The Collaborative Partner Pattern

Persistent memory is the defining characteristic of a true collaborative partner. The Cloud Firestore hierarchy isolates candidate data securely:

```text
users/{user_id}
├── profile: {career_goal, experience_level, target_certs[], updated_at}
└── progress/{milestone_id}
      ├── milestone: "Completed Security+ domain 3 review"
      └── timestamp: "2026-08-26T14:00:00Z"

sessions/{session_id}
└── messages/{message_id}
      ├── role: "user" | "agent"
      └── content: "..."
```

When a user initiates a session, `get_user_progress()` injects historical context directly into the agent reasoning layer. The coach opens with immediate context: *"Welcome back! Last week you finished Domain 2 of your Security+ roadmap. Are you ready to tackle Network Security fundamentals today?"*

For local testing without cloud credentials, all data operations automatically fall back to local JSON storage in `sessions/progress/`.

---

## 💡 Strategic Takeaways and Lessons Learned

1. **Persona Files Outperform System Prompts**: Defining tone, boundaries, and response structures in an explicit `persona.txt` document produced far more consistent coaching behavior than inline prompt strings.
2. **Tool Docstrings Serve as Routing Logic**: The Google Antigravity SDK relies on clear, semantic docstrings to route tasks autonomously, eliminating the need for brittle manual intent dispatchers.
3. **Two-Tier Model Architecture Maximizes Efficiency**: Pairing Gemma for classification with Gemini for reasoning delivers the optimal balance of speed, cost, and intellectual depth.
4. **Graceful Degradation Is Mandatory**: Designing local storage and fallback handlers for all cloud services ensures the application remains dependable in offline or disconnected environments.

---

## 🚀 Running CyberMentor Locally

```bash
git clone https://github.com/cpfcoaching/cybermentor.git
cd cybermentor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn api.main:app --reload --port 8080
```

Deploying to Google Cloud Run requires a single command:

```bash
gcloud config set project YOUR_PROJECT_ID
./deploy.sh
```

---

## 🌐 Project Links and Community Resources

- **Live Application**: [https://cybermentor-1019457807345.us-central1.run.app](https://cybermentor-1019457807345.us-central1.run.app)
- **API Documentation**: [https://cybermentor-1019457807345.us-central1.run.app/docs](https://cybermentor-1019457807345.us-central1.run.app/docs)
- **GitHub Repository**: [https://github.com/cpfcoaching/cybermentor](https://github.com/cpfcoaching/cybermentor)
- **Support the Mission**: [Buy Me a Coffee](https://www.buymeacoffee.com/cpf_coaching)
- **Breaking Into Cybersecurity**: [breakingintocybersecurity.org](https://breakingintocybersecurity.org)

---

### About the Author

**Christophe Foulon** is a cybersecurity leader, author, and co-host of *Breaking Into Cybersecurity*. He has spent years coaching aspiring practitioners into security operations, GRC, and leadership roles. CyberMentor represents the persistent, open-source AI extension of that mission.

> Built for the Google Cloud All Things Agentic Hackathon | Track: The Collaborative Partner
