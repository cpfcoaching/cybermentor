"""
CyberMentor Agent — Google Antigravity SDK

The core agent definition. Configures the CyberMentor agent with its
persona, all custom tools (including Veo, Lyria, and Gemma integrations),
and conversation persistence settings.
"""

import os
import pathlib
from google.antigravity import Agent, LocalAgentConfig

from agent.tools import (
    # Core coaching tools
    query_knowledge_base,
    get_cited_resources,
    generate_study_plan,
    analyze_resume,
    get_interview_question,
    evaluate_answer,
    recommend_certifications,
    save_user_progress,
    get_user_progress,
    # ACE Cognitive Memory & Continual Evolution Architecture
    save_agent_note,
    get_agent_memory,
    optimize_coaching_strategy,
    # Skills Mindmaps & Transferable Skills Matrix
    get_role_mindmap,
    explore_skill_transfer,
    # Veo — video generation
    generate_cert_explainer_video,
    generate_role_preview_video,
    # Lyria — music generation
    generate_study_music,
    generate_cert_celebration_jingle,
    # Gemma — fast classification & extraction
    classify_user_intent,
    extract_resume_skills,
    score_skill_gap,
)

# ── Persona ───────────────────────────────────────────────────────────────────
_PERSONA_PATH = pathlib.Path(__file__).parent / "persona.txt"

def _load_persona() -> str:
    try:
        return _PERSONA_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "You are CyberMentor, an AI career coach for cybersecurity professionals."


# ── All Registered Tools ──────────────────────────────────────────────────────
ALL_TOOLS = [
    # ── Core coaching ─────────────────────────────────────────────────────
    query_knowledge_base,
    get_cited_resources,             # List official citations and referenced resources
    generate_study_plan,
    analyze_resume,
    get_interview_question,
    evaluate_answer,
    recommend_certifications,
    save_user_progress,
    get_user_progress,
    # ── ACE Cognitive Memory & Continual Evolution ─────────────────────────
    save_agent_note,                 # Save structured long-term notes & candidate observations
    get_agent_memory,                # Retrieve candidate memory notes & strategy reflections
    optimize_coaching_strategy,      # Continuously adapt & optimize coaching strategy
    # ── Skills & Certifications Mindmaps & Skill Transfer ─────────────────
    get_role_mindmap,                # Role-specific skills and certification breakdown
    explore_skill_transfer,          # Cross-role transferable skills and intersection roadmap
    # ── Veo: video generation (Google AI bonus) ────────────────────────────
    generate_cert_explainer_video,   # "Show me what Security+ covers" → video
    generate_role_preview_video,     # "What does a SOC analyst do?" → video
    # ── Lyria: music generation (Google AI bonus) ──────────────────────────
    generate_study_music,            # "Play focus music for my study session"
    generate_cert_celebration_jingle,# "I passed my CISSP!" → celebration jingle
    # ── Gemma: fast analysis (Google AI bonus) ─────────────────────────────
    classify_user_intent,            # Rapid intent routing before tool dispatch
    extract_resume_skills,           # Fast structured extraction from resume text
    score_skill_gap,                 # Quick readiness scoring for target role
]


# ── Agent Factory ─────────────────────────────────────────────────────────────
def create_cybermentor_agent(
    save_dir: str | None = None,
    conversation_id: str | None = None,
) -> Agent:
    """
    Create and return a fully configured CyberMentor agent.

    The agent is equipped with:
    - Gemini 3.5 / 2.5 (via Antigravity SDK default or Vertex AI)
    - 15 custom tools across core coaching + Veo + Lyria + Gemma
    - Persistent conversation state via save_dir

    Args:
        save_dir: Directory for conversation history persistence.
        conversation_id: Resume an existing conversation by ID.

    Returns:
        A configured Google Antigravity Agent instance (use as async context manager).
    """
    if save_dir is None:
        save_dir = str(pathlib.Path(__file__).parent.parent / "sessions")
    os.makedirs(save_dir, exist_ok=True)

    config_kwargs: dict = dict(
        system_instructions=_load_persona(),
        tools=ALL_TOOLS,
        save_dir=save_dir,
    )

    api_key = os.getenv("GEMINI_API_KEY", "")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cybermentor-506813")

    if api_key and not "placeholder" in api_key.lower() and not "your_" in api_key.lower():
        config_kwargs["api_key"] = api_key
    else:
        config_kwargs["vertex"] = True
        config_kwargs["project"] = project_id
        config_kwargs["location"] = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        config_kwargs["model"] = "gemini-2.5-flash"

    if conversation_id:
        config_kwargs["conversation_id"] = conversation_id

    config = LocalAgentConfig(**config_kwargs)
    return Agent(config=config)
