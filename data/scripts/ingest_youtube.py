"""
YouTube Transcript Ingestion (Optional)

Pulls transcripts from a YouTube channel and appends them to the
knowledge base as additional context for the CyberMentor agent.

Requirements:
    pip install youtube-transcript-api google-api-python-client

Usage:
    python data/scripts/ingest_youtube.py --channel UCVeW9qkBjo3zosnqUbG7CFw --limit 20
"""

import argparse
import json
import pathlib
import sys

OUTPUT = pathlib.Path(__file__).parent.parent / "knowledge" / "youtube_transcripts.json"


def get_channel_videos(api_key: str, channel_id: str, limit: int = 20) -> list[dict]:
    """Fetch recent video IDs from a YouTube channel."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: google-api-python-client not installed.")
        print("       Run: pip install google-api-python-client")
        sys.exit(1)

    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=limit,
        order="date",
        type="video",
    )
    response = request.execute()
    return [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"]["description"][:500],
        }
        for item in response.get("items", [])
    ]


def get_transcript(video_id: str) -> str:
    """Fetch transcript for a YouTube video."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("ERROR: youtube-transcript-api not installed.")
        print("       Run: pip install youtube-transcript-api")
        sys.exit(1)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except Exception as e:
        return f"[Transcript unavailable: {e}]"


def main():
    parser = argparse.ArgumentParser(description="Ingest YouTube transcripts into CyberMentor knowledge base")
    parser.add_argument("--channel", required=True, help="YouTube channel ID")
    parser.add_argument("--api-key", default=None, help="YouTube Data API key (or set YOUTUBE_API_KEY env var)")
    parser.add_argument("--limit", type=int, default=20, help="Number of videos to process")
    args = parser.parse_args()

    import os
    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YouTube API key required. Pass --api-key or set YOUTUBE_API_KEY.")
        sys.exit(1)

    print(f"Fetching {args.limit} videos from channel {args.channel}...")
    videos = get_channel_videos(api_key, args.channel, args.limit)
    print(f"Found {len(videos)} videos")

    results = []
    for video in videos:
        print(f"  Processing: {video['title'][:60]}...")
        transcript = get_transcript(video["video_id"])
        results.append({
            **video,
            "transcript": transcript,
            "url": f"https://youtube.com/watch?v={video['video_id']}",
        })

    OUTPUT.write_text(json.dumps(results, indent=2))
    print(f"\n✅ Saved {len(results)} transcripts to {OUTPUT}")

if __name__ == "__main__":
    main()
