"""
Seed Firestore

Idempotent script to create initial Firestore collections and seed
the knowledge base into the database.

Usage:
    python data/scripts/seed_firestore.py
"""

import json
import os
import sys
import pathlib

# Add project root to path
ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

def main():
    try:
        from google.cloud import firestore
    except ImportError:
        print("ERROR: google-cloud-firestore not installed. Run: pip install google-cloud-firestore")
        sys.exit(1)

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("ERROR: GOOGLE_CLOUD_PROJECT not set in .env")
        sys.exit(1)

    print(f"Connecting to Firestore project: {project}")
    db = firestore.Client(project=project)

    # ── Seed knowledge base ──────────────────────────────────────────────
    knowledge_dir = ROOT / "data" / "knowledge"

    for filename in ["certifications.json", "career_paths.json"]:
        path = knowledge_dir / filename
        if not path.exists():
            print(f"  SKIP: {filename} not found")
            continue

        collection_name = f"knowledge_{filename.replace('.json', '')}"
        data = json.loads(path.read_text())

        if isinstance(data, list):
            for i, item in enumerate(data):
                doc_id = item.get("name", f"item_{i}").replace(" ", "_").lower()
                db.collection(collection_name).document(doc_id).set(item)
                print(f"  ✅ Seeded {collection_name}/{doc_id}")
        elif isinstance(data, dict):
            for key, value in data.items():
                db.collection(collection_name).document(key).set(value)
                print(f"  ✅ Seeded {collection_name}/{key}")

    print("\n✅ Firestore seed complete!")
    print("   Collections created:")
    print("   - knowledge_certifications")
    print("   - knowledge_career_paths")
    print("\n   Next: users/ and sessions/ will be created automatically as users interact with CyberMentor.")

if __name__ == "__main__":
    main()
