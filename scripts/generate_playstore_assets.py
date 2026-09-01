import os
from pathlib import Path
from PIL import Image, ImageOps

base_dir = Path("/Volumes/Crucial X9 Pro For Mac/Antigravity/data/antigravity/scratch/cybermentor")
web_img_dir = base_dir / "web" / "img"
submission_dir = base_dir / "submission"
out_dir = submission_dir / "playstore_assets"
out_dir.mkdir(parents=True, exist_ok=True)

# 1. App Icon: 512x512 PNG
icon_src = web_img_dir / "app_icon.jpg"
if icon_src.exists():
    with Image.open(icon_src) as img:
        img_512 = img.convert("RGBA").resize((512, 512), Image.Resampling.LANCZOS)
        img_512.save(out_dir / "app_icon_512x512.png", "PNG")
        print("Generated app_icon_512x512.png")

# 2. Feature Graphic: 1024x500 PNG
banner_src = web_img_dir / "hero_banner.jpg"
if not banner_src.exists():
    banner_src = submission_dir / "cybermentor_cover.jpg"

if banner_src.exists():
    with Image.open(banner_src) as img:
        img_feature = ImageOps.fit(img.convert("RGB"), (1024, 500), method=Image.Resampling.LANCZOS)
        img_feature.save(out_dir / "feature_graphic_1024x500.png", "PNG")
        print("Generated feature_graphic_1024x500.png")

# 3. Phone Screenshots (16:9) - 1920x1080 Landscape
screenshots = [
    ("live_screenshot_welcome.png", "phone_screenshot_1_welcome.png"),
    ("live_screenshot_app.png", "phone_screenshot_2_coach_studio.png"),
    ("live_screenshot_mindmap.png", "phone_screenshot_3_skills_mindmap.png"),
    ("live_screenshot_analytics.png", "phone_screenshot_4_soc_interview_rubric.png"),
]

for src_name, out_name in screenshots:
    src_path = web_img_dir / src_name
    if src_path.exists():
        with Image.open(src_path) as img:
            landscape = ImageOps.fit(img.convert("RGB"), (1920, 1080), method=Image.Resampling.LANCZOS)
            landscape.save(out_dir / out_name, "PNG")
            
            # Tablet Screenshots (16:9)
            landscape.save(out_dir / f"tablet_7in_{out_name}", "PNG")
            landscape.save(out_dir / f"tablet_10in_{out_name}", "PNG")
            print(f"Generated {out_name} (1920x1080)")

print(f"All Play Store assets saved to: {out_dir}")
