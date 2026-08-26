"""
CyberMentor Agent — Google Antigravity SDK

The core agent definition. This module creates and configures the CyberMentor
agent with its persona, tools, and persistence settings.
"""

import os
import pathlib
from google.antigravity import Agent, LocalAgentConfig

from agent.tools import (
    query_knowledge_base,
    generate_study_plan,
    analyze_resume,
    get_interview_question,
    evaluate_answer,
    recommend_certifications,
    save_user_progress,
    get_user_progress,
)

# ── Persona ──────────────────────────────────────────────────────────────────
_PERSONA_PATH = pathlib.Path(__file__).parent / "persona.txt"

def _load_persona() -> str:
    """Load the system instructions from the persona file."""
    try:
        return _PERSONA_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "You are CyberMentor, an AI career coach for cybersecurity professionals."


# ── Agent Factory ─────────────────────────────────────────────────────────────

def create_cybermentor_agent(
    save_dir: str | None = None,
    conversation_id: str | None = None,
) -> Agent:
    """
    Create and return a configured CyberMentor agent.

    Args:
        save_dir: Directory where conversation history is persisted.
                  Defaults to a 'sessions' folder in the project root.
        conversation_id: If provided, resumes an existing conversation.

    Returns:
        A configured Google Antigravity Agent instance.
    """
    # Default save directory for conversation persistence
    if save_dir is None:
        save_dir = str(pathlib.Path(__file__).parent.parent / "sessions")
    os.makedirs(save_dir, exist_ok=True)

    config_kwargs = dict(
        system_instructions=_load_persona(),
        tools=[
            query_knowledge_base,
            generate_study_plan,
            analyze_resume,
            get_interview_question,
            evaluate_answer,
            recommend_certifications,
            save_user_progress,
            get_user_progress,
        ],
        save_dir=save_dir,
    )

    # Resume existing conversation if ID provided
    if conversation_id:
        config_kwargs["conversation_id"] = conversation_id

    config = LocalAgentConfig(**config_kwargs)
    return Agent(config=config)
