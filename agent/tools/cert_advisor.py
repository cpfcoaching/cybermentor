"""
Certification Advisor Tool

Recommends certifications and learning order based on the user's
experience level, background, and career goals.
"""

# Certification roadmap database
_CERT_ROADMAPS = {
    "soc_analyst": {
        "title": "SOC Analyst / Blue Team",
        "beginner": ["CompTIA IT Fundamentals (ITF+)", "CompTIA A+", "CompTIA Network+", "CompTIA Security+"],
        "intermediate": ["CompTIA CySA+", "Splunk Core Certified User", "Blue Team Labs certification"],
        "advanced": ["CompTIA CASP+", "GIAC GCIH (Incident Handler)", "GIAC GCIA (Intrusion Analyst)"],
        "description": "Focus on monitoring, detecting, and responding to security events.",
        "avg_salary": "$65,000–$95,000",
        "time_to_first_job": "6–12 months for entry-level with Security+",
    },
    "penetration_tester": {
        "title": "Penetration Tester / Red Team",
        "beginner": ["CompTIA Network+", "CompTIA Security+", "eJPT (eLearnSecurity)"],
        "intermediate": ["CompTIA PenTest+", "CEH (EC-Council)", "PNPT (TCM Security)"],
        "advanced": ["OSCP (Offensive Security)", "CRTO", "GIAC GPEN"],
        "description": "Legally hack systems to find vulnerabilities before attackers do.",
        "avg_salary": "$80,000–$130,000",
        "time_to_first_job": "12–24 months — labs are more important than certs here",
    },
    "grc": {
        "title": "GRC (Governance, Risk & Compliance)",
        "beginner": ["CompTIA Security+", "CompTIA IT Fundamentals"],
        "intermediate": ["CISA (ISACA)", "CRISC (ISACA)", "ISO 27001 Lead Implementer"],
        "advanced": ["CISSP (ISC2)", "CGEIT (ISACA)", "CISM (ISACA)"],
        "description": "Manage security risk, policies, audits, and regulatory compliance.",
        "avg_salary": "$75,000–$120,000",
        "time_to_first_job": "6–18 months — business communication skills matter a lot",
    },
    "cloud_security": {
        "title": "Cloud Security Engineer",
        "beginner": ["CompTIA Cloud+", "AWS Cloud Practitioner", "Google Cloud Digital Leader"],
        "intermediate": ["CompTIA Security+", "AWS Security Specialty", "Google Professional Cloud Security Engineer"],
        "advanced": ["CCSP (ISC2)", "CISSP", "Azure Security Engineer Associate"],
        "description": "Secure cloud infrastructure, identity, and workloads across AWS/GCP/Azure.",
        "avg_salary": "$110,000–$160,000",
        "time_to_first_job": "12–18 months from zero — faster if you have IT background",
    },
    "ciso": {
        "title": "CISO / Security Leadership",
        "beginner": ["CompTIA Security+", "CISM (ISACA)"],
        "intermediate": ["CISSP (ISC2)", "MBA or relevant degree often helps"],
        "advanced": ["CISM", "CRISC", "Executive leadership programs"],
        "description": "Lead an organization's security strategy, team, and board reporting.",
        "avg_salary": "$150,000–$300,000+",
        "time_to_first_job": "15–25 years experience typically required for true CISO roles",
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

*Want me to generate a detailed study plan for your first cert? Just ask!*"""

    return output
