#!/usr/bin/env python3
"""
Generates 30-second 9:16 vertical shorts from the master walkthrough video
with on-screen URL watermark and typography cards using PIL overlays and FFmpeg.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VIDEO_SRC = Path("submission/demo_video/cybermentor_walkthrough.mp4")
OUT_DIR = Path("submission/social_shorts")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OVERLAY_DIR = OUT_DIR / "temp_overlays"
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

SHORTS_CLIPS = [
    {
        "id": "short_01_roi_tuition_savings",
        "title": "Stop Paying $15k For Bootcamps",
        "start": "00:00:20",
        "duration": "00:00:30",
        "tag": "💰 $15,000+ TUITION SAVINGS",
        "headline": "STOP PAYING FOR EXPENSIVE BOOTCAMPS",
        "subtitle": "Autonomous AI Mentorship Powered by Google AI"
    },
    {
        "id": "short_02_cert_study_planner",
        "title": "6-Week Security+ Study Planner",
        "start": "00:01:40",
        "duration": "00:00:30",
        "tag": "📅 HOUR-CALIBRATED ROADMAP",
        "headline": "COMPTIA SECURITY+ IN 6 WEEKS",
        "subtitle": "Personalized Lab Schedules & Exam Weightings"
    },
    {
        "id": "short_03_skills_mindmap_analytics",
        "title": "Interactive Cybersecurity Mindmap",
        "start": "00:02:25",
        "duration": "00:00:30",
        "tag": "🧠 SKILLS & CERTS MINDMAP",
        "headline": "TRANSFER YOUR IT SKILLS TO CYBER",
        "subtitle": "SOC Operations, Cloud Security & GRC Roadmaps"
    },
    {
        "id": "short_04_mock_interview_drill",
        "title": "SOC Incident Triage Mock Interview",
        "start": "00:03:30",
        "duration": "00:00:30",
        "tag": "🎤 SCORED MOCK INTERVIEWS",
        "headline": "REALISTIC SOC INCIDENT TRIAGE",
        "subtitle": "Scored 4-Pillar Rubrics & 1,160+ Podcast Insights"
    }
]

def create_overlay_png(clip, out_png):
    # 1080x1920 RGBA transparent image
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Try loading system fonts
    try:
        font_tag = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 30)
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_url_label = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 26)
        font_url = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 42)
    except Exception:
        font_tag = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_url_label = ImageFont.load_default()
        font_url = ImageFont.load_default()

    # ── Top Card Overlay (y: 180 - 480) ─────────────────────────────────────
    # Glassmorphism dark pill background
    draw.rounded_rectangle([40, 160, 1040, 480], radius=28, fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)
    
    # Tag Pill
    draw.rounded_rectangle([80, 190, 600, 245], radius=15, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=2)
    draw.text((105, 202), clip["tag"], font=font_tag, fill=(56, 189, 248, 255))
    
    # Headline & Subtitle
    draw.text((80, 270), clip["headline"], font=font_title, fill=(255, 255, 255, 255))
    draw.text((80, 390), clip["subtitle"], font=font_sub, fill=(148, 163, 184, 255))

    # ── Bottom URL Watermark Card (y: 1420 - 1680) ───────────────────────────
    draw.rounded_rectangle([40, 1440, 1040, 1680], radius=28, fill=(15, 23, 42, 240), outline=(34, 211, 238, 200), width=3)
    
    # Label
    draw.text((80, 1475), "⚡ TRY THE AI COACH LIVE (FREE):", font=font_url_label, fill=(56, 189, 248, 255))
    
    # URL Pill
    draw.rounded_rectangle([80, 1530, 1000, 1630], radius=20, fill=(2, 6, 23, 255), outline=(34, 211, 238, 255), width=2)
    draw.text((115, 1555), "client.breakingintocybersecurity.org", font=font_url, fill=(34, 211, 238, 255))

    img.save(out_png)

def render_short(clip):
    out_file = OUT_DIR / f"{clip['id']}.mp4"
    overlay_png = OVERLAY_DIR / f"{clip['id']}_overlay.png"
    create_overlay_png(clip, overlay_png)

    print(f"🎬 Rendering Short: {clip['title']} ({clip['duration']}s)...")

    # Filter graph:
    # 1. Scale/crop 16:9 1080p to 9:16 vertical 1080x1920 blurred background
    # 2. Overlay sharp 1080x608 center gameplay/tour video at y=656
    # 3. Overlay typography cards at y=0
    filter_graph = (
        "[0:v]split=2[bgsrc][fgsrc];"
        "[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.35[bg];"
        "[fgsrc]scale=1080:608[fg];"
        "[bg][fg]overlay=0:656[composed];"
        "[composed][1:v]overlay=0:0[vout]"
    )

    cmd = [
        "/usr/local/bin/ffmpeg", "-y",
        "-ss", clip["start"],
        "-i", str(VIDEO_SRC),
        "-i", str(overlay_png),
        "-t", clip["duration"],
        "-filter_complex", filter_graph,
        "-map", "[vout]",
        "-map", "0:a:0",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(out_file)
    ]

    subprocess.run(cmd, check=True)
    size_mb = out_file.stat().st_size / (1024 * 1024)
    print(f"  ✅ Saved: {out_file} ({size_mb:.2f} MB)")

def main():
    if not VIDEO_SRC.exists():
        print(f"❌ Source video not found at {VIDEO_SRC}")
        return

    print(f"🚀 Generating {len(SHORTS_CLIPS)} Social Media & YouTube Shorts (9:16 Vertical 1080x1920)...")
    for clip in SHORTS_CLIPS:
        render_short(clip)
        
    print(f"\n🎉 All {len(SHORTS_CLIPS)} shorts rendered successfully in {OUT_DIR}/")

if __name__ == "__main__":
    main()
