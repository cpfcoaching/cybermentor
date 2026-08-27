"""
Knowledge Base Tool

Searches the curated CyberMentor knowledge base (certifications, career paths,
interview questions) and returns relevant content for the agent to use.
"""

import json
import pathlib
from typing import Optional

_DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data" / "knowledge"


def _load_json(filename: str) -> dict | list:
    """Load a JSON knowledge file."""
    path = _DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def query_knowledge_base(topic: str, category: Optional[str] = None) -> str:
    """Search the CyberMentor knowledge base for information on a cybersecurity topic.

    Use this tool when the user asks about certifications, career paths,
    specific cybersecurity roles, study resources, or interview questions.

    Args:
        topic: The topic to search for. Examples: "Security+", "SOC Analyst",
               "penetration testing", "CISSP requirements", "behavioral interview".
        category: Optional category filter. One of: "certifications",
                  "career_paths", "interview_questions". Leave blank to search all.

    Returns:
        A formatted string with relevant knowledge base content, or a message
        indicating no results were found.
    """
    topic_lower = topic.lower().strip()
    search_tokens = [t for t in topic_lower.split() if len(t) > 2]
    scored_results = []

    files_to_search = []
    if category in ("certifications", None):
        files_to_search.append(("certifications", "certifications.json"))
    if category in ("career_paths", None):
        files_to_search.append(("career_paths", "career_paths.json"))
    if category in ("interview_questions", None):
        files_to_search.append(("interview_questions", "interview_questions.json"))
    if category in ("youtube_transcripts", None):
        files_to_search.append(("breaking_into_cyber_episodes", "youtube_transcripts.json"))

    for cat_name, filename in files_to_search:
        data = _load_json(filename)

        if isinstance(data, list):
            for item in data:
                item_str = json.dumps(item).lower()
                score = 0
                if topic_lower in item_str:
                    score += 10
                for token in search_tokens:
                    if token in item_str:
                        score += 2
                if score > 0:
                    scored_results.append((score, f"[{cat_name.upper()}]\n{json.dumps(item, indent=2)}"))
        elif isinstance(data, dict):
            for key, value in data.items():
                val_str = json.dumps(value).lower()
                score = 0
                if topic_lower in key.lower() or topic_lower in val_str:
                    score += 10
                for token in search_tokens:
                    if token in key.lower() or token in val_str:
                        score += 2
                if score > 0:
                    scored_results.append((score, f"[{cat_name.upper()} — {key}]\n{json.dumps(value, indent=2)}"))

    if not scored_results:
        return (
            f"No specific knowledge base entries found for '{topic}'. "
            "Please use your general training knowledge to answer, but note this "
            "was not found in the curated Breaking Into Cyber knowledge base."
        )

    # Sort by relevance score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = [r[1] for r in scored_results[:5]]

    combined = "\n\n---\n\n".join(top_results)
    count_note = f"\n\n(Showing top {min(5, len(scored_results))} of {len(scored_results)} relevant results)"
    return combined + count_note


def get_cited_resources() -> str:
    """Return the official list of cited and referenced resources used by CyberMentor.

    Use this tool when the user asks for citations, references, sources, or official links used.
    """
    return """## 📚 Official Resources & Citations

1. **Breaking Into Cybersecurity**: [https://breakingintocybersecurity.org](https://breakingintocybersecurity.org) & YouTube [https://www.youtube.com/c/BreakingIntoCybersecurity](https://www.youtube.com/c/BreakingIntoCybersecurity)
   - Primary sponsor, community, video/audio content, and career development platform for cybersecurity candidates.

2. **CISA NICCS Cyber Career Pathways Tool**: [https://niccs.cisa.gov/tools/cyber-career-pathways-tool](https://niccs.cisa.gov/tools/cyber-career-pathways-tool)
   - Interactive CISA workforce pathway tool for exploring core cyber work roles, knowledge, skills, and abilities (KSAs).

3. **NIST NICE Cybersecurity Workforce Framework (SP 800-181r1)**: [https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions)
   - National standard establishing common taxonomy for cybersecurity work roles, tasks, knowledge, and skills.

4. **Paul Jerimy Security Certification Roadmap**: [https://pauljerimy.com/security-certification-roadmap/](https://pauljerimy.com/security-certification-roadmap/)
   - Open-Source GitHub Repository: [https://github.com/PaulJerimy/SecCertRoadmapHTML](https://github.com/PaulJerimy/SecCertRoadmapHTML)
   - Industry-standard progression matrix mapping 300+ cybersecurity certifications across 10 security domains and 6 experience tiers.

5. **Hadess Cybersecurity Certification Roadmap**: [https://career.hadess.io/certificate-roadmap](https://career.hadess.io/certificate-roadmap)
   - Interactive certification matrix, prerequisites, exam costs, and career path mappings.

6. **Cyberdudekz Security Cert Roadmap**: [https://github.com/cyberdudekz/security-cert-roadmap](https://github.com/cyberdudekz/security-cert-roadmap)
   - Community-curated visual roadmap of security certifications categorized by specialization and difficulty.

7. **Coursera Cybersecurity Interview Prep Guide**: [https://www.coursera.org/resources/cybersecurity-interview-prep-guide](https://www.coursera.org/resources/cybersecurity-interview-prep-guide)
   - Comprehensive technical, situational, and behavioral interview preparation frameworks.

8. **Bauer College 61 Cybersecurity Interview Questions & Answers**: [https://careercenter.bauer.uh.edu/blog/2021/06/17/61-cybersecurity-job-interview-questions-and-answers/](https://careercenter.bauer.uh.edu/blog/2021/06/17/61-cybersecurity-job-interview-questions-and-answers/)
   - Industry-calibrated question bank and answers across networking, cryptography, and incident response.

9. **H2K Infosys Cybersecurity Interview & Career Guide**: [https://www.h2kinfosys.com/blog/most-common-cyber-security-interview-questions-and-answers-for-career-growth/](https://www.h2kinfosys.com/blog/most-common-cyber-security-interview-questions-and-answers-for-career-growth/)
   - Common cybersecurity interview scenarios, protocols, and technical defense rubrics.

10. **Insight Global Best Cybersecurity Interview Questions**: [https://insightglobal.com/blog/best-cybersecurity-interview-questions/](https://insightglobal.com/blog/best-cybersecurity-interview-questions/)
    - Key recruiter insights, hiring manager expectations, and behavioral evaluation standards.

11. **ACE (Autonomous Agent with Continual Evolution) Framework**: [https://github.com/ace-agent/ace](https://github.com/ace-agent/ace)
    - Cognitive memory, candidate observation logging, and continual self-optimization strategy framework for AI agents.

12. **NIST AI Risk Management Framework (AI RMF 1.0)**: [https://www.nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework)
    - Enterprise standards for artificial intelligence security, trust, and risk governance.

13. **OWASP Top 10 for Large Language Model Applications**: [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
    - Industry benchmark reference for identifying and mitigating security vulnerabilities in Generative AI and LLM architectures.

14. **OWASP LLM01: Prompt Injection Guide**: [https://genai.owasp.org/llmrisk/llm01-prompt-injection/](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
    - Direct and indirect prompt injection threat vectors, delimiter protections, and defensive mitigation frameworks.

15. **OWASP GenAI Security Checklist & Guide**: [https://genai.owasp.org/download/44348/?tmstv=1734330814](https://genai.owasp.org/download/44348/?tmstv=1734330814)
    - Comprehensive governance, security audit checklist, and operational readiness guide for Generative AI applications."""


