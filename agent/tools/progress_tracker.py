"""
Progress Tracker Tool

Reads and writes user progress data to/from Firestore.
Falls back gracefully to local JSON storage if Firestore is unavailable.
"""

import json
import os
import pathlib
from datetime import datetime, timezone
from typing import Optional

from agent.tools.conversation_store import save_conversation_message

_LOCAL_STORAGE = pathlib.Path(__file__).parent.parent.parent / "sessions" / "progress"


def _get_firestore_client():
    """Get Firestore client, returns None if not configured."""
    try:
        from google.cloud import firestore
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            return None
        return firestore.Client(project=project)
    except Exception:
        return None


def _local_path(user_id: str) -> pathlib.Path:
    """Get local storage path for a user."""
    safe_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
    return _LOCAL_STORAGE / f"{safe_id}.json"


def save_user_progress(user_id: str, milestone: str, notes: str = "") -> str:
    """Save a user's progress milestone to persistent storage (Firestore or local).

    Use this tool when the user:
    - Completes a study session or milestone
    - Passes an exam or earns a certification
    - Sets a new career goal
    - Shares significant progress ("I just finished the Security+ objectives!")

    Args:
        user_id: The unique identifier for this user (their session username).
        milestone: A short description of what was accomplished.
                   Examples: "Completed Security+ study plan week 1",
                   "Passed CISSP exam", "Set goal: SOC Analyst at a healthcare company".
        notes: Optional additional context or details about this milestone.

    Returns:
        A confirmation message.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = {
        "milestone": milestone,
        "notes": notes,
        "timestamp": timestamp,
    }

    # Try Firestore first
    db = _get_firestore_client()
    if db:
        try:
            doc_ref = db.collection("users").document(user_id).collection("progress").document()
            doc_ref.set(entry)
            return f"✅ Progress saved to Firestore: **{milestone}** ({timestamp[:10]})"
        except Exception as e:
            pass  # Fall through to local storage

    # Fallback: local JSON storage
    _LOCAL_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _local_path(user_id)

    existing = []
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            existing = []

    existing.append(entry)
    path.write_text(json.dumps(existing, indent=2))
    return f"✅ Progress saved locally: **{milestone}** ({timestamp[:10]})"


def get_user_progress(user_id: str) -> str:
    """Retrieve a user's progress history to personalize coaching.

    Use this tool at the START of every conversation to load the user's
    context. Also use it when the user asks "where did we leave off?"
    or "what have I accomplished so far?"

    Args:
        user_id: The unique identifier for this user.

    Returns:
        A formatted summary of the user's progress history, or a message
        indicating this is a new user with no history.
    """
    milestones = []

    # Try Firestore first
    db = _get_firestore_client()
    if db:
        try:
            docs = (
                db.collection("users")
                .document(user_id)
                .collection("progress")
                .order_by("timestamp")
                .limit(20)
                .stream()
            )
            milestones = [doc.to_dict() for doc in docs]
        except Exception:
            pass

    # Fallback: local storage
    if not milestones:
        path = _local_path(user_id)
        if path.exists():
            try:
                milestones = json.loads(path.read_text())
            except Exception:
                milestones = []

    if not milestones:
        return (
            f"No previous progress found for user '{user_id}'. "
            "This appears to be a new user — welcome them and ask about their "
            "background, experience level, and career goals to get started."
        )

    entries = []
    for m in milestones[-10:]:  # Show last 10
        date = m.get("timestamp", "")[:10]
        milestone = m.get("milestone", "")
        notes = m.get("notes", "")
        line = f"  • [{date}] {milestone}"
        if notes:
            line += f"\n    → {notes}"
        entries.append(line)

    return f"""## 📚 Progress History for {user_id}

**{len(milestones)} milestone(s) recorded**

### Recent Milestones (last 10)
{chr(10).join(entries)}

---
*Use this context to personalize your coaching responses.*"""
