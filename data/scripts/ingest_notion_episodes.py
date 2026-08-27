"""
Ingest all official Breaking Into Cybersecurity production hub episodes from Notion into CyberMentor knowledge base.
"""

import json
import pathlib
import re

NOTION_DATA_FILE = pathlib.Path("/Users/MacAttack/.gemini/antigravity-ide/brain/4215cb0e-852e-4576-9f8a-417b25555024/.system_generated/steps/228/output.txt")
OUTPUT_FILE = pathlib.Path(__file__).parent.parent / "knowledge" / "youtube_transcripts.json"

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove Notion link tags like [bic-00001]
    return re.sub(r'\[bic-[A-Za-z0-9]+\]', '', text).strip()

def extract_takeaways(notes: str) -> list[str]:
    takeaways = []
    if "Key Takeaways:" in notes:
        parts = notes.split("Key Takeaways:")[1]
        for line in parts.split("\n"):
            line = clean_text(line.strip("* -•\t"))
            if line and len(line) > 15 and not line.startswith("http") and not line.startswith("**"):
                takeaways.append(line)
            if len(takeaways) >= 4 or "Timestamps:" in line or "Guest Bio:" in line:
                break
    elif "In this episode, we explore:" in notes:
        parts = notes.split("In this episode, we explore:")[1]
        for line in parts.split("\n"):
            line = clean_text(line.strip("* -•\t"))
            if line and len(line) > 15:
                takeaways.append(line)
            if len(takeaways) >= 4 or "Timestamps:" in line or "Guest Bio:" in line:
                break
    return takeaways or ["Actionable career advice from industry leaders on Breaking Into Cybersecurity."]

def main():
    if not NOTION_DATA_FILE.exists():
        print(f"Notion data file not found: {NOTION_DATA_FILE}")
        return

    with open(NOTION_DATA_FILE, "r", encoding="utf-8") as f:
        notion_raw = json.load(f)

    results = notion_raw.get("results", [])
    
    # Load existing catalog
    existing_items = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_items = json.load(f)

    existing_urls = {item.get("url") for item in existing_items if item.get("url")}
    existing_titles = {item.get("title", "").lower() for item in existing_items}

    added = 0
    updated = 0

    for page in results:
        props = page.get("properties", {})
        
        title_list = props.get("Episode Title", {}).get("title", []) or props.get("title", {}).get("title", []) or props.get("Name", {}).get("title", [])
        title = title_list[0].get("plain_text", "").strip() if title_list else ""
        
        notes_list = props.get("Notes", {}).get("rich_text", [])
        notes = notes_list[0].get("plain_text", "").strip() if notes_list else ""
        
        guest_list = props.get("Guest Name", {}).get("rich_text", [])
        guest = guest_list[0].get("plain_text", "").strip() if guest_list else ""
        
        company_list = props.get("Guest Company", {}).get("rich_text", [])
        company = company_list[0].get("plain_text", "").strip() if company_list else ""
        
        role_list = props.get("Guest Role", {}).get("rich_text", [])
        role = role_list[0].get("plain_text", "").strip() if role_list else ""

        yt_url = props.get("YouTube URL", {}).get("url") or ""
        ep_id = props.get("Episode ID", {}).get("unique_id", {})
        ep_code = f"{ep_id.get('prefix', 'BIC')}-{ep_id.get('number', '')}" if ep_id and ep_id.get("number") else f"BIC-NOTION-{len(existing_items) + added + 1}"

        pub_date = props.get("Publish Date", {}).get("date", {})
        published_at = pub_date.get("start", "2024-01-01T00:00:00Z") if pub_date else "2024-01-01T00:00:00Z"

        if not title and not notes:
            continue

        clean_title = clean_text(title) or (f"Breaking Into Cybersecurity with {guest}" if guest else "Breaking Into Cybersecurity Episode")
        takeaways = extract_takeaways(notes)

        # Extract YouTube video ID if present
        vid_id = ep_code
        if "youtu.be/" in yt_url:
            vid_id = yt_url.split("youtu.be/")[1].split("?")[0]
        elif "v=" in yt_url:
            vid_id = yt_url.split("v=")[1].split("&")[0]

        entry = {
            "video_id": vid_id,
            "episode_code": ep_code,
            "title": clean_title,
            "guest": guest,
            "guest_role": role,
            "guest_company": company,
            "url": yt_url or "https://youtube.com/c/BreakingIntoCybersecurity",
            "published_at": published_at,
            "channel": "Breaking Into Cybersecurity",
            "host": "Christophe Foulon",
            "category": "breaking_into_cyber_episodes",
            "key_takeaways": takeaways,
            "transcript": clean_text(notes)[:4000],
        }

        # Check if already exists by URL or Title
        if (yt_url and yt_url in existing_urls) or clean_title.lower() in existing_titles:
            # Update existing with richer guest & takeaway metadata
            for item in existing_items:
                if (yt_url and item.get("url") == yt_url) or item.get("title", "").lower() == clean_title.lower():
                    item["guest"] = guest or item.get("guest", "")
                    item["guest_role"] = role or item.get("guest_role", "")
                    item["guest_company"] = company or item.get("guest_company", "")
                    if takeaways and len(takeaways) > len(item.get("key_takeaways", [])):
                        item["key_takeaways"] = takeaways
                    updated += 1
            continue

        existing_items.append(entry)
        existing_urls.add(yt_url)
        existing_titles.add(clean_title.lower())
        added += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_items, f, indent=2)

    print(f"✅ Ingested Notion Hub Episodes! Added: {added}, Enhanced Existing: {updated}. Total Catalog: {len(existing_items)} episodes.")

if __name__ == "__main__":
    main()
