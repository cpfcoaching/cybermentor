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

## 4. Zero Literal Secret & API Key Policy
- **Never Embed Literal Keys:** NEVER write, compare, or allowlist literal API key strings (e.g. `AIzaSy...`, `sk-...`, private keys) in any source file, test script, regex comparison, or security check.
- **Dynamic Config Only:** All API configurations must be loaded via runtime environment variables (`os.getenv(...)`) without hardcoded fallback strings.
- **Security Checkers:** All static security checkers and pre-commit hooks must scan using abstract regex patterns only without embedding example secret strings.
- **Incident Remediation:** When a credential occurs in a commit diff, immediately rotate or delete the key in the cloud console (e.g. Google Cloud Credentials) to ensure automated scanners mark the credential invalid.
