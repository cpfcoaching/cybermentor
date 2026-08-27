"""
High-Speed Parallel Async Transcriber & Ingestor for CyberMentor.
Uses a concurrent worker pool to fetch metadata, transcribe, and extract SEO competencies in parallel.
"""

import asyncio
import concurrent.futures
import json
import os
import pathlib
import re
import ssl
import sys
import urllib.request

OUTPUT = pathlib.Path(__file__).parent.parent / "knowledge" / "youtube_transcripts.json"

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

def extract_seo_skills(title: str, description: str, transcript: str) -> list[str]:
    combined = f"{title} {description} {transcript}".lower()
    matched = []
    for skill, patterns in _SEO_SKILL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined):
                matched.append(skill)
                break
    return matched or ["Cybersecurity Career Strategy", "Breaking Into Cyber"]

def fetch_video_transcript_sync(video_id: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        snippets = list(api.fetch(video_id))
        texts = [s.get("text", "") if isinstance(s, dict) else getattr(s, "text", "") for s in snippets]
        return " ".join(texts)
    except Exception as e:
        return f"[Transcript available via YouTube video audio: {e}]"

async def process_video_async(executor, video: dict) -> dict:
    loop = asyncio.get_running_loop()
    vid = video.get("video_id")
    title = video.get("title", "")
    desc = video.get("description", "")
    
    # Run transcript fetch in parallel thread pool
    transcript = await loop.run_in_executor(executor, fetch_video_transcript_sync, vid)
    skills = extract_seo_skills(title, desc, transcript)
    
    return {
        **video,
        "category": "breaking_into_cyber_episodes",
        "seo_skill_tags": skills,
        "key_takeaways": [
            f"Mentorship guidance from '{title}'.",
            f"Key focus areas: {', '.join(skills)}.",
            "Real-world advice from Breaking Into Cybersecurity."
        ],
        "transcript": transcript[:4000],
        "url": video.get("url") or f"https://youtube.com/watch?v={vid}"
    }

async def fast_ingest_catalog():
    if not OUTPUT.exists():
        print(f"Error: {OUTPUT} does not exist.")
        return

    with open(OUTPUT, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    print(f"⚡ Turbo-transcription pipeline initiated for {len(catalog)} episodes...")
    
    # Use thread pool with 20 parallel workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        tasks = [process_video_async(executor, ep) for ep in catalog]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    cleaned_results = []
    for r in results:
        if isinstance(r, dict):
            cleaned_results.append(r)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(cleaned_results, f, indent=2)

    print(f"🚀 Turbo processing complete! Processed {len(cleaned_results)} episodes in parallel.")

def main():
    asyncio.run(fast_ingest_catalog())

if __name__ == "__main__":
    main()
