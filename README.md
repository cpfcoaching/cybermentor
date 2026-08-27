# 🛡️ CyberMentor — AI Career Coach for Aspiring Security Pros

> Built for the **All Things Agentic Hackathon** | Track: **The Collaborative Partner**  
> Powered by **Google Antigravity SDK** · **Gemini 3.5** · **Firestore** · **Cloud Run**

CyberMentor is an autonomous AI career coaching agent tailored to the [Breaking Into Cybersecurity](https://breakingintocybersecurity.org) brand. It guides aspiring cybersecurity professionals through every stage of their journey — from choosing the right certification path to practicing technical interview answers — while remembering your progress across every session.

---

## 🎯 What It Does

| Feature | Description |
|---|---|
| 🗺️ **Career Path Advisor** | Recommends the right certs and roles based on your experience and goals |
| 📅 **Study Planner** | Generates week-by-week study plans for Security+, CISSP, OSCP, and more |
| 📄 **Resume Analyzer** | Reviews your resume and identifies gaps for cybersecurity roles |
| 🎤 **Interview Coach** | Drills you on technical and behavioral questions with scored feedback |
| 🧠 **ACE Memory & Self-Optimization** | Takes structured memory notes & continuously adapts coaching strategy |
| 💾 **Persistent Memory** | Remembers your goals, notes, and progress across every session via Firestore |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- A `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/app/api-keys)
- A Google Cloud project with Firestore enabled (for memory persistence)

### 1. Clone and set up environment

```bash
git clone <your-repo-url> cybermentor
cd cybermentor

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 3. (Optional) Seed Firestore

```bash
python data/scripts/seed_firestore.py
```

### 4. Run the backend

```bash
uvicorn api.main:app --reload --port 8080
```

### 5. Open the frontend

```bash
open web/index.html
# Or: python -m http.server 3000 --directory web
```

---

## ☁️ Deploy to Cloud Run

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
./deploy.sh
```

---

## 🏆 Hackathon Requirements

- [x] Gemini 3.5 — via Google Antigravity SDK
- [x] Google Agent Framework — Antigravity SDK
- [x] Google Cloud Service — Firestore + Cloud Run
- [ ] Hosted URL — available after deploy
- [ ] Architecture Diagram — see ARCHITECTURE.md

---

## 👤 Author

Built by **Christophe Foulon** | [Breaking Into Cybersecurity](https://breakingintocybersecurity.org)
