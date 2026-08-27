# 🛡️ CyberMentor Privacy Policy & Data Protection Charter

**Effective Date:** August 27, 2026  
**Version:** 1.0 (Zero-Knowledge Profile Isolation & ACE Privacy Standards)

---

## 1. Core Commitment: Purpose-Limited Career Personalization
CyberMentor is an AI-powered career mentor designed to help candidates break into and advance within cybersecurity. **All data collected by CyberMentor is used solely and exclusively to optimize the user experience, adapt coaching strategies, and personalize ongoing training within the application.**

- We do **not** sell, rent, monetize, or broker user data.
- We do **not** share user resumes, interview responses, or notes with third-party advertisers or recruitment agencies without explicit candidate authorization.
- Data collected is strictly operational to deliver intelligent, contextual career mentorship.

---

## 2. Zero-Knowledge & Complete Profile Isolation
Every candidate profile within CyberMentor is logically and cryptographically partitioned:

1. **User Isolation by Design**:
   - Data stored in Cloud Firestore and local session memory is strictly segregated by authenticated `user_id`.
   - Security rules enforce that only the authenticated owner (`request.auth.uid == userId`) has read, write, or delete permissions for their records.
2. **Protection from Administrators**:
   - Individual candidate conversational transcripts, voice recordings, resume files, and private ACE notes cannot be browsed, queried, or accessed by administrative staff or other users.
3. **Session-Level Ephemerality for Guests**:
   - For guest users (unauthenticated), conversation memory is ephemeral and exists only within the active session.

---

## 3. Right to Erasure: Instant Data Deletion
We believe you should own your career data. Candidates have the unconditional right to delete any and all stored information at any time:

- **One-Click Data Deletion**: Clicking the **"🗑️ Delete All My Data"** button in CyberMentor immediately triggers a hard cascade delete:
  - All stored conversation message histories are purged.
  - All cumulative ACE documented skills and competencies are permanently erased.
  - All long-term ACE memory notes and coaching strategy reflections are deleted.
  - All career progress milestones and resumes are erased.
  - All local cache and session tokens are cleared from your device.

---

## 4. Federated & Anonymized ACE Continuous Learning
You may wonder: *How does CyberMentor continue getting smarter without compromising individual privacy?*

CyberMentor utilizes **Differential Privacy & Anonymized Collective Strategy Distillation**:
- **PII Scrubbing**: When the Autonomous Agent with Continual Evolution (ACE) system identifies high-level pedagogical insights (e.g., *"Structuring SOC log analysis into 3-step PCAP labs increases student comprehension"*), all Personally Identifiable Information (names, emails, IP addresses, resumes, specific candidate identifiers) is permanently stripped.
- **Decoupled Global Heuristics**: Anonymized coaching insights are aggregated into a decentralized, generalized strategy pool (`global_ace_heuristics`).
- **Zero Profile Linkage**: When a user exercises their Right to Erasure and deletes their profile, their personal records and individualized ACE memories are 100% destroyed. The decoupled mathematical coaching heuristics remain intact without containing any trace of user-specific data.

---

## 5. Security Architecture
- **In-Transit Encryption**: All network traffic between your client and CyberMentor uses TLS 1.3 encryption.
- **At-Rest Encryption**: Cloud Firestore and storage buckets are encrypted using Google Cloud AES-256 keys.
- **Least Privilege Access**: Agent tools operate with strict scoped access policies adhering to the Principle of Least Privilege.

---

## 6. Questions & Contact
For questions regarding this Privacy Policy, data protection practices, or compliance inquiries, please contact the CyberMentor team or review the open-source repository at [https://github.com/cpfcoaching/cybermentor](https://github.com/cpfcoaching/cybermentor).
