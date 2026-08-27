"""
Certification Advisor Tool

Recommends certifications and learning order based on the user's
experience level, background, and career goals.
"""

# Certification roadmap database
_CERT_ROADMAPS = {
    "ciso": {
        "title": "CISO / Executive Security Leadership",
        "beginner": ["CompTIA Security+", "CISM (ISACA)"],
        "intermediate": ["CISSP (ISC2)", "CRISC (ISACA)", "GIAC GSLC (Security Leadership)"],
        "advanced": ["CISM (ISACA)", "CRISC (ISACA)", "CCISO (EC-Council)", "CGEIT (ISACA)", "Executive Leadership Programs (CMU/Wharton)"],
        "description": "Lead enterprise cybersecurity strategy, risk governance, budget control, and C-suite/Board reporting.",
        "avg_salary": "$180,000–$350,000+",
        "time_to_first_job": "10–20+ years IT & Security experience required for executive CISO roles",
    },
    "soc_analyst": {
        "title": "SOC Analyst / Blue Team",
        "beginner": ["CompTIA IT Fundamentals (ITF+)", "CompTIA A+", "CompTIA Network+", "CompTIA Security+"],
        "intermediate": ["CompTIA CySA+", "Splunk Core Certified User", "Blue Team Labs (BTL1)"],
        "advanced": ["CompTIA CASP+", "GIAC GCIH (Incident Handler)", "GIAC GCIA (Intrusion Analyst)"],
        "description": "Focus on monitoring, threat hunting, detecting, and responding to enterprise security events.",
        "avg_salary": "$65,000–$115,000",
        "time_to_first_job": "6–12 months for entry-level with Security+",
    },
    "penetration_tester": {
        "title": "Penetration Tester / Red Team",
        "beginner": ["CompTIA Network+", "CompTIA Security+", "eJPT (eLearnSecurity)"],
        "intermediate": ["CompTIA PenTest+", "CEH (EC-Council)", "PNPT (TCM Security)"],
        "advanced": ["OSCP (Offensive Security)", "CRTO (Certified Red Team Operator)", "OSEP", "GIAC GPEN"],
        "description": "Legally hack networks, web applications, and Active Directory to identify exploitable vulnerabilities.",
        "avg_salary": "$85,000–$145,000",
        "time_to_first_job": "12–24 months — labs and hands-on offensive skills essential",
    },
    "grc": {
        "title": "GRC (Governance, Risk & Compliance)",
        "beginner": ["CompTIA Security+", "CompTIA IT Fundamentals"],
        "intermediate": ["CISA (ISACA)", "CRISC (ISACA)", "ISO 27001 Lead Implementer"],
        "advanced": ["CISSP (ISC2)", "CISM (ISACA)", "CGEIT (ISACA)", "CIPP/E (IAPP Privacy)"],
        "description": "Manage security risk frameworks (NIST, ISO), policies, regulatory audits, and third-party risk.",
        "avg_salary": "$80,000–$135,000",
        "time_to_first_job": "6–18 months — business communication and risk modeling matter greatly",
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
    "dfir": {
        "title": "DFIR (Digital Forensics & Incident Response)",
        "beginner": ["CompTIA Security+", "CompTIA CySA+"],
        "intermediate": ["GCIH (GIAC Incident Handler)", "Certified Crime Scene / Forensics Tech"],
        "advanced": ["GCFA (GIAC Forensic Analyst)", "GNFA (Network Forensics)", "GREM (Reverse Engineering Malware)"],
        "description": "Investigate enterprise breaches, analyze malware binaries, rebuild attack timelines, and preserve digital evidence.",
        "avg_salary": "$95,000–$160,000",
        "time_to_first_job": "12–24 months — requires deep OS artifacts & memory analysis knowledge",
    },
    "appsec_devsecops": {
        "title": "Application Security & DevSecOps",
        "beginner": ["CompTIA Security+", "CompTIA Linux+"],
        "intermediate": ["Practical DevSecOps (CDSP)", "eWPT (Web Pen Tester)", "Certified Secure Software Programmer"],
        "advanced": ["CSSLP (ISC2)", "OSWE (OffSec Web Expert)", "GIAC GWEB (Web Defender)"],
        "description": "Embed security into developer CI/CD workflows, perform code reviews, SAST/DAST scanning, and threat modeling.",
        "avg_salary": "$110,000–$170,000",
        "time_to_first_job": "12–18 months — strong software development/coding foundation required",
    },
    "ot_ics_scada": {
        "title": "OT / ICS / SCADA Critical Infrastructure Security",
        "beginner": ["CompTIA Security+", "CompTIA Network+"],
        "intermediate": ["GICSP (Global Industrial Cyber Security Professional)", "ISA/IEC 62443 Fundamentals"],
        "advanced": ["GRID (GIAC Response and Industrial Defense)", "GCIP (Critical Infrastructure Protection)"],
        "description": "Protect industrial control systems, manufacturing plants, power grids, and SCADA networks from cyber threats.",
        "avg_salary": "$105,000–$165,000",
        "time_to_first_job": "18–24 months — requires understanding of industrial protocols (Modbus, DNP3, OPC)",
    },
    "ai_governance_security": {
        "title": "AI Security & AI Governance Specialist",
        "beginner": ["CompTIA Security+", "AI Fundamentals"],
        "intermediate": ["AIGP (IAPP Artificial Intelligence Governance Professional)", "NIST AI RMF Auditor"],
        "advanced": ["CISM", "CCSP", "Certified AI Security Specialist"],
        "description": "Govern Generative AI systems, mitigate LLM vulnerabilities (OWASP LLM Top 10), data leakage, and AI compliance.",
        "avg_salary": "$125,000–$190,000",
        "time_to_first_job": "High demand emerging field — fast entry for security pros with AI interest",
    },
    "iam_identity": {
        "title": "Identity & Access Management (IAM) & Zero Trust",
        "beginner": ["CompTIA Security+", "Microsoft SC-900"],
        "intermediate": ["Microsoft SC-300 (Identity & Access Admin)", "Okta Certified Administrator"],
        "advanced": ["CIAM (Certified Identity Management)", "Zero Trust Certified Architect (ZTCA)", "CISSP"],
        "description": "Design and enforce enterprise identity controls, Single Sign-On (SSO), PAM, and Zero Trust access architectures.",
        "avg_salary": "$95,000–$150,000",
        "time_to_first_job": "6–12 months — strong demand across all enterprise industries",
    },
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
