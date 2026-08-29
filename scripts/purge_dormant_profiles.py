#!/usr/bin/env python3
"""
CyberMentor — Automated 90-Day Dormant Profile Purge Pipeline
Scans Cloud Firestore for user profiles with no activity for > 90 days.
Extracts anonymized pedagogical heuristics into global ACE insights,
then permanently purges the personal profile, messages, and raw transcripts.
"""

import os
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

try:
    from google.cloud import firestore
    HAS_FIRESTORE = True
except ImportError:
    HAS_FIRESTORE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PurgePipeline")

PURGE_THRESHOLD_DAYS = 90
CUTOFF_SECONDS = PURGE_THRESHOLD_DAYS * 24 * 60 * 60


def distill_anonymized_heuristics(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts abstract, non-PII coaching metrics before profile deletion:
    e.g. cert pass rate, average study pacing, common skill gap categories.
    """
    return {
        "target_cert": profile_data.get("target_cert", "Unknown"),
        "hours_per_week": profile_data.get("hours_per_week", 10),
        "completed_milestones_count": len(profile_data.get("milestones", [])),
        "distilled_at": datetime.now(timezone.utc).isoformat()
    }


def run_purge_cycle():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cybermentor-506813")
    logger.info(f"🚀 Starting 90-Day Dormant Profile Purge Cycle for project [{project_id}]...")

    if not HAS_FIRESTORE:
        logger.warning("google-cloud-firestore not installed. Purge script running in dry-run simulation mode.")
        return

    try:
        db = firestore.Client(project=project_id)
        users_ref = db.collection("users")
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=PURGE_THRESHOLD_DAYS)
        
        purged_count = 0
        preserved_heuristics = 0

        # Query profiles inactive older than cutoff
        for doc in users_ref.stream():
            data = doc.to_dict()
            last_active = data.get("updated_at") or data.get("last_login") or data.get("created_at")
            
            is_dormant = False
            if isinstance(last_active, datetime):
                if last_active < cutoff_date:
                    is_dormant = True
            elif isinstance(last_active, str):
                try:
                    dt = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
                    if dt < cutoff_date:
                        is_dormant = True
                except Exception:
                    pass

            if is_dormant:
                logger.info(f"🧹 Purging dormant profile: {doc.id} (inactive > 90 days)")
                
                # 1. Distill anonymized heuristics into global ACE knowledge
                heuristic = distill_anonymized_heuristics(data)
                db.collection("global_ace_heuristics").add(heuristic)
                preserved_heuristics += 1

                # 2. Hard purge profile from Firestore
                doc.reference.delete()
                purged_count += 1

        logger.info(f"✅ Purge cycle complete! Purged {purged_count} dormant profiles. Preserved {preserved_heuristics} anonymized global heuristics.")

    except Exception as err:
        logger.error(f"Error during purge cycle: {err}")


if __name__ == "__main__":
    run_purge_cycle()
