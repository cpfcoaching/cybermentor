"""
Firestore Client

Thin wrapper around Google Cloud Firestore for managing user profiles,
session history, and progress milestones.
"""

import os
from datetime import datetime, timezone
from typing import Optional

from google.cloud import firestore


class FirestoreClient:
    """Manages all CyberMentor data in Firestore."""

    def __init__(self):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        database = os.getenv("FIRESTORE_DATABASE", "(default)")
        self.db = firestore.Client(project=project, database=database)

    # ── User Profile ──────────────────────────────────────────────────────────

    def get_user_profile(self, user_id: str) -> Optional[dict]:
        """Fetch a user's profile document."""
        doc = self.db.collection("users").document(user_id).get()
        return doc.to_dict() if doc.exists else None

    def upsert_user_profile(self, user_id: str, profile_data: dict) -> None:
        """Create or update a user's profile."""
        profile_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.db.collection("users").document(user_id).set(profile_data, merge=True)

    # ── Session Messages ──────────────────────────────────────────────────────

    def save_message(self, session_id: str, role: str, content: str) -> str:
        """Append a message to a session's message history."""
        doc_ref = (
            self.db.collection("sessions")
            .document(session_id)
            .collection("messages")
            .document()
        )
        doc_ref.set({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return doc_ref.id

    def get_session_messages(self, session_id: str, limit: int = 50) -> list[dict]:
        """Retrieve recent messages for a session."""
        docs = (
            self.db.collection("sessions")
            .document(session_id)
            .collection("messages")
            .order_by("timestamp")
            .limit_to_last(limit)
            .stream()
        )
        return [doc.to_dict() for doc in docs]

    # ── Progress Milestones ───────────────────────────────────────────────────

    def save_milestone(self, user_id: str, milestone: str, notes: str = "") -> str:
        """Save a progress milestone for a user."""
        doc_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("progress")
            .document()
        )
        doc_ref.set({
            "milestone": milestone,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return doc_ref.id

    def get_milestones(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get a user's progress milestones in chronological order."""
        docs = (
            self.db.collection("users")
            .document(user_id)
            .collection("progress")
            .order_by("timestamp")
            .limit_to_last(limit)
            .stream()
        )
        return [doc.to_dict() for doc in docs]
