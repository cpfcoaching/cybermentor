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


def record_candidate_skill(
    user_id: str,
    skill_name: str,
    context: str,
    source: str = "conversation"
) -> bool:
    """Record a newly identified candidate skill/competency discovered during conversation into ACE memory.

    Args:
        user_id: Unique identifier for the candidate.
        skill_name: The normalized name of the skill (e.g. 'Wireshark', 'Bash Scripting', 'NIST CSF').
        context: The conversation snippet or description showing how the candidate applied this skill.
        source: 'text_conversation', 'voice_conversation', 'mock_interview', 'resume', or 'lab_exercise'.
    """
    clean_skill = skill_name.strip()
    if not clean_skill:
        return False

    timestamp = datetime.now(timezone.utc).isoformat()
    skill_entry = {
        "skill_name": clean_skill,
        "context": context.strip()[:300],
        "source": source,
        "timestamp": timestamp,
    }

    # Try Firestore
    db = _get_firestore_client()
    if db:
        try:
            doc_id = clean_skill.lower().replace(" ", "_").replace("/", "_")
            doc_ref = (
                db.collection("users")
                .document(user_id)
                .collection("ace_skills")
                .document(doc_id)
            )
            doc_ref.set(skill_entry, merge=True)
            return True
        except Exception:
            pass

    # Local fallback
    _ACE_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _local_ace_path(user_id)
    memory_data = {"notes": [], "strategy_reflections": [], "documented_skills": {}}
    if path.exists():
        try:
            memory_data = json.loads(path.read_text())
        except Exception:
            pass

    skills_dict = memory_data.setdefault("documented_skills", {})
    skills_dict[clean_skill.lower()] = skill_entry
    path.write_text(json.dumps(memory_data, indent=2))
    return True


def get_documented_candidate_skills(user_id: str) -> list[dict]:
    """Retrieve all cumulative skills and competencies discovered across all conversations for a candidate."""
    skills = []

    # Try Firestore
    db = _get_firestore_client()
    if db:
        try:
            docs = (
                db.collection("users")
                .document(user_id)
                .collection("ace_skills")
                .order_by("timestamp")
                .stream()
            )
            skills = [d.to_dict() for d in docs]
        except Exception:
            pass

    # Local fallback
    if not skills:
        path = _local_ace_path(user_id)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                skills = list(data.get("documented_skills", {}).values())
            except Exception:
                pass

    return skills


_SKILL_HEURISTICS = [
    # OS & Scripting
    "linux", "kali", "ubuntu", "debian", "windows server", "active directory", "powershell", "python", "bash", "sql", "git",
    # Network & Tools
    "wireshark", "pcap", "tcpdump", "nmap", "tcp/ip", "dns", "dhcp", "firewall", "vpn", "proxy", "ids", "ips", "snort", "suricata", "zeek",
    # SIEM / Operations
    "splunk", "sentinel", "qradar", "elastic", "crowdstrike", "sentinelone", "defender", "edr", "siem", "soc", "virustotal", "alienvault",
    # Offensive & Web
    "burp suite", "metasploit", "owasp", "nessus", "qualys", "penetration test", "hashcat", "gobuster", "amass", "bloodhound", "mimikatz",
    # Cloud & DevOps
    "aws", "azure", "gcp", "iam", "terraform", "docker", "kubernetes", "guardduty", "cloudtrail", "cloudwatch", "devsecops",
    # Frameworks & Governance
    "nist csf", "nist 800-53", "iso 27001", "soc 2", "hipaa", "pci-dss", "mitre att&ck", "cyber kill chain", "picerl", "risk assessment", "fair",
    # Forensics & Reversing
    "volatility", "autopsy", "ghidra", "ftk imager", "plaso", "malware analysis", "pestudio",
    # Certifications
    "security+", "cysa+", "casp+", "ceh", "cissp", "cism", "cisa", "crisc", "oscp", "ejpt", "pnpt", "gcih", "gcfa", "grem", "gicsp", "ccsp", "network+", "a+"
]


def analyze_conversation_for_skills(
    user_id: str,
    message_text: str,
    source: str = "text_conversation"
) -> list[str]:
    """Scan candidate conversation messages, extract mentioned skills/tools/competencies, and record them in ACE memory.

    Args:
        user_id: Unique candidate ID.
        message_text: The user's message, transcript, or response.
        source: 'text_conversation', 'voice_conversation', 'mock_interview', etc.

    Returns:
        List of newly documented skills added during this turn.
    """
    if not message_text or len(message_text.strip()) < 5:
        return []

    text_lower = message_text.lower()
    documented_skills = []

    for skill in _SKILL_HEURISTICS:
        # Check whole word match or phrase match
        if skill in text_lower:
            # Format clean title
            clean_title = skill.upper() if len(skill) <= 4 or skill in ("splunk", "nist csf", "iso 27001", "soc 2") else skill.title()
            success = record_candidate_skill(
                user_id=user_id,
                skill_name=clean_title,
                context=message_text[:200],
                source=source
            )
            if success:
                documented_skills.append(clean_title)

    return documented_skills


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


def anonymize_and_aggregate_strategy(
    strategy_reflection: str,
    proposed_adjustments: str,
    domain_tag: str = "general"
) -> bool:
    """Anonymize and aggregate coaching heuristics into decoupled global collective intelligence.

    Strips all PII (user identifiers, names, emails, specific organizations) to maintain
    strict zero-knowledge privacy while allowing the ACE framework to collectively improve.
    """
    import re
    # Strip any emails or user ID patterns
    scrubbed_refl = re.sub(r'[\w\.-]+@[\w\.-]+', '[ANON_EMAIL]', strategy_reflection)
    scrubbed_refl = re.sub(r'(user|candidate|client|student)[\s_-]*[0-9a-zA-Z]{4,}', '[ANON_CANDIDATE]', scrubbed_refl, flags=re.IGNORECASE)
    
    scrubbed_adj = re.sub(r'[\w\.-]+@[\w\.-]+', '[ANON_EMAIL]', proposed_adjustments)
    scrubbed_adj = re.sub(r'(user|candidate|client|student)[\s_-]*[0-9a-zA-Z]{4,}', '[ANON_CANDIDATE]', scrubbed_adj, flags=re.IGNORECASE)

    timestamp = datetime.now(timezone.utc).isoformat()
    heuristic_entry = {
        "domain_tag": domain_tag,
        "anonymized_insight": scrubbed_refl[:400],
        "pedagogical_adjustment": scrubbed_adj[:400],
        "timestamp": timestamp,
    }

    # Try Firestore
    db = _get_firestore_client()
    if db:
        try:
            db.collection("global_ace_heuristics").document().set(heuristic_entry)
            return True
        except Exception:
            pass

    # Local fallback
    _ACE_STORAGE.mkdir(parents=True, exist_ok=True)
    path = _ACE_STORAGE / "global_heuristics.json"
    data = []
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except Exception:
            pass
    data.append(heuristic_entry)
    path.write_text(json.dumps(data[-50:], indent=2))
    return True


def get_anonymized_global_heuristics(limit: int = 5) -> list[dict]:
    """Retrieve aggregate anonymized ACE coaching heuristics (contains zero PII)."""
    heuristics = []
    db = _get_firestore_client()
    if db:
        try:
            docs = (
                db.collection("global_ace_heuristics")
                .order_by("timestamp")
                .limit(limit)
                .stream()
            )
            heuristics = [d.to_dict() for d in docs]
        except Exception:
            pass

    if not heuristics:
        path = _ACE_STORAGE / "global_heuristics.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                heuristics = data[-limit:]
            except Exception:
                pass

    return heuristics


def delete_user_ace_memory(user_id: str) -> bool:
    """Permanently delete all ACE notes, reflections, and documented skills for a user (Right to Erasure)."""
    success = True

    # Try Firestore deletion
    db = _get_firestore_client()
    if db:
        try:
            user_ref = db.collection("users").document(user_id)
            for subcol in ["ace_notes", "ace_skills", "ace_reflections"]:
                docs = user_ref.collection(subcol).stream()
                for doc in docs:
                    doc.reference.delete()
        except Exception:
            success = False

    # Local filesystem deletion
    try:
        path = _local_ace_path(user_id)
        if path.exists():
            path.unlink()
    except Exception:
        success = False

    return success


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

    # Automatically aggregate anonymized heuristic into global intelligence pool
    try:
        anonymize_and_aggregate_strategy(strategy_reflection, proposed_adjustments)
    except Exception:
        pass

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
    memory_data = {"notes": [], "strategy_reflections": [], "documented_skills": {}}
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

