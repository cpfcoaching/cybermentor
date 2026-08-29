"""
Certification Advisor Tool

Recommends certifications and learning order based on the user's
experience level, background, and career goals.
"""

# Certification roadmap database
_CERT_ROADMAPS = {
    "software_developer": {
        "title": "Software Developer / Software Engineer",
        "beginner": ["AWS Certified Cloud Practitioner", "Meta Front-End/Back-End Developer Certificate"],
        "intermediate": ["AWS Certified Developer - Associate", "Google Cloud Professional Developer", "GitHub Actions Certification"],
        "advanced": ["Certified Kubernetes Application Developer (CKAD)", "AWS Solutions Architect - Associate"],
        "description": "Design, build, and optimize scalable software systems, backend APIs, distributed microservices, and modern web applications.",
        "avg_salary": "$90,000–$165,000",
        "time_to_first_job": "6–12 months with strong GitHub portfolio & full-stack projects",
    },
    "security_software_engineer": {
        "title": "Security Software Engineer (AppSec / DevSecOps)",
        "beginner": ["CompTIA Security+", "CSSLP (Certified Secure Software Lifecycle Professional)"],
        "intermediate": ["Certified DevSecOps Professional (CDP)", "OffSec Web Expert (OSWE)", "eWPT (Web Pen Tester)"],
        "advanced": ["SANS SEC540 (Cloud DevSecOps)", "GIAC GWEB", "CASE (Certified Application Security Engineer)", "ISC2 CISSP"],
        "description": "Embed security into developer CI/CD workflows, perform threat modeling, SAST/DAST automation, and architect secure code.",
        "avg_salary": "$120,000–$185,000",
        "time_to_first_job": "12–18 months — strong coding and OWASP ASVS knowledge required",
    },
    "ai_developer": {
        "title": "AI Developer / LLM Application Engineer",
        "beginner": ["Google Cloud Digital Leader", "DeepLearning.AI Generative AI Specialist"],
        "intermediate": ["Google Cloud Professional Machine Learning Engineer", "AWS Certified AI Practitioner", "Databricks Generative AI Engineer"],
        "advanced": ["TensorFlow Developer Certificate", "NVIDIA Deep Learning Institute Certification"],
        "description": "Architect and deploy GenAI applications, multi-agent frameworks (Antigravity SDK), RAG systems, and fine-tuned LLM services.",
        "avg_salary": "$130,000–$210,000",
        "time_to_first_job": "3–9 months for experienced coders pivoting into GenAI",
    },
    "ai_security_specialist": {
        "title": "AI Security Specialist / AI Safety Engineer",
        "beginner": ["CompTIA Security+", "IAPP AIGP (AI Governance Professional)"],
        "intermediate": ["Certified AI Security Professional (CAISP)", "SANS SEC595 (AI Security & LLM Defense)"],
        "advanced": ["OffSec OSDA", "MIT Professional Certificate in AI Safety", "ISC2 CISSP with AI Security Specialization"],
        "description": "Defend AI systems against prompt injection, model extraction, data poisoning, and secure RAG vector embeddings.",
        "avg_salary": "$135,000–$225,000",
        "time_to_first_job": "Emerging high-growth role — rapid placement for cybersecurity professionals with LLM security knowledge",
    },
    "prompt_engineer": {
        "title": "Prompt Engineer / LLM Guardrail Specialist",
        "beginner": ["Anthropic Prompt Engineering Certification", "Vanderbilt Prompt Engineering Specialization"],
        "intermediate": ["OpenAI Certified Prompt Architect", "DeepLearning.AI Prompt Engineering for Developers"],
        "advanced": ["AWS Certified AI Practitioner", "LangChain Certified Developer"],
        "description": "Optimize few-shot and chain-of-thought prompts, design semantic injection guardrails, and benchmark LLM response evaluations.",
        "avg_salary": "$95,000–$160,000",
        "time_to_first_job": "2–6 months — strong linguistic precision and evaluation benchmark portfolio",
    },
    "forward_deployed_engineer": {
        "title": "Forward Deployed Engineer (FDE)",
        "beginner": ["AWS Certified Solutions Architect - Associate", "CompTIA Security+"],
        "intermediate": ["Google Cloud Professional Cloud Architect", "Certified Kubernetes Administrator (CKA)"],
        "advanced": ["AWS Solutions Architect - Professional", "HashiCorp Certified: Terraform Associate"],
        "description": "Deploy, customize, and integrate enterprise platforms on-site for high-value clients across complex multi-cloud and air-gapped environments.",
        "avg_salary": "$130,000–$200,000",
        "time_to_first_job": "6–12 months with strong client-facing technical skills",
    },
    "cloud_engineer": {
        "title": "Cloud Engineer / Infrastructure Architect",
        "beginner": ["AWS Cloud Practitioner", "Google Cloud Digital Leader"],
        "intermediate": ["AWS Solutions Architect - Associate", "Google Cloud Professional Cloud Architect", "CKA (Kubernetes)"],
        "advanced": ["AWS Solutions Architect - Professional", "HashiCorp Terraform Associate"],
        "description": "Build, manage, and scale cloud infrastructure, Kubernetes clusters, GitOps pipelines, and Terraform fleets.",
        "avg_salary": "$105,000–$165,000",
        "time_to_first_job": "6–12 months from IT sysadmin",
    },
    "cloud_security": {
        "title": "Cloud Security Engineer",
        "beginner": ["CompTIA Cloud+", "AWS Cloud Practitioner", "Google Cloud Digital Leader"],
        "intermediate": ["CompTIA Security+", "AWS Security Specialty", "Google Professional Cloud Security Engineer"],
        "advanced": ["CCSP (ISC2)", "CISSP", "Microsoft SC-100 (Cybersecurity Architect)", "Azure Security Engineer Associate"],
        "description": "Secure multi-cloud infrastructure, IAM policy, container security, and CI/CD pipelines across AWS/GCP/Azure.",
        "avg_salary": "$115,000–$175,000",
        "time_to_first_job": "12–18 months from zero — faster with IT/sysadmin background",
    },
    "security_engineer": {
        "title": "Security Engineer (SecOps & Infrastructure)",
        "beginner": ["CompTIA Security+", "Microsoft SC-900"],
        "intermediate": ["CompTIA CySA+", "GIAC GSEC", "Microsoft SC-200 (Security Operations Analyst)"],
        "advanced": ["GIAC GCED", "ISC2 SSCP", "Palo Alto PCNSE", "ISC2 CISSP"],
        "description": "Engineer enterprise identity (SSO/MFA), endpoint EDR systems, vulnerability management, and automated security SOAR playbooks.",
        "avg_salary": "$100,000–$160,000",
        "time_to_first_job": "6–12 months with hands-on enterprise security lab experience",
    },
    "network_security_engineer": {
        "title": "Network Security Engineer",
        "beginner": ["CompTIA Network+", "Cisco CCNA"],
        "intermediate": ["Cisco CCNP Security", "Palo Alto PCNSE", "Fortinet NSE 4/7"],
        "advanced": ["GIAC GNFA (Network Forensics)", "Check Point CCSA/CCSE", "Cisco CCIE Security"],
        "description": "Defend enterprise network perimeters, deploy Next-Gen Firewalls, configure Zero Trust Network Access (ZTNA), and inspect encrypted traffic.",
        "avg_salary": "$95,000–$155,000",
        "time_to_first_job": "6–12 months from networking foundations",
    },
    "soc_analyst": {
        "title": "SOC Analyst / Blue Team",
        "beginner": ["CompTIA Network+", "CompTIA Security+", "Cisco CyberOps Associate"],
        "intermediate": ["CompTIA CySA+", "Splunk Core Certified User", "Blue Team Labs (BTL1)", "Microsoft SC-200"],
        "advanced": ["CompTIA CASP+", "GIAC GCIH (Incident Handler)", "GIAC GCIA (Intrusion Analyst)"],
        "description": "Monitor enterprise SIEM telemetry, investigate alerts, analyze PCAPs, and contain security incidents.",
        "avg_salary": "$65,000–$115,000",
        "time_to_first_job": "6–12 months for entry-level with Security+",
    },
    "penetration_tester": {
        "title": "Penetration Tester / Ethical Hacker",
        "beginner": ["CompTIA Network+", "CompTIA Security+", "eJPT (eLearnSecurity)"],
        "intermediate": ["CompTIA PenTest+", "CEH (EC-Council)", "PNPT (TCM Security)"],
        "advanced": ["OSCP (Offensive Security)", "CRTO (Certified Red Team Operator)", "OffSec OSWE", "GIAC GPEN"],
        "description": "Legally exploit web applications, networks, and Active Directory domains to find and report critical vulnerabilities.",
        "avg_salary": "$85,000–$145,000",
        "time_to_first_job": "12–24 months — labs and hands-on offensive skills essential",
    },
    "red_team": {
        "title": "Red Teamer / Offensive Operations",
        "beginner": ["CompTIA PenTest+", "OffSec OSCP"],
        "intermediate": ["Zero-Point Security CRTO (Red Team Operator)", "OffSec OSEP (Evasion Techniques)"],
        "advanced": ["CRTE (Red Team Expert)", "SANS SEC565 (Red Team Operations)", "OffSec OSMR"],
        "description": "Emulate advanced nation-state adversaries, deploy C2 frameworks, bypass EDR/AV detections, and perform multi-forest compromises.",
        "avg_salary": "$115,000–$185,000",
        "time_to_first_job": "2–4 years offensive experience required",
    },
    "grc": {
        "title": "GRC (Governance, Risk & Compliance) Analyst",
        "beginner": ["CompTIA Security+", "ISACA ITCA"],
        "intermediate": ["CISA (ISACA)", "CRISC (ISACA)", "ISO 27001 Lead Implementer"],
        "advanced": ["CISSP (ISC2)", "CISM (ISACA)", "CGEIT (ISACA)", "CIPP/E (IAPP Privacy)"],
        "description": "Manage security risk frameworks (NIST, ISO), policies, regulatory audits, and third-party vendor risk assessments.",
        "avg_salary": "$80,000–$135,000",
        "time_to_first_job": "6–18 months — business communication and risk modeling matter greatly",
    },
    "grc_leader": {
        "title": "GRC Leader / VP of Risk & Compliance",
        "beginner": ["CompTIA Security+", "CISA (ISACA)"],
        "intermediate": ["CISM (ISACA)", "CRISC (ISACA)", "ISO 27001 Lead Auditor"],
        "advanced": ["ISC2 CISSP", "ISACA CGEIT", "Open FAIR Certification"],
        "description": "Direct global compliance operations, quantify cyber risk in financial terms for the Board, and oversee multi-jurisdiction regulatory examinations.",
        "avg_salary": "$150,000–$240,000",
        "time_to_first_job": "7–15 years enterprise governance experience",
    },
    "privacy_specialist": {
        "title": "Privacy Specialist / Data Protection Officer (DPO)",
        "beginner": ["CompTIA Security+", "IAPP CIPM (Privacy Manager)"],
        "intermediate": ["IAPP CIPP/US", "IAPP CIPP/E (European Privacy)", "IAPP CIPT (Privacy Technologist)"],
        "advanced": ["ISACA CDPSE (Data Privacy Solutions Engineer)", "FIP (Fellow of Information Privacy)"],
        "description": "Enforce GDPR, CCPA/CPRA, perform Data Privacy Impact Assessments (DPIAs), and build Privacy-by-Design data architectures.",
        "avg_salary": "$95,000–$160,000",
        "time_to_first_job": "6–12 months with IAPP certification",
    },
    "policy_specialist": {
        "title": "Policy Specialist / Cyber Regulatory Strategist",
        "beginner": ["CompTIA Security+", "ISACA ITCA"],
        "intermediate": ["ISC2 CGRC (Governance, Risk & Compliance)", "ISACA CGEIT"],
        "advanced": ["SANS MGT514 (Security Strategic Planning)", "Harvard/Georgetown Cyber Policy Certificate"],
        "description": "Author enterprise security standards, align with SEC Cyber Disclosure rules, and design enterprise AI acceptable-use governance.",
        "avg_salary": "$90,000–$150,000",
        "time_to_first_job": "6–12 months",
    },
    "dfir": {
        "title": "DFIR (Digital Forensics & Incident Response)",
        "beginner": ["CompTIA Security+", "CompTIA CySA+"],
        "intermediate": ["GCIH (GIAC Incident Handler)", "Certified Crime Scene / Forensics Tech"],
        "advanced": ["GCFA (GIAC Forensic Analyst)", "GNFA (Network Forensics)", "GREM (Reverse Engineering Malware)"],
        "description": "Investigate enterprise breaches, analyze malware binaries, rebuild attack timelines, and preserve digital evidence.",
        "avg_salary": "$95,000–$160,000",
        "time_to_first_job": "12–24 months — requires deep OS artifacts & memory analysis knowledge",
    },
    "ciso": {
        "title": "CISO / Executive Security Leadership",
        "beginner": ["CompTIA Security+", "CISM (ISACA)"],
        "intermediate": ["CISSP (ISC2)", "CRISC (ISACA)", "GIAC GSLC (Security Leadership)"],
        "advanced": ["CISM (ISACA)", "CRISC (ISACA)", "CCISO (EC-Council)", "CGEIT (ISACA)", "Executive Leadership Programs (CMU/Wharton)"],
        "description": "Lead enterprise cybersecurity strategy, risk governance, budget control, and C-suite/Board reporting.",
        "avg_salary": "$180,000–$350,000+",
        "time_to_first_job": "10–20+ years IT & Security experience required for executive CISO roles",
    },
    "it_helpdesk": {
        "title": "IT Helpdesk / Systems Support",
        "beginner": ["CompTIA A+", "Google IT Support Professional"],
        "intermediate": ["CompTIA Network+", "Microsoft MD-102 (Endpoint Administrator)"],
        "advanced": ["CompTIA Security+", "Microsoft SC-900 (Security Fundamentals)"],
        "description": "Provide enterprise operating system support, manage Active Directory users, troubleshoot network routing, and manage endpoint fleets.",
        "avg_salary": "$45,000–$75,000",
        "time_to_first_job": "1–3 months with CompTIA A+",
    }
}


def recommend_certifications(
    experience_level: str,
    career_goal: str,
) -> str:
    """Recommend cybersecurity certifications based on experience and career goal.

    Use this tool when the user asks which certifications they should get,
    what their learning path should be, or how to get into a specific security role.

    Args:
        experience_level: The user's current level. One of: "beginner"
                          (no IT/security experience), "intermediate"
                          (1-3 years IT/security experience), "advanced"
                          (3+ years, or already in security).
        career_goal: The security career the user wants. One of: "soc_analyst",
                     "penetration_tester", "grc", "cloud_security", "ciso".
                     Use the closest match based on what the user described.

    Returns:
        A formatted certification roadmap with recommended certs in order,
        salary info, and time-to-hire estimates.
    """
    goal_key = career_goal.lower().replace(" ", "_").replace("-", "_")
    level = experience_level.lower()

    if goal_key not in _CERT_ROADMAPS:
        # Best-effort fallback
        return (
            f"I don't have a specific roadmap for '{career_goal}' in my database, "
            "but I can help you build a custom path. Generally, start with CompTIA "
            "Security+ if you're new to security — it's the universal foundation. "
            "Tell me more about what you want to do day-to-day and I'll give you "
            "a tailored recommendation."
        )

    roadmap = _CERT_ROADMAPS[goal_key]

    # Build cert sequence
    start_certs = roadmap.get("beginner", [])
    mid_certs = roadmap.get("intermediate", [])
    adv_certs = roadmap.get("advanced", [])

    if level == "beginner":
        immediate = start_certs
        next_up = mid_certs[:2]
    elif level == "intermediate":
        immediate = mid_certs
        next_up = adv_certs[:2]
    else:  # advanced
        immediate = adv_certs
        next_up = []

    immediate_str = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(immediate))
    next_str = "\n".join(f"  - {c}" for c in next_up) if next_up else "  (You're on the advanced track!)"

    output = f"""## 🗺️ Certification Roadmap: {roadmap['title']}

**Your Profile:** {experience_level.title()} | Target: {roadmap['title']}

---

### 📌 Role Overview
{roadmap['description']}

💰 **Salary Range:** {roadmap['avg_salary']}
⏱️ **Time to First Job:** {roadmap['time_to_first_job']}

---

### 🎯 Start Here (Your Immediate Next Certs)
{immediate_str}

### 🔭 Then Work Toward
{next_str}

### 🏁 Full Roadmap (All Levels)
**Foundation:**
{chr(10).join(f'  • {c}' for c in start_certs)}

**Intermediate:**
{chr(10).join(f'  • {c}' for c in mid_certs)}

**Advanced:**
{chr(10).join(f'  • {c}' for c in adv_certs)}

---

### 💡 Key Advice for {roadmap['title']}
- Certifications open doors, but **hands-on labs** close deals in interviews
- Don't wait to be "ready" — schedule the exam when you're at 85% in practice tests
- Build a portfolio: GitHub projects, TryHackMe profile, or a home lab writeup

---
*Cross-referenced with the [Paul Jerimy Security Certification Roadmap](https://pauljerimy.com/security-certification-roadmap/) matrix, [Hadess Certificate Roadmap](https://career.hadess.io/certificate-roadmap), and [Cyberdudekz Security Cert Roadmap](https://github.com/cyberdudekz/security-cert-roadmap).*
*Want me to generate a detailed study plan for your next cert? Just ask!*"""

    return output
