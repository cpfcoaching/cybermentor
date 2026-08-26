"""
Interview Coach Tool

Provides role-specific interview questions and evaluates user answers
with rubric-based scoring and improvement suggestions.
"""

import json
import pathlib
import random

_DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data" / "knowledge"

# Built-in question bank (supplemented by knowledge base JSON)
_QUESTIONS = {
    "soc_analyst": {
        "technical": [
            {"q": "What is the difference between IDS and IPS?", "key_points": ["IDS detects only", "IPS can block/prevent", "inline vs passive", "signature-based vs behavioral"]},
            {"q": "Walk me through how you would investigate a phishing alert.", "key_points": ["triage severity", "check email headers", "analyze links/attachments safely", "check for credential theft", "contain and remediate"]},
            {"q": "What is a SIEM and how do you use it?", "key_points": ["aggregates logs", "correlation rules", "alerting", "specific product experience", "tuning to reduce false positives"]},
            {"q": "Explain the difference between a false positive and a false negative in security monitoring.", "key_points": ["false positive: alert with no real threat", "false negative: missed real threat", "impact of each", "how to tune to reduce them"]},
            {"q": "What are the phases of incident response?", "key_points": ["Preparation", "Identification", "Containment", "Eradication", "Recovery", "Lessons Learned", "PICERL mnemonic"]},
        ],
        "behavioral": [
            {"q": "Tell me about a time you had to escalate a security incident. How did you decide when to escalate?", "key_points": ["specific example", "criteria for escalation", "communication", "outcome"]},
            {"q": "How do you stay current with cybersecurity threats and news?", "key_points": ["specific sources named", "routine/habit", "applying learning to work"]},
        ],
    },
    "penetration_tester": {
        "technical": [
            {"q": "Describe the penetration testing methodology you follow.", "key_points": ["Reconnaissance", "Scanning", "Exploitation", "Post-exploitation", "Reporting", "rules of engagement"]},
            {"q": "What is the difference between a vulnerability scan and a penetration test?", "key_points": ["vuln scan is automated/surface", "pen test is manual/deeper", "scope", "deliverables"]},
            {"q": "You find a critical SQL injection vulnerability. What do you do next?", "key_points": ["document carefully", "assess impact", "don't go out of scope", "report immediately if critical", "propose remediation"]},
            {"q": "What tools do you use for network reconnaissance?", "key_points": ["Nmap", "Masscan", "Shodan", "purpose of each", "passive vs active recon"]},
        ],
        "behavioral": [
            {"q": "Describe a time when a penetration test didn't go as planned. How did you adapt?", "key_points": ["specific situation", "problem-solving", "communication with client", "outcome"]},
        ],
    },
    "grc": {
        "technical": [
            {"q": "What is the difference between a risk assessment and a risk analysis?", "key_points": ["assessment is broader process", "analysis is the calculation part", "qualitative vs quantitative"]},
            {"q": "Walk me through implementing an ISO 27001 program from scratch.", "key_points": ["gap assessment", "define scope", "risk treatment", "policies and controls", "audit", "certification"]},
            {"q": "What is the CIA triad and why does it matter in GRC?", "key_points": ["Confidentiality", "Integrity", "Availability", "how controls map to each", "risk decisions"]},
        ],
        "behavioral": [
            {"q": "How would you explain a complex security risk to a non-technical executive?", "key_points": ["business language", "financial impact", "simple analogy", "recommendation"]},
        ],
    },
    "general": {
        "behavioral": [
            {"q": "Why do you want to work in cybersecurity?", "key_points": ["genuine motivation", "specific interest area", "career trajectory"]},
            {"q": "Where do you see yourself in 3-5 years in cybersecurity?", "key_points": ["specific role target", "realistic timeline", "steps being taken"]},
            {"q": "Tell me about a technical project or lab you've done recently.", "key_points": ["specific project", "tools used", "what you learned", "challenges overcome"]},
        ],
    },
}


def get_interview_question(role: str, difficulty: str = "mixed", question_type: str = "mixed") -> str:
    """Retrieve a cybersecurity interview question for practice.

    Use this tool when the user wants to practice interview questions,
    asks to be quizzed, or wants to do a mock interview session.

    Args:
        role: The cybersecurity role to get questions for. One of:
              "soc_analyst", "penetration_tester", "grc", "general".
              Use "general" if the role is unclear.
        difficulty: Question difficulty level. One of: "beginner", "intermediate",
                    "advanced", "mixed". Use "mixed" for a varied experience.
        question_type: Type of question. One of: "technical", "behavioral", "mixed".

    Returns:
        A formatted interview question ready for the user to answer.
    """
    role_key = role.lower().replace(" ", "_").replace("-", "_")
    questions_pool = _QUESTIONS.get(role_key, _QUESTIONS["general"])

    available = []
    if question_type in ("technical", "mixed") and "technical" in questions_pool:
        available.extend([(q, "technical") for q in questions_pool["technical"]])
    if question_type in ("behavioral", "mixed") and "behavioral" in questions_pool:
        available.extend([(q, "behavioral") for q in questions_pool["behavioral"]])

    if not available:
        available = [(q, "behavioral") for q in _QUESTIONS["general"]["behavioral"]]

    selected, q_type = random.choice(available)

    return f"""## 🎤 Interview Question — {role.replace('_', ' ').title()}

**Type:** {q_type.title()}

---

> **"{selected['q']}"**

---

Take your time to formulate a complete answer, then share it with me and I'll give you scored feedback.

*Tip: For behavioral questions, use the STAR method (Situation, Task, Action, Result).*"""


def evaluate_answer(question: str, user_answer: str, role: str = "general") -> str:
    """Evaluate a user's interview answer with rubric-based scoring and coaching feedback.

    Use this tool immediately after the user provides their answer to an interview question.
    This tool analyzes the answer quality and returns actionable improvement suggestions.

    Args:
        question: The interview question that was asked (copy exactly).
        user_answer: The user's answer to evaluate (their exact response).
        role: The role context for this question. Helps calibrate expectations.

    Returns:
        A structured evaluation with a score out of 10, strengths, gaps, and
        a model answer template to learn from.
    """
    # Find matching question and key points from the bank
    role_key = role.lower().replace(" ", "_").replace("-", "_")
    questions_pool = _QUESTIONS.get(role_key, _QUESTIONS["general"])

    key_points = []
    for q_type_list in questions_pool.values():
        for q_data in q_type_list:
            if q_data["q"].lower() in question.lower() or question.lower() in q_data["q"].lower():
                key_points = q_data.get("key_points", [])
                break

    # Score based on key point coverage
    answer_lower = user_answer.lower()
    covered = [kp for kp in key_points if any(word in answer_lower for word in kp.lower().split()[:2])]
    missed = [kp for kp in key_points if kp not in covered]

    if key_points:
        coverage_score = len(covered) / len(key_points)
    else:
        coverage_score = 0.7  # Default if we can't evaluate specific key points

    # Length/completeness score
    word_count = len(user_answer.split())
    if word_count < 20:
        length_score = 0.3
    elif word_count < 50:
        length_score = 0.6
    elif word_count < 200:
        length_score = 1.0
    else:
        length_score = 0.9  # Slightly penalize rambling

    final_score = round((coverage_score * 0.6 + length_score * 0.4) * 10, 1)
    final_score = min(10.0, max(1.0, final_score))

    covered_str = "\n".join(f"  ✅ {kp}" for kp in covered) if covered else "  (None detected)"
    missed_str = "\n".join(f"  ❌ {kp}" for kp in missed) if missed else "  None — great coverage!"

    return f"""## 📊 Answer Evaluation

**Score: {final_score}/10**

---

### ✅ What You Covered Well
{covered_str}

### 🔧 Gaps to Address
{missed_str}

### 💬 Coaching Notes
{"Great answer! You covered the key concepts well. " if final_score >= 8 else ""}{"Consider making your answer more concise — aim for 3-4 clear sentences. " if word_count > 200 else ""}{"Your answer was a bit brief. Try to elaborate with specific examples. " if word_count < 50 else ""}

### 🎯 What a Strong Answer Looks Like
A strong answer to this question would:
{chr(10).join(f'- Mention {kp}' for kp in (key_points or ["Specific examples from experience", "Clear reasoning", "Structured format"]))}

---
*Want to try another question, or should I rephrase this one?*"""
