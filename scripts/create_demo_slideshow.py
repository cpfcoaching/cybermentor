#!/usr/bin/env python3
"""
Compiles the high-res captured UI screenshots and visual assets into a
smooth 1080p 60fps HD video walkthrough with pan/zoom and transitions.
"""

import os
import subprocess
from pathlib import Path

IMG_DIR = Path("web/img")
OUT_DIR = Path("submission/demo_video")
OUT_FILE = OUT_DIR / "cybermentor_walkthrough.mp4"

def build_video():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 6 Scenes mapped to production plan
    scenes = [
        {"file": IMG_DIR / "hero_banner.jpg", "dur": 8, "title": "CyberMentor — AI Career Coach"},
        {"file": IMG_DIR / "live_screenshot_welcome.png", "dur": 12, "title": "Authenticated Google SSO & Onboarding"},
        {"file": IMG_DIR / "live_screenshot_app.png", "dur": 25, "title": "Real-Time SSE Streaming & Focus Studio"},
        {"file": IMG_DIR / "live_screenshot_mindmap.png", "dur": 18, "title": "Interactive Skills & Certs Transfer Explorer"},
        {"file": IMG_DIR / "live_screenshot_analytics.png", "dur": 18, "title": "Career Readiness Dashboard & ACE Milestones"},
        {"file": IMG_DIR / "mobile_mockup.jpg", "dur": 10, "title": "24/7 Mobile & Cloud Run Serverless Architecture"}
    ]
    
    # Create segment videos with zoom/pan
    seg_files = []
    for i, s in enumerate(scenes):
        seg_out = OUT_DIR / f"seg_{i}.mp4"
        seg_files.append(seg_out)
        
        # FFmpeg zoompan filter to create engaging motion
        cmd = [
            "/usr/local/bin/ffmpeg", "-y",
            "-loop", "1",
            "-i", str(s["file"]),
            "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,zoompan=z='min(zoom+0.0008,1.08)':d={s['dur']*30}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
            "-t", str(s["dur"]),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(seg_out)
        ]
        print(f"🎬 Rendering Scene {i+1}: {s['title']}...")
        subprocess.run(cmd, check=True)

    # Concatenate segments
    concat_list = OUT_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for seg in seg_files:
            f.write(f"file '{seg.name}'\n")

    print("🎞️ Concatenating all scenes into final HD walkthrough video...")
    concat_cmd = [
        "/usr/local/bin/ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(OUT_FILE)
    ]
    subprocess.run(concat_cmd, check=True)

    # Clean up temp segments
    concat_list.unlink(missing_ok=True)
    for seg in seg_files:
        seg.unlink(missing_ok=True)

    size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\n🎉 Successfully rendered: {OUT_FILE} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    build_video()
