# ACE System Learnings & Architectural Constraints

This document records consolidated learnings and architectural rules established through the ACE Framework for CyberMentor.

## 1. Footer & Branding Standard
- **Core UI Footer:** MUST ONLY state `Powered by Breaking Into Cybersecurity` with hyperlink to `https://breakingintocybersecurity.org`.
- **Secondary Citations:** All secondary resources (Paul Jerimy Certification Roadmap, Hadess Roadmap, Cyberdudekz Roadmap, ACE Framework, NIST AI RMF 1.0, OWASP LLM Top 10) MUST be located in the interactive **Resources & Citations Modal** (`#resources-overlay`), accessed via the `📚 Resources & Citations` quick action button.

## 2. Authentication & Session Storage Policy
- **Authenticated Account Mode (Google SSO - MFA Verified):**
  - Triggered via Google OAuth 2.0 (`signInWithPopup`).
  - Conversation history is saved to and retrieved from Cloud Firestore (`users/{user_id}/conversations/{session_id}/messages`).
  - Candidate progress milestones are saved to Cloud Firestore (`users/{user_id}/progress/milestones`).
- **Temporary Guest Mode (Display Name / Screen Name):**
  - Activated when a candidate enters a temporary screen name.
  - NO conversation data or progress is saved to Cloud Firestore across sessions.
  - ACE Cognitive Memory operates in-memory for the turn/session duration.

## 3. UI/UX Authentication Rules
- **No Browser JS Prompts:** NEVER use Javascript `prompt()` popup dialogs for Google SSO. Display status messages directly inside the onboarding card element (`#auth-status-msg`) if popups are cancelled or blocked.
