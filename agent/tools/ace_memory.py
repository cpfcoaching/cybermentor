"""
ACE (Autonomous Agent with Continual Evolution) Memory & Self-Optimization Module

Implements a cognitive memory layer for CyberMentor:
- Long-term Episodic & Semantic Memory Notes (`save_agent_note`)
- Comprehensive Context & Memory Retrieval (`get_agent_memory`)
- Continual Learning & Self-Optimization Loop (`optimize_coaching_strategy`)

Stores data persistently in Cloud Firestore (or local JSON fallback).
"""

import json
import os
import pathlib
from datetime import datetime, timezone
from typing import Optional

_ACE_STORAGE = pathlib.Path(__file__).parent.parent.parent / "sessions" / "ace_memory"


def _get_firestore_client():
    """Get Firestore client, returns None if not available."""
    try:
        from google.cloud import firestore
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            return None
        return firestore.Client(project=project)
    except Exception:
        return None


def _local_ace_path(user_id: str) -> pathlib.Path:
    """Get path for local ACE memory file."""
    safe_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
    return _ACE_STORAGE / f"{safe_id}_ace.json"


def save_agent_note(
    user_id: str,
    note_category: str,
    note_content: str,
    importance: int = 3
) -> str:
    """Take an explicit note into ACE agent memory about a user's background, preferences, or performance.

    MANDATORY ACE INSTRUCTION: You MUST use this tool to record key observations, user traits,
    learning habits, resume weaknesses, interview performance notes, or preferences whenever the user
    shares new context.

    Args:
        user_id: Unique identifier for the user.
        note_category: One of ['user_preference', 'skill_gap', 'learning_style', 'coaching_reflection', 'career_target'].
        note_content: Detailed observation or fact to store in long-term memory.
        importance: Rating from 1 (minor detail) to 5 (critical insight/goal).

    Returns:
        Confirmation of memory storage.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    note_entry = {
        "category": note_category,
        "content": note_content,
        "importance": max(1, min(5, importance)),
        "timestamp": timestamp,
    }

    # Try Firestore
    db = _get_firestore_client()
    if db:
        try:
            doc_ref = (
                db.collection("users")
                .document(user_id)
                .collection("ace_notes")
                .document()
            )
            doc_ref.set(note_entry)
            return f"🧠 [ACE Memory] Note saved under '{note_category}' (Importance: {importance}/5)."
        except Exception:
            pass

    # Local fallback
    _ACE_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _local_ace_path(user_id)
    memory_data = {"notes": [], "strategy_reflections": []}
    if path.exists():
        try:
            memory_data = json.loads(path.read_text())
        except Exception:
            pass

    memory_data.setdefault("notes", []).append(note_entry)
    path.write_text(json.dumps(memory_data, indent=2))
    return f"🧠 [ACE Memory] Note saved locally under '{note_category}' (Importance: {importance}/5)."


def optimize_coaching_strategy(
    user_id: str,
    strategy_reflection: str,
    proposed_adjustments: str
) -> str:
    """Execute a self-optimization loop step in the ACE Cognitive Engine.

    MANDATORY ACE INSTRUCTION: Use this tool to continuously learn and adapt your coaching approach
    for the user based on how they respond to study plans, interview feedback, or cert roadmaps.

    Args:
        user_id: Unique identifier for the user.
        strategy_reflection: Self-assessment of what coaching approach worked or failed in recent turns.
        proposed_adjustments: Explicit strategy changes you will adopt going forward for this user.

    Returns:
        Confirmation of strategy optimization update.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    reflection_entry = {
        "reflection": strategy_reflection,
        "adjustments": proposed_adjustments,
        "timestamp": timestamp,
    }

    # Try Firestore
    db = _get_firestore_client()
    if db:
        try:
            doc_ref = (
                db.collection("users")
                .document(user_id)
                .collection("ace_reflections")
                .document()
            )
            doc_ref.set(reflection_entry)
            return "⚡ [ACE Self-Optimization] Coaching strategy adapted & logged to cognitive memory."
        except Exception:
            pass

    # Local fallback
    _ACE_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _local_ace_path(user_id)
    memory_data = {"notes": [], "strategy_reflections": []}
    if path.exists():
        try:
            memory_data = json.loads(path.read_text())
        except Exception:
            pass

    memory_data.setdefault("strategy_reflections", []).append(reflection_entry)
    path.write_text(json.dumps(memory_data, indent=2))
    return "⚡ [ACE Self-Optimization] Coaching strategy adapted & logged locally to cognitive memory."


def get_agent_memory(user_id: str) -> str:
    """Retrieve full ACE cognitive memory (notes, user traits, self-optimization reflections, and history).

    Use this tool to inspect all long-term notes and strategy reflections for the user.

    Args:
        user_id: Unique identifier for the user.

    Returns:
        Formatted summary of long-term notes and coaching strategy adjustments.
    """
    notes = []
    reflections = []

    # Try Firestore
    db = _get_firestore_client()
    if db:
        try:
            note_docs = (
                db.collection("users")
                .document(user_id)
                .collection("ace_notes")
                .order_by("timestamp")
                .limit(20)
                .stream()
            )
            notes = [d.to_dict() for d in note_docs]

            refl_docs = (
                db.collection("users")
                .document(user_id)
                .collection("ace_reflections")
                .order_by("timestamp")
                .limit(10)
                .stream()
            )
            reflections = [d.to_dict() for d in refl_docs]
        except Exception:
            pass

    # Local fallback
    if not notes and not reflections:
        path = _local_ace_path(user_id)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                notes = data.get("notes", [])
                reflections = data.get("strategy_reflections", [])
            except Exception:
                pass

    if not notes and not reflections:
        return f"🧠 [ACE Memory for {user_id}]: Memory is empty. Take initial notes with `save_agent_note`."

    output_lines = [f"## 🧠 ACE Cognitive Memory & Reflection Log for {user_id}", ""]

    if notes:
        output_lines.append("### 📝 Stored Memory Notes:")
        for n in notes[-10:]:
            date = n.get("timestamp", "")[:10]
            cat = n.get("category", "general")
            imp = n.get("importance", 3)
            content = n.get("content", "")
            output_lines.append(f"  • [{date}] ({cat.upper()} | Imp: {imp}/5): {content}")
        output_lines.append("")

    if reflections:
        output_lines.append("### ⚡ Strategy Optimization History:")
        for r in reflections[-5:]:
            date = r.get("timestamp", "")[:10]
            refl = r.get("reflection", "")
            adj = r.get("adjustments", "")
            output_lines.append(f"  • [{date}] Reflection: {refl}")
            output_lines.append(f"    ↳ Strategy Shift: {adj}")
        output_lines.append("")

    output_lines.append("---")
    output_lines.append("*Utilize these memory notes and strategy shifts to deliver optimal, hyper-personalized coaching.*")

    return "\n".join(output_lines)
