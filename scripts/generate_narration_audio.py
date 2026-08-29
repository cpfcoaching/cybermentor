#!/usr/bin/env python3
"""
Generates timed voice narration tracks for each scene in the demo walkthrough.
Uses edge-tts with the natural en-US-ChristopherNeural voice.
"""

import asyncio
import json
import subprocess
from pathlib import Path
import edge_tts

OUT_DIR = Path("submission/demo_video/audio_scenes")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "en-US-ChristopherNeural"
SCRIPT_FILE = Path("submission/demo_video/narration_script_full.json")

def get_duration(audio_file: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

async def main():
    with open(SCRIPT_FILE, "r") as f:
        scenes = json.load(f)

    manifest = []
    print(f"🎙️ Generating full 5-minute voice tracks using voice: {VOICE}...")
    
    for s in scenes:
        scene_id = s["scene_number"]
        out_mp3 = OUT_DIR / f"scene_{scene_id}_full.mp3"
        comm = edge_tts.Communicate(s["narration_script"], VOICE, rate="+2%")
        await comm.save(str(out_mp3))
        
        dur = get_duration(out_mp3)
        print(f"  Scene {scene_id} ({s['title']}): {dur:.2f}s")
        manifest.append({
            "id": scene_id,
            "title": s["title"],
            "file": str(out_mp3),
            "duration": dur,
            "text": s["narration_script"]
        })
        
    manifest_file = OUT_DIR / "manifest_full.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
        
    total_dur = sum(m["duration"] for m in manifest)
    print(f"\n✅ Total Walkthrough Audio Duration: {total_dur:.2f}s ({total_dur/60:.2f} minutes)")
    print(f"Manifest written to {manifest_file}")

if __name__ == "__main__":
    asyncio.run(main())
