# CyberMentor — Architecture

## System Architecture

```mermaid
graph TB
    subgraph Browser["🖥️ Browser (SPA)"]
        UI["web/index.html<br/>CSS + Vanilla JS"]
        SSE["SSE Stream Reader"]
        UI --> SSE
    end

    subgraph CloudRun["☁️ Cloud Run — cybermentor service"]
        API["FastAPI<br/>api/main.py"]
        ChatRoute["POST /api/chat/stream<br/>api/routes/chat.py"]
        ProgressRoute["GET/POST /api/progress<br/>api/routes/progress.py"]
        API --> ChatRoute
        API --> ProgressRoute

        subgraph Agent["🤖 Google Antigravity SDK Agent"]
            Persona["Persona & System Instructions<br/>agent/persona.txt"]
            Tools["Custom Tools"]
            KB["query_knowledge_base()"]
            SP["generate_study_plan()"]
            RA["analyze_resume()"]
            IC["get_interview_question()<br/>evaluate_answer()"]
            CA["recommend_certifications()"]
            PT["save/get_user_progress()"]
            Tools --> KB
            Tools --> SP
            Tools --> RA
            Tools --> IC
            Tools --> CA
            Tools --> PT
        end

        ChatRoute --> Agent
    end

    subgraph Google["🔵 Google Cloud Services"]
        Gemini["Gemini 3.5<br/>(via Antigravity SDK)"]
        Firestore[("Cloud Firestore<br/>users/ · sessions/<br/>progress/ · knowledge/")]
    end

    subgraph KnowledgeBase["📚 Knowledge Base"]
        CertJSON["certifications.json"]
        CareerJSON["career_paths.json"]
        InterviewJSON["interview_questions.json"]
    end

    Browser -->|"HTTP / SSE"| CloudRun
    Agent -->|"Gemini API"| Gemini
    PT -->|"Read/Write"| Firestore
    ProgressRoute -->|"CRUD"| Firestore
    KB -->|"Search"| KnowledgeBase

    style Browser fill:#0c1527,color:#e4eaf5
    style CloudRun fill:#0c1527,color:#e4eaf5
    style Google fill:#1a2a4a,color:#e4eaf5
    style KnowledgeBase fill:#0c1527,color:#e4eaf5
```

## Data Model

### Firestore Collections

```
users/{user_id}
├── profile: {
│     career_goal: string
│     experience_level: string
│     target_certs: string[]
│     created_at: ISO timestamp
│     updated_at: ISO timestamp
│   }
└── progress/{milestone_id}
      ├── milestone: string
      ├── notes: string
      └── timestamp: ISO timestamp

sessions/{session_id}
└── messages/{message_id}
      ├── role: "user" | "agent"
      ├── content: string
      └── timestamp: ISO timestamp
```

## Request Flow: Streaming Chat

```
User types message
      │
      ▼
POST /api/chat/stream
      │
      ├─ Lookup or create session_id
      │
      ├─ Prepend user context to message
      │
      ├─ async with create_cybermentor_agent(conversation_id) as agent:
      │       response = await agent.chat(message)
      │
      ├─ Stream SSE chunks → Browser
      │       data: {"token": "...", "session_id": "..."}
      │
      └─ data: {"done": true}
            │
            ▼
      Browser renders markdown
      Progress sidebar reloads
```

## Agent Tool Decision Tree

```
User message arrives
       │
       ├─ Contains cert name?           → query_knowledge_base() + generate_study_plan()
       ├─ Asks "what cert should I get?" → recommend_certifications()
       ├─ Pastes resume text?            → analyze_resume()
       ├─ Asks for interview question?   → get_interview_question()
       ├─ Answers an interview question? → evaluate_answer()
       ├─ Shares a milestone/progress?   → save_user_progress()
       └─ New session?                   → get_user_progress() (called at session start)
```

## Deployment

| Component | Service | Config |
|---|---|---|
| Backend | Cloud Run | 1 CPU, 1GB RAM, 0-10 instances |
| Database | Cloud Firestore | Enterprise edition, us-central1 |
| AI Model | Gemini 3.5 via AGY SDK | Default model |
| Frontend | Served from Cloud Run | Static files at `/static` |
| Secrets | Cloud Secret Manager | `cybermentor-gemini-key` |
