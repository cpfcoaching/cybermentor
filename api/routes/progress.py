"""
Progress Route

Endpoints for reading and writing user career progress milestones.
"""

import os
import json
import pathlib
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from api.models import MilestoneRequest, MilestoneItem, ProgressResponse

router = APIRouter(prefix="/api/progress", tags=["progress"])

_LOCAL_STORAGE = pathlib.Path(__file__).parent.parent.parent / "sessions" / "progress"


def _get_firestore():
    """Try to get a Firestore client, return None if unavailable."""
    try:
        from google.cloud import firestore
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            return None
        return firestore.Client(project=project)
    except Exception:
        return None


def _local_path(user_id: str) -> pathlib.Path:
    safe = "".join(c for c in user_id if c.isalnum() or c in "-_")
    return _LOCAL_STORAGE / f"{safe}.json"


@router.get("/{user_id}", response_model=ProgressResponse)
async def get_progress(user_id: str):
    """Get all progress milestones for a user."""
    milestones = []

    db = _get_firestore()
    if db:
        try:
            docs = (
                db.collection("users")
                .document(user_id)
                .collection("progress")
                .order_by("timestamp")
                .stream()
            )
            milestones = [doc.to_dict() for doc in docs]
        except Exception:
            pass

    if not milestones:
        path = _local_path(user_id)
        if path.exists():
            try:
                milestones = json.loads(path.read_text())
            except Exception:
                milestones = []

    items = [
        MilestoneItem(
            milestone=m.get("milestone", ""),
            notes=m.get("notes", ""),
            timestamp=m.get("timestamp", ""),
        )
        for m in milestones
    ]

    return ProgressResponse(
        user_id=user_id,
        total_milestones=len(items),
        milestones=items,
    )


@router.post("/{user_id}/milestone")
async def add_milestone(user_id: str, body: MilestoneRequest):
    """Manually add a progress milestone for a user."""
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = {
        "milestone": body.milestone,
        "notes": body.notes or "",
        "timestamp": timestamp,
    }

    db = _get_firestore()
    if db:
        try:
            db.collection("users").document(user_id).collection("progress").document().set(entry)
            return {"status": "saved", "storage": "firestore", "timestamp": timestamp}
        except Exception:
            pass

    # Fallback to local storage
    _LOCAL_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _local_path(user_id)
    existing = []
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            pass
    existing.append(entry)
    path.write_text(json.dumps(existing, indent=2))

    return {"status": "saved", "storage": "local", "timestamp": timestamp}


@router.delete("/{user_id}/data")
async def delete_user_data(user_id: str):
    """Permanently delete all user profile data, ACE cognitive memory, progress, and conversation history (Right to Erasure)."""
    from agent.tools.ace_memory import delete_user_ace_memory

    # 1. Delete ACE Cognitive Memory
    delete_user_ace_memory(user_id)

    # 2. Delete Firestore documents
    db = _get_firestore()
    if db:
        try:
            user_ref = db.collection("users").document(user_id)
            for subcol in ["progress", "conversations", "ace_notes", "ace_skills", "ace_reflections"]:
                docs = user_ref.collection(subcol).stream()
                for doc in docs:
                    doc.reference.delete()
            user_ref.delete()
        except Exception:
            pass

    # 3. Delete local files
    try:
        p_path = _local_path(user_id)
        if p_path.exists():
            p_path.unlink()
    except Exception:
        pass

    try:
        conv_dir = pathlib.Path(__file__).parent.parent.parent / "sessions" / "conversations"
        safe = "".join(c for c in user_id if c.isalnum() or c in "-_")
        c_path = conv_dir / f"{safe}.json"
        if c_path.exists():
            c_path.unlink()
    except Exception:
        pass

    return {
        "status": "deleted",
        "user_id": user_id,
        "message": "All personal profile data, conversation history, progress milestones, and ACE cognitive memory have been permanently deleted."
    }

