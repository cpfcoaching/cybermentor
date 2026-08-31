import json
from agent.tools.ace_memory import get_documented_candidate_skills


def analyze_resume(resume_text: str, target_role: str = "general", user_id: str = "guest") -> str:
    """Analyze a cybersecurity resume, extract existing competencies, probe for missing skills, and cross-reference ACE memory.

    Use this tool when the user pastes or uploads their resume text and asks for feedback.
    This tool extracts all identified skills, cross-references any previously documented
    competencies stored in ACE cognitive memory across past conversations, scores ATS readiness,
    and generates proactive probing questions for unlisted skills.

    Args:
        resume_text: The full text of the user's resume.
        target_role: The specific cybersecurity role to optimize for ("soc_analyst",
                     "penetration_tester", "grc", "cloud_security", "dfir", "general").
        user_id: The candidate ID to cross-reference documented skills from past ACE conversations.

    Returns:
        A structured resume analysis with extracted competencies, ACE memory cross-checks,
        ATS score, identified strengths/gaps, and proactive probing questions.
    """
    text_lower = resume_text.lower()
    word_count = len(resume_text.split())

    # ── Categorized Skill Taxonomy ────────────────────────────────────────────
    taxonomy = {
        "Certifications": [
            "security+", "cysa+", "casp+", "ceh", "cissp", "cism", "cisa", "crisc",
            "oscp", "ejpt", "pnpt", "gcih", "gcfa", "grem", "gicsp", "ccsp",
            "aws certified", "google cloud", "azure security", "sc-200", "sc-900",
            "network+", "a+", "linux+", "ccna", "btl1"
        ],
        "Operating Systems & Scripting": [
            "linux", "ubuntu", "kali", "debian", "red hat", "windows server", "active directory",
            "powershell", "python", "bash", "shell scripting", "sql", "git"
        ],
        "Networking & Protocols": [
            "tcp/ip", "dns", "dhcp", "wireshark", "pcap", "tcpdump", "firewall", "vpn",
            "routing", "subnetting", "proxy", "ids", "ips", "ssh", "ssl/tls"
        ],
        "Security Operations & SIEM/EDR": [
            "splunk", "sentinel", "qradar", "elastic", "crowdstrike", "sentinelone",
            "defender", "edr", "siem", "soc", "virustotal", "alienvault", "threat intelligence",
            "incident response", "threat hunting", "log analysis", "snort", "suricata", "zeek"
        ],
        "Offensive & Application Security": [
            "burp suite", "nmap", "metasploit", "owasp", "vulnerability scan", "nessus",
            "qualys", "penetration test", "hashcat", "sql injection", "xss", "gobuster", "amass"
        ],
        "Cloud & Infrastructure": [
            "aws", "azure", "gcp", "iam", "s3", "ec2", "terraform", "docker", "kubernetes",
            "guardduty", "cloudtrail", "cloudwatch", "cspm", "ci/cd", "devsecops"
        ],
        "Governance, Risk & Compliance": [
            "nist csf", "nist 800-53", "iso 27001", "soc 2", "hipaa", "pci-dss", "gdpr",
            "risk assessment", "vendor risk", "policy", "audit", "compliance", "fair"
        ]
    }

    # Extract detected competencies per category
    extracted_by_cat = {}
    total_detected_skills = 0
    for cat, skills in taxonomy.items():
        found = [s for s in skills if s in text_lower]
        if found:
            extracted_by_cat[cat] = found
            total_detected_skills += len(found)

    # Cross-reference with cumulative skills recorded in ACE memory from past conversations
    ace_documented = get_documented_candidate_skills(user_id) if user_id and user_id != "guest" else []
    forgotten_ace_skills = []
    for skill_rec in ace_documented:
        s_name = skill_rec.get("skill_name", "")
        if s_name and s_name.lower() not in text_lower:
            forgotten_ace_skills.append((s_name, skill_rec.get("context", ""), skill_rec.get("source", "conversation")))

    # Detect soft skills & metrics
    soft_keywords = ["led", "managed", "collaborated", "communicated", "trained", "mentored", "presented", "documented", "analyzed"]
    quantified_keywords = ["%", "$", "reduced", "improved", "increased", "saved", "decreased", "scaled"]
    education_keywords = ["bachelor", "master", "degree", "bs", "ms", "mba", "cybersecurity", "computer science", "information technology"]

    found_soft = [k for k in soft_keywords if k in text_lower]
    has_quantification = any(k in text_lower for k in quantified_keywords)
    has_education = any(k in text_lower for k in education_keywords)
    has_links = any(k in text_lower for k in ["linkedin", "github", "portfolio", "blog", "@"])

    # ── Scoring ───────────────────────────────────────────────────────────────
    score = 0
    has_certs = len(extracted_by_cat.get("Certifications", [])) > 0
    score += min(25, len(extracted_by_cat.get("Certifications", [])) * 10)
    score += min(30, total_detected_skills * 3)
    score += 15 if has_quantification else 0
    score += 10 if has_education else 0
    score += 10 if has_links else 0
    score += min(10, len(found_soft) * 2)

    score = min(100, max(15, score))
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D"

    # ── Role Expected Skills & Probing Questions ─────────────────────────────
    role_benchmarks = {
        "soc_analyst": {
            "critical": ["splunk", "wireshark", "active directory", "incident response", "security+"],
            "probing_questions": [
                ("wireshark", "Have you analyzed network packet captures (PCAPs) in Wireshark during labs or coursework? Adding this proves network analysis competency."),
                ("splunk", "Have you queried logs or built dashboards in Splunk, Elastic, or Sentinel (even in a home lab)? SOC managers look for specific SIEM tools."),
                ("powershell", "Do you have any experience with PowerShell or Python for automating repetitive tasks? Scripting sets entry-level SOC candidates apart."),
                ("nist csf", "Are you familiar with the NIST Incident Response lifecycle (PICERL) or MITRE ATT&CK? Mentioning these frameworks validates your analytical methodology.")
            ]
        },
        "penetration_tester": {
            "critical": ["nmap", "burp suite", "metasploit", "linux", "owasp"],
            "probing_questions": [
                ("burp suite", "Have you used Burp Suite for web vulnerability testing on PortSwigger Web Security Academy or TryHackMe? This is a core pentester tool."),
                ("nmap", "Have you performed network enumeration with Nmap and written custom scripts? Explicitly naming your recon tools is essential."),
                ("python", "Do you write or modify custom exploit scripts in Python or Bash? Scripting ability is a top differentiator for offensive roles."),
                ("github", "Do you have CTF writeups, lab reports, or tools published on GitHub? Linking your portfolio proves hands-on ability.")
            ]
        },
        "grc": {
            "critical": ["risk assessment", "nist csf", "iso 27001", "compliance", "policy"],
            "probing_questions": [
                ("nist csf", "Have you mapped security controls or performed gap assessments against NIST CSF, NIST SP 800-53, or ISO 27001? Recruiter filters specifically search for these standard names."),
                ("vendor risk", "Have you evaluated third-party vendor risks or reviewed security questionnaires (e.g., SIG, CAIQ)? Vendor risk management is in high demand."),
                ("soc 2", "Have you participated in audit preparation (SOC 2, HIPAA, or PCI-DSS)? Explicitly naming the audit standards significantly increases callback rates.")
            ]
        },
        "cloud_security": {
            "critical": ["aws", "terraform", "iam", "cloudtrail", "kubernetes"],
            "probing_questions": [
                ("terraform", "Have you defined cloud infrastructure or security policies using Infrastructure as Code (Terraform/CloudFormation)? IaC security is crucial."),
                ("iam", "Have you designed least-privilege IAM roles, SCPs, or bucket policies in AWS, Azure, or GCP? Identity is the cloud perimeter."),
                ("kubernetes", "Do you have experience with container security (Docker, Kubernetes, Trivy)? Containerization skills command premium salaries.")
            ]
        },
        "general": {
            "critical": ["security+", "wireshark", "linux", "active directory", "incident response"],
            "probing_questions": [
                ("wireshark", "Have you used network packet analysis tools like Wireshark or TCPDump?"),
                ("linux", "Do you have command-line experience in Linux (Ubuntu, Kali, CentOS)?"),
                ("splunk", "Have you set up a home lab with a free SIEM (Splunk/Security Onion) to analyze logs?"),
                ("github", "Do you have a GitHub repository documenting your home labs, CTF writeups, or projects?")
            ]
        }
    }

    target_key = target_role.lower().replace(" ", "_").replace("-", "_")
    benchmark = role_benchmarks.get(target_key, role_benchmarks["general"])

    # Collect probing questions for skills NOT found in resume
    probing_items = []
    for skill_key, probe_text in benchmark["probing_questions"]:
        if skill_key not in text_lower:
            probing_items.append(f"  ❓ **{skill_key.upper()}**: {probe_text}")

    # Build output sections
    extracted_lines = []
    for cat, items in extracted_by_cat.items():
        extracted_lines.append(f"- **{cat}**: {', '.join(items).title()}")
    extracted_str = "\n".join(extracted_lines) if extracted_lines else "- No cybersecurity-specific keywords detected yet."

    strengths = []
    if has_certs:
        strengths.append(f"Recognized certifications: {', '.join(extracted_by_cat['Certifications']).title()}")
    if total_detected_skills >= 5:
        strengths.append(f"Found {total_detected_skills} specific cybersecurity tools and technical keywords")
    if has_quantification:
        strengths.append("Includes quantified achievements with measurable metrics (%, $, scale)")
    if has_links:
        strengths.append("Professional profile links (LinkedIn/GitHub) present in header")

    strengths_str = "\n".join(f"  ✅ {s}" for s in strengths) if strengths else "  Baseline layout detected — needs cybersecurity keyword enrichment."

    # ACE Memory Discovered Skills Section
    ace_section = ""
    if forgotten_ace_skills:
        ace_items = []
        for s_name, ctx, src in forgotten_ace_skills[:5]:
            ace_items.append(f"  💡 **{s_name}** *(Discovered during {src.replace('_', ' ')})*: You previously demonstrated familiarity with this in conversation. Adding it to your resume bullet points will directly increase your hiring match score!")
        ace_section = f"""\n### 🧠 Skills Documented from Past Conversations (ACE Memory) Not on Your Resume
*I remembered the following skills you mentioned in earlier chats/exercises that are currently missing from your resume text:*

{chr(10).join(ace_items)}
\n---"""

    probing_str = "\n".join(probing_items[:4]) if probing_items else "  Your resume covers all standard benchmark keywords for this role!"

    return f"""## 📄 Resume & Competency Analysis — {target_role.replace('_', ' ').title()} Track

**ATS Readiness Score: {score}/100 (Grade: {grade})**

---

### 🔍 Extracted Skills & Detected Competencies
{extracted_str}
{ace_section}

---

### ✅ Core Strengths Identified
{strengths_str}

---

### ❓ High-Value Skills You Might Have Forgotten to List (Probing Discovery)
*Hiring teams specifically filter for the following competencies. If you have experience with any of these from home labs, coursework, or prior jobs, adding them will immediately boost your visibility:*

{probing_str}

---

### 🎯 High-Impact Action Items
1. **Incorporate Missing Probed Skills**: If you have used any of the tools above (even in TryHackMe or a home lab), add a dedicated **'Technical Skills & Labs'** section.
2. **Quantify Bullet Points**: Upgrade responsibilities into achievements (e.g., *"Analyzed 40+ daily SIEM alerts with Splunk, documenting root cause for 100% of escalations"*).
3. **Include Home Lab / GitHub Link**: If you don't have paid experience, a link to your documented lab projects serves as tangible proof of competence.

---
💬 *Reply with your answers to the probing questions above, or tell me which sections you would like me to rewrite or draft for you!*"""


def save_updated_resume(resume_markdown: str, user_id: str = "guest", target_role: str = "general", candidate_name: str = "Candidate") -> str:
    """Save the candidate's updated, rewritten, or newly drafted resume to their profile and enable one-click DOCX/PDF export.

    Call this tool whenever you draft, update, or rewrite the candidate's resume so that the document is
    persisted into their user profile and immediately made downloadable in Word (.docx) and PDF (.pdf) format on the web interface.

    Args:
        resume_markdown: The complete updated resume formatted in clean Markdown.
        user_id: The candidate's user ID or session identifier.
        target_role: The target cybersecurity track (e.g. 'ciso', 'soc_analyst', 'cloud_security', 'grc', 'general').
        candidate_name: The candidate's name (optional).

    Returns:
        Confirmation message with export details and next steps.
    """
    from api.routes.resume import save_user_resume_to_storage

    try:
        record = save_user_resume_to_storage(
            user_id=user_id,
            markdown_text=resume_markdown,
            target_role=target_role,
            candidate_name=candidate_name
        )
        return (
            f"✅ **Updated Resume Successfully Saved to User Profile!**\n\n"
            f"- **Target Track**: {target_role.replace('_', ' ').title()}\n"
            f"- **Timestamp**: {record.get('updated_at', 'Just now')}\n\n"
            f"📄 **Your resume is ready for 1-click export on the web interface:**\n"
            f"• Click **'Download DOCX'** for an ATS-optimized Microsoft Word version.\n"
            f"• Click **'Download PDF'** for a formatted PDF version.\n"
            f"• Access and edit it anytime from the **'My Resume & Exports'** studio in your sidebar.\n\n"
            f"```resume_export_ready\n{json.dumps({'user_id': user_id, 'target_role': target_role, 'saved': True})}\n```"
        )
    except Exception as e:
        return f"✅ **Updated Resume Generated:**\n\n{resume_markdown}\n\n*(Note: Could not automatically save to cloud storage: {e}, but you can copy/paste or export directly)*"


