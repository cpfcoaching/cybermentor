"""
Cloud Firestore Conversation Store

Saves and retrieves individual candidate conversation histories securely in
Cloud Firestore (`users/{user_id}/conversations/{session_id}/messages`).
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, List, Optional
from google.cloud import firestore

logger = logging.getLogger(__name__)

_DB: Optional[firestore.Client] = None


def get_firestore_client() -> Optional[firestore.Client]:
    """Get or initialize the Cloud Firestore client."""
    global _DB
    if _DB is not None:
        return _DB
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "cybermentor-506813")
        _DB = firestore.Client(project=project)
        return _DB
    except Exception as e:
        logger.warning(f"Could not connect to Firestore: {e}")
        return None


def save_conversation_message(
    user_id: str,
    session_id: str,
    role: str,
    content: str,
    user_email: Optional[str] = None,
) -> bool:
    """
    Save a single conversation message (user or model) into Cloud Firestore.
    Collection: users/{user_id}/conversations/{session_id}/messages
    """
    db = get_firestore_client()
    if not db or not user_id or not content:
        return False

    try:
        clean_user_id = user_id.replace("/", "_")
        clean_session_id = session_id.replace("/", "_") if session_id else "default_session"

        # Update conversation document metadata
        conv_ref = (
            db.collection("users")
            .document(clean_user_id)
            .collection("conversations")
            .document(clean_session_id)
        )
        conv_ref.set(
            {
                "updated_at": firestore.SERVER_TIMESTAMP,
                "session_id": clean_session_id,
                "user_id": clean_user_id,
                "user_email": user_email or "",
            },
            merge=True,
        )

        # Add message document
        msg_doc = {
            "role": role,  # "user" or "model"
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        conv_ref.collection("messages").add(msg_doc)
        logger.info(f"Saved message ({role}) for user {clean_user_id} in session {clean_session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save message to Firestore: {e}", exc_info=True)
        return False


def _clean_message_doc(doc_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert Firestore timestamp and datetime objects to JSON-serializable strings."""
    cleaned = {}
    for k, v in doc_dict.items():
        if hasattr(v, "isoformat"):
            cleaned[k] = v.isoformat()
        elif isinstance(v, (str, int, float, bool, list, dict)) or v is None:
            cleaned[k] = v
        else:
            cleaned[k] = str(v)
    return cleaned


def get_conversation_history(
    user_id: str, session_id: Optional[str] = None, limit: int = 50
) -> List[dict[str, Any]]:
    """
    Retrieve conversation history messages for a user from Cloud Firestore.
    """
    db = get_firestore_client()
    if not db or not user_id:
        return []

    try:
        clean_user_id = user_id.replace("/", "_")
        if session_id:
            clean_session_id = session_id.replace("/", "_")
            query = (
                db.collection("users")
                .document(clean_user_id)
                .collection("conversations")
                .document(clean_session_id)
                .collection("messages")
                .order_by("created_at", direction=firestore.Query.ASCENDING)
                .limit(limit)
            )
            docs = list(query.stream())
            if docs:
                return [_clean_message_doc(d.to_dict()) for d in docs]

        # Fallback to latest conversation for user
        convs = list(
            db.collection("users")
            .document(clean_user_id)
            .collection("conversations")
            .order_by("updated_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        for conv in convs:
            msg_docs = list(
                conv.reference.collection("messages")
                .order_by("created_at", direction=firestore.Query.ASCENDING)
                .limit(limit)
                .stream()
            )
            return [_clean_message_doc(m.to_dict()) for m in msg_docs]

        return []
    except Exception as e:
        logger.error(f"Failed to fetch conversation history from Firestore: {e}", exc_info=True)
        return []
