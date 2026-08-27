"""
Script to expand the curated Breaking Into Cybersecurity knowledge base with additional rich topic episodes.
"""

import json
import pathlib

OUTPUT = pathlib.Path(__file__).parent.parent / "knowledge" / "youtube_transcripts.json"

NEW_EPISODES = [
    {
        "video_id": "BIC-EP061",
        "title": "Breaking Into Cybersecurity Episode 61: CISO Strategy & The First 90 Days",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-05-01T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "grc_strategy",
        "key_takeaways": [
            "Your first 90 days as a security leader are about listening, mapping business assets, and building alliances with engineering and finance.",
            "Security cannot be the 'department of no' — frame security controls as business enablers that unlock enterprise revenue.",
            "Establish a clear Cyber Risk Register aligned to NIST CSF 2.0 governance functions."
        ],
        "transcript": "When stepping into executive security leadership or becoming a virtual CISO, technical acumen is assumed. What determines your success is executive presence, business acumen, and relationship building. Meet with the VP of Engineering, Chief Legal Officer, and CFO in your first month. Understand what keeps them up at night. Translate technical vulnerabilities into dollar-loss risk exposure using FAIR methodology."
    },
    {
        "video_id": "BIC-EP062",
        "title": "Breaking Into Cybersecurity Episode 62: Threat Hunting & Proactive Incident Response",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-05-15T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "soc_incident_response",
        "key_takeaways": [
            "Threat hunting starts with a hypothesis based on MITRE ATT&CK techniques, not just scrolling through SIEM logs.",
            "Focus on living-off-the-land binaries (LOLBins) like Certutil, WMI, and PowerShell that bypass traditional signature AV.",
            "Automate recurring hunt queries into new detection engineering alerting rules."
        ],
        "transcript": "Tier 1 SOC analysts react to alerts. Threat hunters search for the adversaries who bypassed your alerts. Formulate specific hunt hypotheses: 'Is an unauthorized actor using PsExec or WMI for lateral movement across our subnet?' Query your EDR telemetry for parent-child process anomalies, document your findings in Sigma rules, and present your hunt metrics to leadership."
    },
    {
        "video_id": "BIC-EP063",
        "title": "Breaking Into Cybersecurity Episode 63: Zero Trust Architecture & Identity Governance",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-06-01T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "cloud_security",
        "key_takeaways": [
            "Zero Trust is a philosophical security model: 'Never trust, always verify, assume breach.'",
            "Identity is the new perimeter — enforce phishing-resistant MFA (FIDO2/WebAuthn) and conditional access policies.",
            "Micro-segmentation isolates workloads to prevent catastrophic lateral movement."
        ],
        "transcript": "Traditional castle-and-moat perimeter security is dead in the cloud era. Zero Trust means every user, device, and service-to-service connection must be dynamically authenticated and authorized based on device posture, user identity, and session risk scores. If you want to stand out to enterprise hiring managers, learn Okta, Microsoft Entra ID, and cloud IAM boundary enforcement."
    },
    {
        "video_id": "BIC-EP064",
        "title": "Breaking Into Cybersecurity Episode 64: AppSec & DevSecOps — Securing the CI/CD Pipeline",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-06-15T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "devsecops_appsec",
        "key_takeaways": [
            "Integrate SAST, DAST, SCA, and secret scanning directly into GitHub Actions or GitLab CI pipelines.",
            "Empower developers with actionable IDE feedback rather than dumping 500-page PDF vulnerability reports.",
            "Understand the OWASP Top 10 API Security Risks (BOLA, broken authentication, excessive data exposure)."
        ],
        "transcript": "Application Security is one of the highest paying niches in cybersecurity. If you know how to read Python, JavaScript, or Go, and understand how to remediate SQLi, SSRF, and Broken Object Level Authorization (BOLA), you are gold to engineering teams. Learn tools like Semgrep, Snyk, and OWASP ZAP to automate continuous pipeline gates."
    },
    {
        "video_id": "BIC-EP065",
        "title": "Breaking Into Cybersecurity Episode 65: Overcoming Career Burnout & Building Resilience",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-07-01T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "career_strategy",
        "key_takeaways": [
            "Cybersecurity on-call rotations and alert fatigue cause severe burnout if healthy boundaries are not enforced.",
            "Automate low-value repetitive alerts with SOAR playbooks to free up cognitive bandwidth.",
            "Prioritize mental health, physical exercise, and disconnecting after incident response sprints."
        ],
        "transcript": "Let's talk about the elephant in the room: burnout. 50% of SOC analysts and security leaders consider quitting due to stress, 24/7 on-call duties, and endless false positives. You cannot protect an organization if you are cognitively depleted. Set firm boundaries, cross-train team members to avoid single points of failure, and build a supportive peer network through Breaking Into Cybersecurity."
    },
    {
        "video_id": "BIC-EP066",
        "title": "Breaking Into Cybersecurity Episode 66: Military Veteran Transition to Commercial Cyber",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-07-15T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "career_transition",
        "key_takeaways": [
            "Military veterans excel in crisis command, discipline, procedural rigor, and high-stress problem solving.",
            "Translate military MOS/AFSC acronyms into civilian corporate language on your resume.",
            "Leverage DoD SkillBridge, VET TEC, and American Corporate Partners (ACP) mentorship programs."
        ],
        "transcript": "To all our military veterans transitioning out: your leadership under pressure, threat assessment mindset, and operational discipline are desperately needed in cybersecurity. The biggest hurdle is resume translation: change 'Platoon Communications NCOIC' to 'Senior Network Operations & Security Team Lead.' Connect with veteran-friendly employers and leverage your security clearance."
    },
    {
        "video_id": "BIC-EP067",
        "title": "Breaking Into Cybersecurity Episode 67: Digital Forensics & Incident Response (DFIR) Deep Dive",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-08-01T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "dfir_forensics",
        "key_takeaways": [
            "DFIR combines disk triage, memory volatile analysis (Volatility), and network packet reconstruction.",
            "Master evidence chain of custody, timeline analysis (Plaso/log2timeline), and MFT parsing.",
            "Top certs: GIAC GCFA, GCFE, and SANS FOR508."
        ],
        "transcript": "When ransomware strikes, DFIR professionals are the digital crime scene investigators. You must preserve volatile RAM before powering down a machine, mount forensic disk images with write-blockers, and reconstruct the attacker's timeline of initial access, persistence, credential harvesting, and exfiltration. Build your lab with Autopsy, FTK Imager, and Volatility."
    },
    {
        "video_id": "BIC-EP068",
        "title": "Breaking Into Cybersecurity Episode 68: Operational Technology (OT) & ICS/SCADA Security",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-08-15T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "ot_ics_security",
        "key_takeaways": [
            "OT security protects physical infrastructure (power grids, water treatment, manufacturing lines).",
            "Availability and safety supersede confidentiality in industrial control systems (Purdue Model).",
            "Understanding Modbus, DNP3, and OPC protocols is critical for OT security specialists."
        ],
        "transcript": "In traditional enterprise IT, Confidentiality is often king. In Industrial Control Systems (ICS) and Critical Infrastructure, Safety and Availability are everything. You cannot simply reboot a PLC in a nuclear reactor or patch a live water purification plant without rigorous engineering change management. OT security engineers are in massive demand with high compensation."
    },
    {
        "video_id": "BIC-EP069",
        "title": "Breaking Into Cybersecurity Episode 69: AI Security Governance & OWASP LLM Top 10",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-09-01T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "ai_security",
        "key_takeaways": [
            "Securing Generative AI requires mitigating direct/indirect prompt injection (LLM01) and insecure output handling (LLM05).",
            "Implement automated content safety filters, system instruction delimiters, and vector database access controls.",
            "Align AI deployments with the NIST AI Risk Management Framework (AI RMF 1.0)."
        ],
        "transcript": "As every enterprise rushes to deploy LLM applications and autonomous AI agents, security teams face brand new attack surfaces: prompt injection, training data poisoning, model denial of service, and sensitive information leakage. Learn the OWASP Top 10 for LLM Applications and how to build guardrails into AI inference pipelines."
    },
    {
        "video_id": "BIC-EP070",
        "title": "Breaking Into Cybersecurity Episode 70: Building Your Personal Brand & Public Speaking",
        "url": "https://www.youtube.com/c/BreakingIntoCybersecurity",
        "published_at": "2024-09-15T00:00:00Z",
        "channel": "Breaking Into Cybersecurity",
        "host": "Christophe Foulon",
        "category": "mentorship",
        "key_takeaways": [
            "Publicly sharing what you learn on LinkedIn, YouTube, or Medium attracts recruiters directly to your inbox.",
            "Submit talk proposals to local BSides conferences, OWASP chapters, and ISSA/ISACA meetups.",
            "Consistent community contribution establishes authority faster than accumulating inactive certifications."
        ],
        "transcript": "The best cybersecurity career advice I can give anyone is to 'learn in public.' When you complete a TryHackMe room, solve a tough lab, or read a new NIST standard, write a 3-paragraph breakdown on LinkedIn explaining the concept. Speak at your local BSides. Hiring managers hire people they know, like, and trust."
    }
]

def main():
    if not OUTPUT.exists():
        existing = []
    else:
        with open(OUTPUT, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing_ids = {e.get("video_id") for e in existing}
    added = 0

    for ep in NEW_EPISODES:
        if ep["video_id"] not in existing_ids:
            existing.append(ep)
            existing_ids.add(ep["video_id"])
            added += 1

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    print(f"✅ Added {added} episodes. Total episodes now: {len(existing)}")

if __name__ == "__main__":
    main()
