"""
Resume Analyzer Tool

Analyzes a cybersecurity resume and provides structured, actionable
gap analysis and improvement recommendations.
"""


def analyze_resume(resume_text: str, target_role: str = "general") -> str:
    """Analyze a cybersecurity resume and provide gap analysis and improvement tips.

    Use this tool when the user pastes their resume or describes their work
    experience and asks for feedback targeted at cybersecurity roles.

    Args:
        resume_text: The full text of the user's resume. Encourage users to paste
                     the plain text of their resume for best results.
        target_role: The specific cybersecurity role to optimize for. One of:
                     "soc_analyst", "penetration_tester", "grc", "cloud_security",
                     "general". Defaults to "general" for broad feedback.

    Returns:
        A structured resume analysis with a score, identified strengths,
        critical gaps, and specific action items.
    """
    text_lower = resume_text.lower()
    word_count = len(resume_text.split())

    # ── Skill signal detection ────────────────────────────────────────────────
    cert_keywords = [
        "security+", "cysa+", "casp+", "ceh", "cissp", "cism", "oscp",
        "ejpt", "pnpt", "comptia", "isc2", "isaca", "sans", "giac",
        "aws certified", "google cloud", "azure security",
    ]
    tool_keywords = [
        "splunk", "siem", "wireshark", "nmap", "metasploit", "burp suite",
        "nessus", "qualys", "crowdstrike", "sentinelone", "palo alto",
        "firewall", "ids", "ips", "soc", "endpoint", "vulnerability",
        "incident response", "threat hunting", "penetration test",
    ]
    soft_keywords = [
        "led", "managed", "collaborated", "communicated", "trained",
        "mentored", "presented", "documented",
    ]
    quantified_keywords = ["%", "$", "reduced", "improved", "increased", "saved"]
    education_keywords = [
        "bachelor", "master", "degree", "bs", "ms", "mba",
        "cybersecurity", "computer science", "information technology",
    ]

    found_certs = [k for k in cert_keywords if k in text_lower]
    found_tools = [k for k in tool_keywords if k in text_lower]
    found_soft = [k for k in soft_keywords if k in text_lower]
    has_quantification = any(k in text_lower for k in quantified_keywords)
    has_education = any(k in text_lower for k in education_keywords)
    has_contact = any(k in text_lower for k in ["linkedin", "github", "@", "phone"])

    # ── Scoring ───────────────────────────────────────────────────────────────
    score = 0
    score += min(30, len(found_certs) * 10)  # Up to 30 pts for certs
    score += min(25, len(found_tools) * 5)    # Up to 25 pts for tools
    score += 15 if has_quantification else 0   # 15 pts for quantified achievements
    score += 10 if has_education else 0        # 10 pts for education
    score += 10 if has_contact else 0          # 10 pts for contact completeness
    score += min(10, len(found_soft) * 2)      # Up to 10 pts for soft skills

    score = min(100, score)
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D"

    # ── Build feedback ────────────────────────────────────────────────────────
    strengths = []
    gaps = []
    actions = []

    if found_certs:
        strengths.append(f"Certifications found: {', '.join(found_certs[:5]).title()}")
    else:
        gaps.append("No certifications detected — security certifications are often a baseline requirement")
        actions.append("Prioritize earning CompTIA Security+ as your first cert if you don't have one")

    if found_tools:
        strengths.append(f"Security tools mentioned: {', '.join(found_tools[:6])}")
    else:
        gaps.append("No specific security tools mentioned — hiring managers look for tool familiarity")
        actions.append("Add a 'Technical Skills' section listing specific tools, platforms, and technologies you've used")

    if has_quantification:
        strengths.append("Resume includes quantified achievements (numbers, percentages, or dollar amounts)")
    else:
        gaps.append("No quantified achievements found — resumes without numbers are less compelling")
        actions.append("Add metrics to every bullet: 'Reduced false positive rate by 30%', 'Monitored 500+ endpoints', etc.")

    if not has_contact:
        gaps.append("Contact information or professional profile links may be incomplete")
        actions.append("Ensure your LinkedIn URL and GitHub profile (if applicable) are in the header")

    if word_count < 200:
        gaps.append("Resume appears very short — may lack sufficient detail to compete")
        actions.append("Expand each role with 3-5 bullet points describing specific responsibilities and achievements")

    # Role-specific gaps
    role_specific_tools = {
        "soc_analyst": ["splunk", "siem", "endpoint", "threat hunting"],
        "penetration_tester": ["nmap", "metasploit", "burp suite", "penetration test"],
        "grc": ["risk", "audit", "compliance", "policy", "iso 27001", "nist"],
        "cloud_security": ["aws", "azure", "gcp", "cloud", "iam", "terraform"],
    }
    if target_role.lower() in role_specific_tools:
        missing_role_tools = [t for t in role_specific_tools[target_role.lower()] if t not in text_lower]
        if missing_role_tools:
            gaps.append(f"For a {target_role.replace('_', ' ').title()} role, these keywords are missing: {', '.join(missing_role_tools)}")
            actions.append(f"Add relevant {target_role.replace('_', ' ').title()} keywords to match job description language")

    strengths_str = "\n".join(f"  ✅ {s}" for s in strengths) if strengths else "  No major strengths automatically detected — manual review recommended."
    gaps_str = "\n".join(f"  ⚠️  {g}" for g in gaps) if gaps else "  No major gaps detected!"
    actions_str = "\n".join(f"  {i+1}. {a}" for i, a in enumerate(actions)) if actions else "  Your resume looks solid — focus on tailoring to each job description."

    return f"""## 📄 Resume Analysis — {target_role.replace('_', ' ').title()} Focus

**Overall Score: {score}/100 (Grade: {grade})**

---

### ✅ Strengths
{strengths_str}

### ⚠️ Gaps Identified
{gaps_str}

### 🎯 Action Items (Priority Order)
{actions_str}

### 💡 General Resume Best Practices for Cybersecurity
1. **Tailor for each application** — copy exact keywords from the job description
2. **Lead with impact** — start every bullet with a strong action verb
3. **One page for < 5 years experience** — two pages is fine for senior roles
4. **ATS-friendly format** — avoid tables, columns, headers/footers in Word docs
5. **Include a 'Projects' section** — home lab, CTF wins, and GitHub are gold

---
*Want me to help rewrite specific sections or bullet points? Paste them and I'll coach you through it.*"""
