"""
YouTube Transcript & SEO Skill Extraction Pipeline for Breaking Into Cybersecurity

Fetches live videos and transcripts from the Breaking Into Cybersecurity channel (UCM3YAEDu6W7JmQc0kb-CNtw)
using Google Cloud YouTube Data API v3 and extracts high-impact SEO skill tags and hiring competencies
(inspired by YouTubeSEOMaximizer) to maximize candidate discoverability and agent knowledge retrieval.

Usage:
    python data/scripts/ingest_youtube.py --limit 50
    python data/scripts/ingest_youtube.py --all
"""

import argparse
import json
import os
import pathlib
import re
import sys

_DEFAULT_CHANNEL_ID = "UCM3YAEDu6W7JmQc0kb-CNtw"
OUTPUT = pathlib.Path(__file__).parent.parent / "knowledge" / "youtube_transcripts.json"

# Curated Cybersecurity SEO & Skill Taxonomy for SEO Maximizer
_SEO_SKILL_PATTERNS = {
    "Reverse Engineering": [r"reverse engineer", r"binary analyst", r"ghidra", r"ida pro", r"disassembl", r"malware"],
    "DevSecOps & AppSec": [r"devsecops", r"appsec", r"application security", r"ci/cd", r"pipeline", r"secure code", r"vibe coding"],
    "AI Security & LLMs": [r"ai ", r"artificial intelligence", r"llm", r"ai agent", r"prompt injection", r"ai extortion", r"machine learning"],
    "SOC & Incident Response": [r"soc", r"siem", r"splunk", r"sentinel", r"incident response", r"threat mitigation", r"threat hunt", r"triage"],
    "Penetration Testing & Red Teaming": [r"bug bounty", r"pentest", r"penetration test", r"red team", r"exploit", r"burp suite", r"nmap"],
    "Cloud Security": [r"cloud", r"aws", r"azure", r"gcp", r"terraform", r"iam", r"kubernetes", r"docker"],
    "GRC & Risk Management": [r"grc", r"governance", r"compliance", r"risk", r"nist", r"iso 27001", r"audit", r"policy"],
    "Career Pivot & Mentorship": [r"interview", r"resume", r"career", r"networking", r"mentor", r"pc builder", r"internship", r"job market", r"certs"]
}


def extract_seo_skills_and_tags(title: str, description: str, transcript: str) -> list[str]:
    """Extract high-traffic SEO skill keywords and competency tags from video content."""
    combined_text = f"{title} {description} {transcript}".lower()
    matched_skills = []

    for skill_name, patterns in _SEO_SKILL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined_text, re.IGNORECASE):
                if skill_name not in matched_skills:
                    matched_skills.append(skill_name)
                break

    return matched_skills or ["Cybersecurity Careers", "Breaking Into Cyber"]


def get_all_channel_videos(api_key: str, channel_id: str, limit: int = 50, fetch_all: bool = False) -> list[dict]:
    """Fetch video metadata from the YouTube channel with full pagination."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: google-api-python-client not installed. Run: pip install google-api-python-client")
        sys.exit(1)

    youtube = build("youtube", "v3", developerKey=api_key)
    
    uploads_playlist_id = None
    try:
        channel_resp = youtube.channels().list(id=channel_id, part="contentDetails").execute()
        items = channel_resp.get("items", [])
        if items:
            uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except Exception as e:
        print(f"Warning: Could not fetch uploads playlist: {e}")

    videos = []
    next_page_token = None

    if uploads_playlist_id:
        print(f"📋 Querying Uploads Playlist ID: {uploads_playlist_id}")
        while True:
            max_to_fetch = 50 if (fetch_all or (limit - len(videos) >= 50)) else (limit - len(videos))
            if max_to_fetch <= 0 and not fetch_all:
                break

            req = youtube.playlistItems().list(
                playlistId=uploads_playlist_id,
                part="snippet",
                maxResults=max_to_fetch,
                pageToken=next_page_token
            )
            resp = req.execute()
            for item in resp.get("items", []):
                snippet = item.get("snippet", {})
                res_id = snippet.get("resourceId", {})
                vid = res_id.get("videoId")
                if vid:
                    videos.append({
                        "video_id": vid,
                        "title": snippet.get("title", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "description": snippet.get("description", "")[:500],
                        "channel": "Breaking Into Cybersecurity",
                        "host": "Christophe Foulon",
                    })
                    if not fetch_all and len(videos) >= limit:
                        break

            next_page_token = resp.get("nextPageToken")
            if not next_page_token or (not fetch_all and len(videos) >= limit):
                break
    else:
        while True:
            max_to_fetch = 50 if (fetch_all or (limit - len(videos) >= 50)) else (limit - len(videos))
            if max_to_fetch <= 0 and not fetch_all:
                break

            req = youtube.search().list(
                channelId=channel_id,
                part="snippet",
                order="date",
                type="video",
                maxResults=max_to_fetch,
                pageToken=next_page_token
            )
            resp = req.execute()
            for item in resp.get("items", []):
                vid = item["id"].get("videoId")
                if vid:
                    videos.append({
                        "video_id": vid,
                        "title": item["snippet"]["title"],
                        "published_at": item["snippet"]["publishedAt"],
                        "description": item["snippet"]["description"][:500],
                        "channel": "Breaking Into Cybersecurity",
                        "host": "Christophe Foulon",
                    })
                    if not fetch_all and len(videos) >= limit:
                        break

            next_page_token = resp.get("nextPageToken")
            if not next_page_token or (not fetch_all and len(videos) >= limit):
                break

    return videos


def get_transcript(video_id: str) -> str:
    """Fetch transcript for a YouTube video using youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("ERROR: youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
        sys.exit(1)

    try:
        api = YouTubeTranscriptApi()
        snippets = list(api.fetch(video_id))
        texts = []
        for s in snippets:
            if hasattr(s, "text"):
                texts.append(s.text)
            elif isinstance(s, dict) and "text" in s:
                texts.append(s["text"])
        return " ".join(texts)
    except Exception as e:
        return f"[Transcript unavailable: {e}]"


def main():
    parser = argparse.ArgumentParser(description="Ingest YouTube transcripts & extract SEO skills for CyberMentor")
    parser.add_argument("--channel", default=_DEFAULT_CHANNEL_ID, help="YouTube channel ID")
    parser.add_argument("--api-key", default=None, help="YouTube Data API key")
    parser.add_argument("--limit", type=int, default=50, help="Number of videos to process")
    parser.add_argument("--all", action="store_true", help="Fetch ALL videos on the channel without limit")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YouTube Data API key required. Pass --api-key or set YOUTUBE_API_KEY environment variable.")
        sys.exit(1)

    print(f"📡 Connecting to YouTube Data API v3 for 'Breaking Into Cybersecurity' ({args.channel})...")
    videos = get_all_channel_videos(api_key, args.channel, limit=args.limit, fetch_all=args.all)
    print(f"📹 Discovered {len(videos)} videos from channel")

    # Load existing to merge
    existing_items = []
    if OUTPUT.exists():
        try:
            existing_items = json.loads(OUTPUT.read_text())
        except Exception:
            existing_items = []

    existing_vids = {item.get("video_id"): item for item in existing_items if item.get("video_id")}

    updated_items = []
    newly_added = 0

    for i, video in enumerate(videos, 1):
        vid = video["video_id"]
        if vid in existing_vids:
            item = existing_vids[vid]
            # Ensure SEO skills are extracted
            if "seo_skill_tags" not in item:
                item["seo_skill_tags"] = extract_seo_skills_and_tags(item.get("title", ""), item.get("description", ""), item.get("transcript", ""))
            updated_items.append(item)
            continue

        print(f"  🎙️ [{i}/{len(videos)}] Transcribing & Extracting SEO Skills: {video['title'][:55]}...")
        transcript = get_transcript(vid)
        seo_skills = extract_seo_skills_and_tags(video["title"], video["description"], transcript)

        takeaways = [
            f"Key cybersecurity insights and guidance from '{video['title']}'.",
            f"Target Skills: {', '.join(seo_skills)}.",
            "Breaking Into Cybersecurity mentorship lessons and career strategy."
        ]

        entry = {
            **video,
            "category": "breaking_into_cyber_episodes",
            "seo_skill_tags": seo_skills,
            "key_takeaways": takeaways,
            "transcript": transcript[:4000],
            "url": f"https://youtube.com/watch?v={vid}",
        }
        updated_items.append(entry)
        newly_added += 1

    # Keep any foundational episodes from before
    for item in existing_items:
        if item.get("video_id") not in {u.get("video_id") for u in updated_items}:
            if "seo_skill_tags" not in item:
                item["seo_skill_tags"] = extract_seo_skills_and_tags(item.get("title", ""), item.get("description", ""), item.get("transcript", ""))
            updated_items.append(item)

    OUTPUT.write_text(json.dumps(updated_items, indent=2))
    print(f"\n✅ Ingestion complete! Total indexed knowledge base episodes: {len(updated_items)} (New: {newly_added}) at {OUTPUT}")


if __name__ == "__main__":
    main()
