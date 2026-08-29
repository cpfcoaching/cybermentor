#!/usr/bin/env python3
"""
Uploads CyberMentor walkthrough and shorts directly to YouTube using YouTube Data API v3.
"""

import os
import sys
import time
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

TOKEN_FILE = Path("/Volumes/Crucial X9 Pro For Mac/GDriveSync/Antigravity/YouTubeSEOMaximizer/token_breakingintocyber.json")

DEMO_VIDEO = Path("submission/demo_video/cybermentor_walkthrough.mp4")
SHORTS_DIR = Path("submission/social_shorts")

def get_authenticated_service():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"Token file {TOKEN_FILE} not found.")

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), ['https://www.googleapis.com/auth/youtube.force-ssl'])
    if creds and creds.expired and creds.refresh_token:
        print("🔄 Refreshing expired YouTube token...")
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file_path, title, description, tags, privacy_status="unlisted"):
    print(f"\n🚀 Uploading '{title}' ({file_path.name})...")
    body = {
        'snippet': {
            'title': title[:100],
            'description': description[:5000],
            'tags': tags,
            'categoryId': '27' # Education
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True, mimetype='video/mp4')
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Uploading: {int(status.progress() * 100)}% complete...")

    video_id = response.get('id')
    video_url = f"https://youtu.be/{video_id}"
    print(f"✅ Upload Complete! Video ID: {video_id}")
    print(f"🔗 Video URL: {video_url}")
    return video_id, video_url

def main():
    youtube = get_authenticated_service()

    # 1. Upload Master Demo Video
    master_desc = """CyberMentor is an autonomous AI career coach that guides candidates from career discovery to their first cybersecurity role. Built for the Google Cloud #AllThingsAgenticHackathon using Google Antigravity SDK, Gemini 3.7 Flash, Gemma 3, Veo, Lyria, and Cloud Firestore.

Try the Live App: https://client.breakingintocybersecurity.org
GitHub Repository: https://github.com/cpfcoaching/cybermentor

0:00 - Introduction & The Mentorship Bottleneck
1:08 - Frictionless Onboarding & CompTIA Security+ Study Planner
2:20 - Google Antigravity SDK Routing & Interactive Mindmap
3:21 - 1,164-Episode RAG & Scored Mock Interview Drills
4:26 - Serverless Google Cloud Run & State Persistence

#GoogleCloud #AgenticAI #AllThingsAgenticHackathon #Gemini #Cybersecurity #CareerCoach"""

    master_tags = [
        "CyberMentor", "Google Cloud", "Gemini 3.7", "Google Antigravity",
        "Agentic AI", "AllThingsAgenticHackathon", "Cybersecurity Career",
        "CompTIA Security+", "SOC Analyst", "Cloud Security", "AI Career Coach"
    ]

    master_id, master_url = upload_video(
        youtube,
        DEMO_VIDEO,
        "CyberMentor: Autonomous AI Cybersecurity Career Coach (Google Antigravity SDK & Gemini 3.7)",
        master_desc,
        master_tags,
        privacy_status="unlisted"
    )

    # 2. Upload Shorts
    shorts_meta = [
        {
            "file": SHORTS_DIR / "short_01_roi_tuition_savings.mp4",
            "title": "Stop Paying $15,000 For Cyber Bootcamps! #Shorts #Cybersecurity #AI",
            "desc": "CyberMentor provides free, autonomous AI mentorship for cybersecurity careers. Try it: https://client.breakingintocybersecurity.org\n\n#Shorts #Cybersecurity #CareerAdvice #GoogleCloud #AllThingsAgenticHackathon"
        },
        {
            "file": SHORTS_DIR / "short_02_cert_study_planner.mp4",
            "title": "How to Pass CompTIA Security+ in 6 Weeks with AI #Shorts #SecurityPlus",
            "desc": "Personalized, hour-calibrated certification study plans with hands-on labs. Try it: https://client.breakingintocybersecurity.org\n\n#Shorts #SecurityPlus #CompTIA #Infosec #GoogleCloud"
        },
        {
            "file": SHORTS_DIR / "short_03_skills_mindmap_analytics.mp4",
            "title": "How to Transfer IT Skills to Cybersecurity #Shorts #CareerAdvice",
            "desc": "Map your Helpdesk, SysAdmin, or Networking skills directly into SOC and Cloud roles. Try it: https://client.breakingintocybersecurity.org\n\n#Shorts #Cybersecurity #ITCareer #Mentorship"
        },
        {
            "file": SHORTS_DIR / "short_04_mock_interview_drill.mp4",
            "title": "SOC Analyst Mock Interview: Incident Triage Drill #Shorts #Infosec",
            "desc": "Scored rubric evaluations and incident response scenarios powered by Gemini 3.7. Try it: https://client.breakingintocybersecurity.org\n\n#Shorts #MockInterview #SOCAnalyst #IncidentResponse"
        }
    ]

    results = [{"name": "Master Demo Video", "id": master_id, "url": master_url}]

    for sm in shorts_meta:
        if sm["file"].exists():
            sid, surl = upload_video(
                youtube,
                sm["file"],
                sm["title"],
                sm["desc"],
                master_tags,
                privacy_status="unlisted"
            )
            results.append({"name": sm["title"], "id": sid, "url": surl})

    print("\n" + "="*60)
    print("🎉 ALL VIDEOS UPLOADED TO YOUTUBE AS UNLISTED:")
    for r in results:
        print(f"  • {r['name']}: {r['url']}")
    print("="*60)

if __name__ == "__main__":
    main()
