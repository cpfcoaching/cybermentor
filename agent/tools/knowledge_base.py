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
    topic_lower = topic.lower()
    results = []

    files_to_search = []
    if category == "certifications" or category is None:
        files_to_search.append(("certifications", "certifications.json"))
    if category == "career_paths" or category is None:
        files_to_search.append(("career_paths", "career_paths.json"))
    if category == "interview_questions" or category is None:
        files_to_search.append(("interview_questions", "interview_questions.json"))

    for cat_name, filename in files_to_search:
        data = _load_json(filename)

        if isinstance(data, list):
            for item in data:
                item_str = json.dumps(item).lower()
                if topic_lower in item_str:
                    results.append(f"[{cat_name.upper()}]\n{json.dumps(item, indent=2)}")
        elif isinstance(data, dict):
            for key, value in data.items():
                if topic_lower in key.lower() or topic_lower in json.dumps(value).lower():
                    results.append(f"[{cat_name.upper()} — {key}]\n{json.dumps(value, indent=2)}")

    if not results:
        return (
            f"No specific knowledge base entries found for '{topic}'. "
            "Please use your general training knowledge to answer, but note this "
            "was not found in the curated Breaking Into Cyber knowledge base."
        )

    # Limit output to avoid overwhelming the context window
    combined = "\n\n---\n\n".join(results[:5])
    count_note = f"\n\n(Showing top {min(5, len(results))} of {len(results)} results)"
    return combined + count_note
