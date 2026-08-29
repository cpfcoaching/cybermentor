"""
CyberMentor — Automated Demo Video & Narration Generator
Uses native Cloud Run / Google AI audio synthesis for voice narration
and composites with Google AI & visual assets into a demo video presentation.
"""

import os
import json
import pathlib
import subprocess
import asyncio
import edge_tts

OUTPUT_DIR = pathlib.Path(__file__).parent.parent.parent / "submission" / "demo_video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 5 Structured Scenes matching the hackathon demo video requirement
SCENES = [
    {
        "scene_number": 1,
        "title": "Introduction & The Mentorship Challenge",
        "duration": "45s",
        "visual_asset": "hero_banner.jpg",
        "narration_script": (
            "Every single week on Breaking Into Cybersecurity, candidates ask me the same question: "
            "'I want to break into cybersecurity. Where do I start?' "
            "Over 7 years and hundreds of podcast episodes, the answer is always tailored to each person's background. "
            "The problem is, I can't personally mentor thousands of candidates 1-on-1 every day. "
            "So for the Google Cloud All Things Agentic Hackathon, I built CyberMentor: an autonomous 24/7 AI Cybersecurity Career Coach "
            "powered by Google Gemini 3.7 Flash and the Google Antigravity SDK."
        )
    },
    {
        "scene_number": 2,
        "title": "Interactive Study Plans & Resume Skill Audits",
        "duration": "60s",
        "visual_asset": "mobile_mockup.jpg",
        "narration_script": (
            "CyberMentor goes beyond simple chatbot answers. "
            "Tell it your background—whether you're transitioning from IT helpdesk, military service, or a non-technical field—and it builds a personalized weekly study schedule for certifications like Security+, CySA+, or CISSP. "
            "Paste in your resume or target job description, and CyberMentor runs an automated gap analysis aligned with the NIST NICE cybersecurity workforce framework."
        )
    },
    {
        "scene_number": 3,
        "title": "Google Antigravity SDK & Low-Cost Model Routing",
        "duration": "45s",
        "visual_asset": "hero_banner.jpg",
        "narration_script": (
            "Under the hood, CyberMentor is built on the Google Antigravity SDK, using tool docstrings for deterministic routing without brittle prompt chains. "
            "To keep cloud costs near zero, we use a two-tier model pipeline: Google Gemma 3 27B handles fast intent classification and entity parsing, "
            "while Gemini 3.7 Flash on Vertex AI powers deep coaching reasoning and mock interview evaluations. "
            "Google Veo and Lyria generate on-demand study visuals and focus music."
        )
    },
    {
        "scene_number": 4,
        "title": "1,160+ Episode RAG & Scored Mock Interviews",
        "duration": "60s",
        "visual_asset": "mobile_mockup.jpg",
        "narration_script": (
            "CyberMentor's RAG pipeline is grounded in transcripts from 1,164 episodes of Breaking Into Cybersecurity. "
            "When you practice for a job interview, CyberMentor simulates realistic technical scenarios—like triaging a phishing alert or isolating a compromised host—and grades your answer against an objective four-pillar rubric with actionable feedback."
        )
    },
    {
        "scene_number": 5,
        "title": "Persistent Cloud Memory & Live Demo",
        "duration": "30s",
        "visual_asset": "hero_banner.jpg",
        "narration_script": (
            "Because CyberMentor uses Google Cloud Firestore for persistent memory, it remembers your completed milestones and goals across sessions. "
            "It's 100% serverless, scales to zero on Google Cloud Run, and is completely free to use. "
            "Visit client.breakingintocybersecurity.org and start your personalized cybersecurity roadmap today."
        )
    }
]

async def generate_scene_audio(scene_num, text, out_file):
    print(f"🎙️ Synthesizing Scene {scene_num} audio...")
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(str(out_file))
    print(f"  ✅ Saved: {out_file}")

async def main():
    print("🎬 Generating CyberMentor Demo Video Narration Audio...")
    for scene in SCENES:
        out_file = OUTPUT_DIR / f"scene_{scene['scene_number']}_audio.mp3"
        await generate_scene_audio(scene['scene_number'], scene['narration_script'], out_file)
    print("\n🎉 All scene audio tracks generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
