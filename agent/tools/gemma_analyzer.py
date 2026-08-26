"""
Gemma Fast Analyzer Tool (+0.2 bonus)

Uses Google Gemma (via Vertex AI Model Garden) as a lightweight, fast
model for specific classification and extraction tasks within CyberMentor.

Gemma handles quick, structured tasks that don't require Gemini's full
power — reducing latency and cost for high-frequency classification calls:

1. Intent classification — route user messages before invoking expensive tools
2. Resume keyword extraction — fast structured extraction from resume text
3. Skill gap scoring — quick scoring of skill coverage for a target role

Requires: google-genai >= 0.8.0, GOOGLE_CLOUD_PROJECT env var,
          Gemma model access via Vertex AI Model Garden
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Gemma model to use (via Vertex AI Model Garden)
GEMMA_MODEL = "gemma-3-27b-it"


def _get_gemma_client():
    """Build a Vertex AI GenAI client targeting Gemma."""
    try:
        from google import genai
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project:
            return None
        return genai.Client(vertexai=True, project=project, location=location)
    except ImportError:
        logger.warning("google-genai not installed. Gemma integration unavailable.")
        return None
    except Exception as e:
        logger.warning(f"Gemma client init failed: {e}")
        return None


def _gemma_generate(prompt: str, max_tokens: int = 512) -> Optional[str]:
    """Run a prompt through Gemma and return the text response."""
    client = _get_gemma_client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(
            model=GEMMA_MODEL,
            contents=prompt,
            config={"max_output_tokens": max_tokens, "temperature": 0.1},
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemma inference error: {e}")
        return None


def classify_user_intent(message: str) -> str:
    """Rapidly classify a user's message intent using Gemma for fast routing.

    Use this tool FIRST when you receive an ambiguous user message to quickly
    determine which primary tool to invoke next. Gemma is faster than Gemini
    for this single-purpose classification task.

    Args:
        message: The user's raw message text to classify.

    Returns:
        A JSON string with the classified intent and confidence.
        Intent labels: "career_advice", "cert_recommendation", "study_plan",
        "resume_review", "interview_prep", "progress_check", "general_chat".
    """
    prompt = f"""You are an intent classifier for a cybersecurity career coaching app.
Classify the following user message into exactly ONE intent category.

Categories:
- career_advice: User wants guidance on career paths, roles, or the industry
- cert_recommendation: User wants to know which certifications to pursue
- study_plan: User wants a study schedule or learning plan for a specific cert
- resume_review: User wants feedback on their resume or work experience
- interview_prep: User wants to practice interview questions or get feedback on answers
- progress_check: User is sharing an achievement or asking about their progress
- general_chat: None of the above

User message: "{message}"

Respond with ONLY valid JSON in this exact format:
{{"intent": "<category>", "confidence": <0.0-1.0>, "key_entities": ["<entity1>", "<entity2>"]}}"""

    result = _gemma_generate(prompt, max_tokens=128)

    if result is None:
        # Fallback: simple keyword matching
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["resume", "cv", "experience", "background"]):
            intent = "resume_review"
        elif any(w in msg_lower for w in ["study", "plan", "schedule", "hours", "week"]):
            intent = "study_plan"
        elif any(w in msg_lower for w in ["cert", "certification", "comptia", "cissp", "oscp"]):
            intent = "cert_recommendation"
        elif any(w in msg_lower for w in ["interview", "question", "answer", "practice"]):
            intent = "interview_prep"
        elif any(w in msg_lower for w in ["career", "role", "job", "path", "soc", "analyst"]):
            intent = "career_advice"
        elif any(w in msg_lower for w in ["passed", "got", "earned", "completed", "finished"]):
            intent = "progress_check"
        else:
            intent = "general_chat"
        return json.dumps({"intent": intent, "confidence": 0.7, "key_entities": [], "source": "fallback"})

    # Try to parse Gemma's JSON response
    try:
        # Strip any markdown code fences Gemma might add
        clean = result.strip().strip("```json").strip("```").strip()
        parsed = json.loads(clean)
        parsed["source"] = "gemma"
        return json.dumps(parsed)
    except json.JSONDecodeError:
        return json.dumps({
            "intent": "general_chat",
            "confidence": 0.5,
            "key_entities": [],
            "source": "gemma_parse_error",
        })


def extract_resume_skills(resume_text: str) -> str:
    """Use Gemma to rapidly extract structured skill data from a resume.

    Use this tool BEFORE analyze_resume() to quickly pull structured
    data from raw resume text. Gemma handles this extraction faster
    than Gemini, and the structured output feeds into deeper analysis.

    Args:
        resume_text: The plain text content of the user's resume.

    Returns:
        A JSON string containing extracted skills, certs, tools, and
        years of experience — structured for downstream analysis.
    """
    # Truncate to avoid token limits
    truncated = resume_text[:3000]

    prompt = f"""Extract structured information from this resume text for a cybersecurity job analysis.

Resume text:
---
{truncated}
---

Extract and return ONLY valid JSON in this exact structure:
{{
  "certifications": ["list of certifications found"],
  "security_tools": ["list of security tools/platforms mentioned"],
  "programming_languages": ["list of languages/scripting"],
  "years_of_experience": <integer or null>,
  "current_role": "<job title or null>",
  "education": "<highest degree or null>",
  "linkedin_present": <true/false>,
  "github_present": <true/false>,
  "quantified_achievements": <true/false>,
  "job_titles": ["list of job titles found in work history"]
}}

Return ONLY the JSON object, no explanation."""

    result = _gemma_generate(prompt, max_tokens=512)

    if result is None:
        return json.dumps({
            "certifications": [],
            "security_tools": [],
            "programming_languages": [],
            "years_of_experience": None,
            "current_role": None,
            "education": None,
            "linkedin_present": False,
            "github_present": False,
            "quantified_achievements": False,
            "job_titles": [],
            "source": "fallback",
        })

    try:
        clean = result.strip().strip("```json").strip("```").strip()
        parsed = json.loads(clean)
        parsed["source"] = "gemma"
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"raw_gemma_output": result[:500], "source": "gemma_parse_error"})


def score_skill_gap(
    user_skills: list[str],
    target_role: str,
) -> str:
    """Use Gemma to score a candidate's skill gap for a specific cybersecurity role.

    Use this tool to quickly assess how close a user is to being job-ready
    for their target role, based on the skills they've listed.

    Args:
        user_skills: List of skills, tools, and certifications the user has.
                     Example: ["Security+", "Splunk", "Python", "Linux"]
        target_role: The role to evaluate readiness for.
                     Example: "SOC Analyst", "Penetration Tester", "GRC Analyst"

    Returns:
        A JSON string with a readiness score (0-100), identified strengths,
        critical gaps, and a time-to-ready estimate.
    """
    skills_str = ", ".join(user_skills) if user_skills else "No skills listed"

    prompt = f"""You are a cybersecurity hiring manager evaluating a candidate's readiness.

Candidate skills: {skills_str}
Target role: {target_role}

Rate this candidate's readiness for the {target_role} role and identify gaps.
Return ONLY valid JSON:
{{
  "readiness_score": <0-100>,
  "readiness_label": "<Not Ready | Getting There | Almost Ready | Job Ready>",
  "top_strengths": ["skill1", "skill2"],
  "critical_gaps": ["gap1", "gap2", "gap3"],
  "estimated_months_to_ready": <integer>,
  "next_priority_skill": "<single most important skill to add now>"
}}

Return ONLY the JSON object."""

    result = _gemma_generate(prompt, max_tokens=400)

    if result is None:
        return json.dumps({
            "readiness_score": 50,
            "readiness_label": "Getting There",
            "top_strengths": user_skills[:2] if user_skills else [],
            "critical_gaps": ["Assessment unavailable — Gemma client not configured"],
            "estimated_months_to_ready": 6,
            "next_priority_skill": "Security+",
            "source": "fallback",
        })

    try:
        clean = result.strip().strip("```json").strip("```").strip()
        parsed = json.loads(clean)
        parsed["source"] = "gemma"
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"raw_output": result[:300], "source": "gemma_parse_error"})
