#!/usr/bin/env python3
"""
Generates 30-second 9:16 vertical shorts from the master walkthrough video
with pixel-perfect auto-wrapped text, centered layouts, and generous padding.
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
        "headline": "STOP PAYING $15,000\nFOR EXPENSIVE BOOTCAMPS",
        "subtitle": "Autonomous AI Mentorship Powered by Google AI"
    },
    {
        "id": "short_02_cert_study_planner",
        "title": "6-Week Security+ Study Planner",
        "start": "00:01:40",
        "duration": "00:00:30",
        "tag": "📅 HOUR-CALIBRATED ROADMAP",
        "headline": "COMPTIA SECURITY+\nIN JUST 6 WEEKS",
        "subtitle": "Personalized Lab Schedules & Exam Weightings"
    },
    {
        "id": "short_03_skills_mindmap_analytics",
        "title": "Interactive Cybersecurity Mindmap",
        "start": "00:02:25",
        "duration": "00:00:30",
        "tag": "🧠 SKILLS & CERTS MINDMAP",
        "headline": "TRANSFER YOUR IT SKILLS\nDIRECTLY TO CYBER",
        "subtitle": "SOC Operations, Cloud Security & GRC Roadmaps"
    },
    {
        "id": "short_04_mock_interview_drill",
        "title": "SOC Incident Triage Mock Interview",
        "start": "00:03:30",
        "duration": "00:00:30",
        "tag": "🎤 SCORED MOCK INTERVIEWS",
        "headline": "REALISTIC SOC INCIDENT\nTRIAGE DRILLS",
        "subtitle": "Scored 4-Pillar Rubrics & 1,160+ Podcast Insights"
    }
]

def load_font(font_path, size):
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def create_overlay_png(clip, out_png):
    # 1080x1920 RGBA transparent canvas
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_tag = load_font("/System/Library/Fonts/Helvetica.ttc", 26)
    font_title = load_font("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 40)
    font_sub = load_font("/System/Library/Fonts/Helvetica.ttc", 24)
    font_url_label = load_font("/System/Library/Fonts/Helvetica.ttc", 24)
    font_url = load_font("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)

    # ── Top Card Overlay (y: 120 - 520, w: 960 centered at x=60..1020) ──────
    card_x1, card_y1, card_x2, card_y2 = 50, 120, 1030, 520
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=(10, 15, 30, 240), outline=(56, 189, 248, 200), width=3)

    # Dynamic Tag Pill (Auto-width centered)
    tag_text = clip["tag"]
    tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0] + 40
    tag_x1 = int((1080 - tag_w) / 2)
    tag_y1 = card_y1 + 25
    draw.rounded_rectangle([tag_x1, tag_y1, tag_x1 + tag_w, tag_y1 + 45], radius=12, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=2)
    draw.text((tag_x1 + 20, tag_y1 + 8), tag_text, font=font_tag, fill=(56, 189, 248, 255))

    # Headline (Centered, 2 lines)
    headline_lines = clip["headline"].split("\n")
    cur_y = tag_y1 + 68
    for line in headline_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_title)
        line_w = line_bbox[2] - line_bbox[0]
        draw.text(((1080 - line_w) / 2, cur_y), line, font=font_title, fill=(255, 255, 255, 255))
        cur_y += 50

    # Subtitle (Centered, with padding)
    sub_text = clip["subtitle"]
    sub_bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(((1080 - sub_w) / 2, cur_y + 15), sub_text, font=font_sub, fill=(148, 163, 184, 255))

    # ── Bottom URL Watermark Card (y: 1400 - 1680) ───────────────────────────
    bcard_x1, bcard_y1, bcard_x2, bcard_y2 = 50, 1400, 1030, 1680
    draw.rounded_rectangle([bcard_x1, bcard_y1, bcard_x2, bcard_y2], radius=28, fill=(10, 15, 30, 245), outline=(34, 211, 238, 220), width=3)

    # Label (Centered)
    lbl_text = "⚡ TRY THE AI CAREER COACH (100% FREE)"
    lbl_bbox = draw.textbbox((0, 0), lbl_text, font=font_url_label)
    lbl_w = lbl_bbox[2] - lbl_bbox[0]
    draw.text(((1080 - lbl_w) / 2, bcard_y1 + 30), lbl_text, font=font_url_label, fill=(56, 189, 248, 255))

    # URL Pill (Centered with generous padding)
    url_text = "client.breakingintocybersecurity.org"
    url_bbox = draw.textbbox((0, 0), url_text, font=font_url)
    url_w = url_bbox[2] - url_bbox[0]
    pill_w = url_w + 60
    pill_x1 = int((1080 - pill_w) / 2)
    pill_y1 = bcard_y1 + 80
    draw.rounded_rectangle([pill_x1, pill_y1, pill_x1 + pill_w, pill_y1 + 80], radius=20, fill=(2, 6, 23, 255), outline=(34, 211, 238, 255), width=2)
    draw.text(((1080 - url_w) / 2, pill_y1 + 20), url_text, font=font_url, fill=(34, 211, 238, 255))

    # Sub-footer CTA
    sub_cta = "Built with Google Antigravity SDK & Gemini 3.7"
    cta_bbox = draw.textbbox((0, 0), sub_cta, font=font_sub)
    cta_w = cta_bbox[2] - cta_bbox[0]
    draw.text(((1080 - cta_w) / 2, pill_y1 + 105), sub_cta, font=font_sub, fill=(100, 116, 139, 255))

    img.save(out_png)

def render_short(clip):
    out_file = OUT_DIR / f"{clip['id']}.mp4"
    overlay_png = OVERLAY_DIR / f"{clip['id']}_overlay.png"
    create_overlay_png(clip, overlay_png)

    print(f"🎬 Rendering Short: {clip['title']} ({clip['duration']}s)...")

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

    print(f"🚀 Re-generating {len(SHORTS_CLIPS)} Social Media & YouTube Shorts with centered borders...")
    for clip in SHORTS_CLIPS:
        render_short(clip)
        
    print(f"\n🎉 All {len(SHORTS_CLIPS)} shorts rendered successfully in {OUT_DIR}/")

if __name__ == "__main__":
    main()
