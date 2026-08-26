"""CyberMentor agent tools — all custom capabilities registered here."""

# Core coaching tools
from agent.tools.knowledge_base import query_knowledge_base
from agent.tools.study_planner import generate_study_plan
from agent.tools.resume_analyzer import analyze_resume
from agent.tools.interview_coach import get_interview_question, evaluate_answer
from agent.tools.cert_advisor import recommend_certifications
from agent.tools.progress_tracker import save_user_progress, get_user_progress

# Bonus: Google AI model integrations
from agent.tools.veo_generator import generate_cert_explainer_video, generate_role_preview_video
from agent.tools.lyria_composer import generate_study_music, generate_cert_celebration_jingle
from agent.tools.gemma_analyzer import classify_user_intent, extract_resume_skills, score_skill_gap

__all__ = [
    # Core
    "query_knowledge_base",
    "generate_study_plan",
    "analyze_resume",
    "get_interview_question",
    "evaluate_answer",
    "recommend_certifications",
    "save_user_progress",
    "get_user_progress",
    # Veo (video generation)
    "generate_cert_explainer_video",
    "generate_role_preview_video",
    # Lyria (music generation)
    "generate_study_music",
    "generate_cert_celebration_jingle",
    # Gemma (fast analysis)
    "classify_user_intent",
    "extract_resume_skills",
    "score_skill_gap",
]
