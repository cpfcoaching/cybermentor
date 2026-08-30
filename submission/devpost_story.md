## Inspiration

Breaking into cybersecurity is genuinely hard — not because the field is inaccessible, but because the information landscape is overwhelming and deeply contradictory.

- A forum tells you to get OSCP first. A video says Security+ is a waste of money. A bootcamp charges $15,000 to tell you to "just do TryHackMe."
- Career changers from IT, military, accounting, or help desk struggle to identify which role aligns with their transferable skills.
- Study plans are one-size-fits-all and ignore real-world constraints like working full-time with only 8 hours a week to study.
- Interview prep is scattered and expensive, with zero real-time scoring or structured rubrics.

Over seven years of hosting [Breaking Into Cybersecurity](https://breakingintocybersecurity.org) and mentoring thousands of candidates, one lesson became crystal clear: **success requires personalized, persistent mentorship.** Because one mentor cannot personally coach thousands of students 1-on-1 every day, I built **CyberMentor** for the Google Cloud *All Things Agentic Hackathon* to democratize CISO-grade career coaching 24/7.

---

## What It Does

CyberMentor is an autonomous, persistent AI career coaching partner built on the **Google Antigravity SDK** and **Gemini 3.7 Flash**. It is not a stateless chatbot — it builds a persistent profile of each user in Cloud Firestore, remembering their background, study milestones, and interview scores across sessions.

### Core Capabilities:
1. **Career Path Discovery & Mindmapping**: Analyzes candidate background, IT experience, and goals to map them to targeted cybersecurity domains (SOC Analyst, Pen Tester, GRC, Cloud Security, CISO track) with salary benchmarks.
2. **Hour-Calibrated Study Planner**: Generates phased week-by-week certification roadmaps (Security+, CySA+, CISSP, OSCP, eJPT, etc.) customized to available study hours per week.
3. **Resume & Skill Gap Auditor**: Scans resumes against target roles, computing match percentages and prioritizing high-impact action items.
4. **Voice-Enabled Scored Mock Interviews**: Drills candidates on technical and behavioral scenarios, scoring responses against rubrics out of 10 and pinpointing knowledge gaps.
5. **Persistent Memory**: Automatically syncs progress, practice scores, and notes to Google Cloud Firestore so candidates resume exactly where they left off.
6. **Podcast RAG Engine**: Connects candidates to 7+ years and 1,100+ episodes of real CISO and practitioner guidance.

---

## How We Built It

```text
┌─────────────────────────────────────────────────────────┐
│                    Browser (SPA)                        │
│   Vanilla JS · Glassmorphism Dark UI · SSE Streaming    │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP / SSE
┌──────────────────────────▼──────────────────────────────┐
│           FastAPI Backend — Google Cloud Run            │
│  ┌────────────────────────────────────────────────┐    │
│  │         Google Antigravity SDK Agent           │    │
│  │  ├─ query_knowledge_base()                     │    │
│  │  ├─ generate_study_plan()                      │    │
│  │  ├─ analyze_resume()                           │    │
│  │  ├─ get_interview_question()                   │    │
│  │  ├─ evaluate_answer()                          │    │
│  │  └─ save/get_user_progress()                   │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬───────────────────┬─────────────────┘
                   │                   │
        ┌──────────▼──────┐   ┌────────▼─────────────────┐
        │   Gemini 3.7    │   │  Google Cloud Firestore   │
        │  (via AGY SDK)  │   │  users/ · progress/       │
        └─────────────────┘   └──────────────────────────┘
```

CyberMentor is engineered as an enterprise-grade agentic system on Google Cloud:

- **Agent Framework**: Google Antigravity SDK using structured Python tool docstrings as dynamic routing logic.
- **Foundation Model**: Google Gemini 3.7 Flash via Vertex AI / Antigravity SDK.
- **Multimodal AI Extensions**:
  - **Gemma 3**: Local, low-latency pre-routing and token-efficient resume skill extraction.
  - **Google Veo**: Generates cinematic role preview videos (e.g., modern SOC operations environments) for candidates.
  - **Google Lyria**: Generates ambient binaural focus study music and milestone fanfare audio.
- **Backend Architecture**: Python 3.12 + FastAPI with Server-Sent Events (SSE) for sub-second, token-by-token streaming responses.
- **Storage & State**: Google Cloud Firestore enterprise database for session state and progress persistence (with graceful offline JSON fallback for local dev).
- **Deployment**: Google Cloud Run (containerized, auto-scaling to zero) fronted with Cloudflare Edge SSL.

---

## Challenges We Ran Into

1. **State Persistence Across SSE Streams**: Bridging long-lived agent conversational memory across stateless HTTP SSE streaming connections required a clean session reconciler that writes progress delta checkpoints to Firestore without blocking the streaming text generator.
2. **Deterministic Routing vs. Free-Form Mentorship**: Balancing natural conversational warmth with strict tool invocation (e.g., triggering the interview rubric vs. study planner) was solved by fine-tuning the system persona file (`agent/persona.txt`) and structuring tool signatures to return machine-readable payloads.
3. **Graceful Cloud-to-Local Fallback**: Designing a dual-mode persistence architecture that seamlessly switches between Cloud Firestore and local JSON files to allow offline development and evaluation.

---

## Accomplishments That We're Proud Of

- **True State Persistence**: Unlike standard LLM chat wrappers, returning users are greeted by name and immediately pick up where their certification study plan left off.
- **Measurable Candidate ROI**: Replaces $15,000 bootcamps with personalized, self-paced guidance that reduces time-to-hire by an estimated ~65%.
- **Zero-Cost Scale-to-Zero Architecture**: Fully serverless deployment on Google Cloud Run and Firestore with sub-second cold starts.
- **Comprehensive Multimodal Integration**: Full adoption of Gemini 3.7, Gemma 3, Veo, and Lyria within a unified agent workflow.

---

## What We Learned

- **Persona Files Drive Mentorship Quality**: The tone, empathy, and pedagogy of the coach were dramatically elevated by engineering `agent/persona.txt` to always require actionable next steps and encouraging feedback.
- **Tools as Cognitive Primitives**: Giving the model discrete Python tools for specific tasks (scoring rubrics, roadmap generation, resume auditing) produces far more consistent, higher-fidelity outputs than massive single-prompt instructions.

---

## What's Next for CyberMentor

- **Live Mobile Apps**: Finalizing iOS App Store and Google Play Store TWA distributions via Capacitor.
- **Automated Resume Tailoring**: Expanding the Gemma skill extractor to generate targeted bullet points calibrated to specific corporate job postings.
