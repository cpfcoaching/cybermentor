"""
CyberMentor — Automated Demo Video & Narration Generator
Uses ElevenLabs (Custom Voice ID: o2VOIZD2uQWZgLM51WKf) for voice narration
and composites with Google AI & visual assets into a demo video presentation.
"""

import os
import json
import pathlib
import urllib.request
import urllib.error
import ssl

OUTPUT_DIR = pathlib.Path(__file__).parent.parent.parent / "submission" / "demo_video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "o2VOIZD2uQWZgLM51WKf")
API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

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
        "title": "1,164-Episode RAG Knowledge Base & Voice Coaching",
        "duration": "60s",
        "visual_asset": "app_icon.jpg",
        "narration_script": (
            "What makes CyberMentor uniquely powerful is its knowledge base. "
            "We indexed over 1,160 real Breaking Into Cybersecurity podcast episodes and Notion production briefs into a parallel semantic search engine. "
            "Ask how to break in with a history degree, and CyberMentor recalls Daniel Ayala's exact advice and timestamp. "
            "With real-time voice speech-to-text and audio narration, candidates can practice live mock interviews hands-free."
        )
    },
    {
        "scene_number": 5,
        "title": "Zero-Cost Serverless Cloud Run & Call to Action",
        "duration": "30s",
        "visual_asset": "hero_banner.jpg",
        "narration_script": (
            "CyberMentor is deployed 100% serverless on Google Cloud Run with scale-to-zero compute and Cloud Firestore persistent memory, "
            "running comfortably within Google Cloud's free tier. "
            "Try CyberMentor live today in your browser or mobile device, and accelerate your cybersecurity career journey."
        )
    }
]

def synthesize_speech_elevenlabs(text: str, output_path: pathlib.Path, api_key: str, voice_id: str) -> bool:
    ctx = ssl._create_unverified_context()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.85
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "xi-api-key": api_key
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            audio_bytes = resp.read()
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"  🎙️ Generated audio: {output_path.name} ({len(audio_bytes)} bytes)")
            return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        print(f"  ❌ ElevenLabs Error on {output_path.name}: {err_msg}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🎬 CyberMentor Demo Video Narration Generator")
    print(f"📁 Output Directory: {OUTPUT_DIR}")
    print(f"🗣️ Voice ID: {VOICE_ID}")
    
    if not API_KEY or not API_KEY.startswith("sk_"):
        print("\n⚠️  Note: ElevenLabs API Key must start with 'sk_'.")
        print("Please check your ElevenLabs settings at: https://elevenlabs.io/app/settings/api-keys")
        print("Then set ELEVENLABS_API_KEY=sk_... in your .env file.\n")
    
    # Save narration scripts
    script_manifest = OUTPUT_DIR / "narration_script.json"
    with open(script_manifest, "w", encoding="utf-8") as f:
        json.dump(SCENES, f, indent=2)
    print(f"✅ Saved script manifest to {script_manifest}")

    if API_KEY and API_KEY.startswith("sk_"):
        print("\n🎙️ Generating Scene Narration Audio via ElevenLabs...")
        for scene in SCENES:
            num = scene["scene_number"]
            audio_file = OUTPUT_DIR / f"scene_{num}_narration.mp3"
            print(f"Generating Scene {num}: {scene['title']}...")
            synthesize_speech_elevenlabs(scene["narration_script"], audio_file, API_KEY, VOICE_ID)

if __name__ == "__main__":
    main()
