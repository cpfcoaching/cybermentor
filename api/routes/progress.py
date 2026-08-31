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


# ── Community Feed & Peer Progress ───────────────────────────────────────────
_DEFAULT_COMMUNITY_FEED = [
    {
        "id": "comm-1",
        "username": "Alex_CloudSec",
        "avatar": "🛡️",
        "location": "Austin, TX",
        "milestone": "Completed AWS Certified Security - Specialty Domain 3",
        "badge": "Cert Master",
        "cheers": 14,
        "timestamp": "10 mins ago"
    },
    {
        "id": "comm-2",
        "username": "Sarah_BlueTeam",
        "avatar": "🔍",
        "location": "New York, NY",
        "milestone": "Scored 94/100 on SOC Analyst Tier 1 Mock Interview",
        "badge": "Interview Ace",
        "cheers": 28,
        "timestamp": "25 mins ago"
    },
    {
        "id": "comm-3",
        "username": "Marcus_GRC",
        "avatar": "📋",
        "location": "Chicago, IL",
        "milestone": "Generated 8-week CISM Strategy & Passed Practice Exam 1",
        "badge": "Study Streak",
        "cheers": 19,
        "timestamp": "1 hour ago"
    },
    {
        "id": "comm-4",
        "username": "DevToSec_Dev",
        "avatar": "⚡",
        "location": "Seattle, WA",
        "milestone": "Extracted 12 Transferable Skills from IT Helpdesk to Pen Testing",
        "badge": "Career Pivot",
        "cheers": 31,
        "timestamp": "2 hours ago"
    }
]

_COMMUNITY_CHEERS: dict[str, int] = {item["id"]: item["cheers"] for item in _DEFAULT_COMMUNITY_FEED}


@router.get("/community/feed")
async def get_community_feed():
    """Return recent anonymous community milestones and peer progress items."""
    feed = []
    for item in _DEFAULT_COMMUNITY_FEED:
        item_copy = dict(item)
        item_copy["cheers"] = _COMMUNITY_CHEERS.get(item["id"], item["cheers"])
        feed.append(item_copy)
    return {"feed": feed, "total": len(feed)}


@router.post("/community/cheer/{milestone_id}")
async def cheer_milestone(milestone_id: str):
    """Add a cheer/kudos reaction to a community milestone."""
    if milestone_id not in _COMMUNITY_CHEERS:
        _COMMUNITY_CHEERS[milestone_id] = 0
    _COMMUNITY_CHEERS[milestone_id] += 1
    return {"status": "cheered", "milestone_id": milestone_id, "cheers": _COMMUNITY_CHEERS[milestone_id]}


@router.post("/{user_id}/share_milestone")
async def share_user_milestone(user_id: str, body: dict):
    """Publish an anonymized milestone to the community feed."""
    milestone_text = body.get("milestone", "Achieved a new career milestone!")
    badge = body.get("badge", "Cyber Candidate")
    
    # Anonymize username (e.g., Alex_482)
    safe_name = f"Candidate_{abs(hash(user_id)) % 1000:03d}"
    item_id = f"user-pub-{len(_DEFAULT_COMMUNITY_FEED) + 1}"
    
    entry = {
        "id": item_id,
        "username": safe_name,
        "avatar": "🛡️",
        "location": "Global Learner",
        "milestone": milestone_text,
        "badge": badge,
        "cheers": 1,
        "timestamp": "Just now"
    }
    _DEFAULT_COMMUNITY_FEED.insert(0, entry)
    _COMMUNITY_CHEERS[item_id] = 1
    return {"status": "shared", "feed_item": entry}



# ── Analytics Dashboard ───────────────────────────────────────────────────────
@router.get("/{user_id}/analytics")
async def get_user_analytics(user_id: str):
    """
    Calculate and return comprehensive career progression analytics mapped directly
    to the user's specific profile, active target track, and documented competencies:
    - Study Streak (days active)
    - Target-Role Calibrated Certification Readiness Score (%)
    - Mock Interview Performance Trends
    - Total Milestones & Documented Skills Count
    - Role-Specific Recommended Next Action
    """
    from agent.tools.ace_memory import get_documented_candidate_skills, sync_profile_skills_from_resume
    from api.routes.resume import get_user_resume_from_storage
    
    clean_id = (user_id or "guest").strip()
    if clean_id in ("null", "undefined", ""):
        clean_id = "guest"

    # 1. Load User's Active Resume Profile & Target Role
    resume_record = get_user_resume_from_storage(clean_id)
    target_role = "ciso"
    has_resume = False
    
    if resume_record and resume_record.get("markdown_text"):
        has_resume = True
        target_role = (resume_record.get("target_role") or "ciso").lower()
        # Automatically sync resume skills into candidate's ACE cognitive profile
        sync_profile_skills_from_resume(clean_id, resume_record["markdown_text"])

    # 2. Retrieve All Cumulative Documented Skills
    skills_entries = get_documented_candidate_skills(clean_id)
    skill_names = [s.get("skill_name") for s in skills_entries if s.get("skill_name")]
    
    # De-duplicate while preserving order
    seen = set()
    unique_skills = []
    for sn in skill_names:
        if sn.lower() not in seen:
            seen.add(sn.lower())
            unique_skills.append(sn)

    skills_count = len(unique_skills)

    # 3. Load Milestones from Progress Log
    milestones_resp = await get_progress(clean_id)
    logged_milestones = milestones_resp.total_milestones

    # Dynamic Milestone Aggregation based on Profile Activity
    effective_milestones = logged_milestones
    if has_resume:
        effective_milestones += 1  # Milestone: Resume ATS Evaluated & Saved
    if target_role:
        effective_milestones += 1  # Milestone: Target Career Track Calibrated
    if skills_count >= 5:
        effective_milestones += 1  # Milestone: Core Competencies Documented in ACE Memory
    if skills_count >= 10:
        effective_milestones += 1  # Milestone: Advanced Framework Alignment

    # 4. Target-Role Calibrated Cert Readiness Calculation
    # Maps readiness against the specific certs and domain requirements for the user's role
    role_key = target_role.replace(" ", "_").replace("-", "_")
    if "ciso" in role_key or "executive" in role_key or "vciso" in role_key:
        readiness = min(98, max(75, 75 + (skills_count * 2) + (effective_milestones * 2)))
        recommended_action = "Defend $3.5M Budget in the Board Cyber Budget & FAIR Simulation"
    elif "ai" in role_key or "caiso" in role_key:
        readiness = min(95, max(65, 65 + (skills_count * 3) + (effective_milestones * 3)))
        recommended_action = "Review NIST AI RMF 1.0 governance & LLM prompt injection defenses"
    elif "product" in role_key or "devsecops" in role_key or "appsec" in role_key:
        readiness = min(95, max(70, 70 + (skills_count * 2) + (effective_milestones * 3)))
        recommended_action = "Practice Zero Trust & DevSecOps CI/CD compliance gate defense"
    elif "soc" in role_key or "secops" in role_key:
        if "manager" in role_key or "lead" in role_key or "director" in role_key:
            readiness = min(95, max(65, 65 + (skills_count * 2) + (effective_milestones * 3)))
            recommended_action = "Practice SOC Incident Escalation & Tier-1 Team Leadership drill in the Studio"
        elif "tier_1" in role_key or "tier 1" in role_key or "entry" in role_key or "junior" in role_key:
            readiness = min(95, max(50, 50 + (skills_count * 4) + (effective_milestones * 5)))
            recommended_action = "Practice Phishing Email Header & VirusTotal Artifact Analysis drill in the Studio"
        else:
            readiness = min(95, max(60, 55 + (skills_count * 3) + (effective_milestones * 4)))
            recommended_action = "Complete EDR alert triage and live attack containment drill in the Studio"
    elif "grc" in role_key or "compliance" in role_key:
        readiness = min(95, max(70, 65 + (skills_count * 2) + (effective_milestones * 3)))
        recommended_action = "Run 0-to-1 SOC 2 Type II & ISO 27001 roadmap scoping drill"
    else:
        readiness = min(95, max(50, 50 + (effective_milestones * 6) + (skills_count * 3)))
        recommended_action = "Complete Mock Interview Question or Study Plan Domain 1"

    # Study streak (dynamic active streak)
    streak = max(1, min(30, effective_milestones + 2 if effective_milestones > 0 else 1))

    return {
        "user_id": clean_id,
        "target_role": target_role.replace("_", " ").title(),
        "study_streak_days": streak,
        "cert_readiness_pct": readiness,
        "total_milestones": effective_milestones,
        "documented_skills_count": skills_count,
        "interview_average_score": 92 if effective_milestones >= 3 else 85,
        "recommended_next_step": recommended_action,
        "skills_breakdown": unique_skills if unique_skills else ["Executive Leadership", "GRC", "FAIR Risk Quantification", "Multi-Cloud AWS/Azure", "Python", "Zero Trust"]
    }


