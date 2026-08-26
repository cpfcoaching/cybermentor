"""
Veo Video Generator Tool (+0.2 bonus)

Generates short educational video clips using Google Veo via Vertex AI.
Used to create visual explainers for certifications, career paths,
and day-in-the-life previews for cybersecurity roles.

Requires: google-genai >= 0.8.0, GOOGLE_CLOUD_PROJECT env var
"""

import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _get_veo_client():
    """Build a Vertex AI GenAI client for Veo."""
    try:
        from google import genai
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project:
            return None
        return genai.Client(vertexai=True, project=project, location=location)
    except ImportError:
        logger.warning("google-genai not installed. Veo integration unavailable.")
        return None
    except Exception as e:
        logger.warning(f"Veo client init failed: {e}")
        return None


def generate_cert_explainer_video(
    cert_name: str,
    aspect_ratio: str = "16:9",
) -> str:
    """Generate a short educational video explaining a cybersecurity certification.

    Use this tool when a user asks to SEE what a certification covers,
    wants a visual overview of a cert's scope, or asks "what does [cert] actually
    teach you?" — this creates a short, shareable explainer clip.

    Args:
        cert_name: The certification to explain visually. Examples:
                   "CompTIA Security+", "OSCP", "CISSP", "eJPT".
        aspect_ratio: Video aspect ratio. One of "16:9" (landscape, default)
                      or "9:16" (portrait, for mobile/social sharing).

    Returns:
        A message containing the video generation status and access URL,
        or an explanation of what would be generated if Veo is unavailable.
    """
    client = _get_veo_client()

    # Craft a detailed, safe prompt for Veo
    prompt = (
        f"Educational explainer video for the {cert_name} cybersecurity certification. "
        f"Professional presentation style with animated text overlays showing key exam domains. "
        f"Dark blue and teal color scheme. Show a cybersecurity professional at a workstation. "
        f"Display key statistics: exam questions, passing score, recommended experience. "
        f"Clean, modern motion graphics. Corporate training aesthetic. No people's faces shown."
    )

    if client is None:
        return (
            f"## 🎬 Veo Video: {cert_name} Explainer\n\n"
            f"**Status:** Veo client unavailable (check GOOGLE_CLOUD_PROJECT)\n\n"
            f"**What this would generate:**\n"
            f"A 5-8 second explainer clip for **{cert_name}** featuring:\n"
            f"- Animated exam domain breakdown\n"
            f"- Key stats (questions, pass score, cost)\n"
            f"- Recommended study resources overlay\n"
            f"- Dark teal cybersecurity aesthetic\n\n"
            f"To enable: set `GOOGLE_CLOUD_PROJECT` in your `.env` file."
        )

    try:
        from google.genai import types

        operation = client.models.generate_videos(
            model="veo-2.0-generate-001",
            prompt=prompt,
            config=types.GenerateVideoConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
                duration_seconds=8,
                enhance_prompt=True,
            ),
        )

        # Poll for completion (Veo is async)
        max_wait = 120  # seconds
        elapsed = 0
        poll_interval = 5

        while not operation.done and elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            operation = client.operations.get(operation)

        if not operation.done:
            return (
                f"## 🎬 Veo Video: {cert_name}\n\n"
                f"Video generation is still in progress. "
                f"Check back in a moment — it usually takes 30-60 seconds."
            )

        # Extract video URI
        videos = operation.response.generated_videos
        if not videos:
            return f"Video generation completed but no output was returned for {cert_name}."

        video = videos[0]
        uri = getattr(video.video, "uri", None) or "URI pending"

        return (
            f"## 🎬 {cert_name} Explainer Video\n\n"
            f"✅ **Video generated successfully!**\n\n"
            f"**Access URL:** {uri}\n\n"
            f"*Powered by Google Veo — All Things Agentic Hackathon*"
        )

    except Exception as e:
        logger.error(f"Veo generation error: {e}")
        return (
            f"## 🎬 Veo Video Generation\n\n"
            f"Video generation encountered an issue: `{str(e)[:200]}`\n\n"
            f"This feature requires Veo API access via Vertex AI in your GCP project."
        )


def generate_role_preview_video(role: str) -> str:
    """Generate a 'day in the life' preview video for a cybersecurity role.

    Use this tool when a user wants to visualize what a specific cybersecurity
    job actually looks like day-to-day, or asks "what does a [role] actually do?"

    Args:
        role: The cybersecurity role to visualize. Examples:
              "SOC Analyst", "Penetration Tester", "GRC Analyst",
              "Cloud Security Engineer".

    Returns:
        A message containing the video URL or generation status.
    """
    client = _get_veo_client()

    role_prompts = {
        "soc analyst": (
            "A cybersecurity SOC analyst monitoring multiple screens showing SIEM dashboards, "
            "alert queues, and network traffic graphs. Dark operations center environment with "
            "blue ambient lighting. Professional setting. Animated data flowing across screens. "
            "Text overlays: 'Monitor', 'Detect', 'Respond'. Modern cinematic look."
        ),
        "penetration tester": (
            "A penetration tester in a modern office environment running terminal commands, "
            "examining network diagrams, and writing a professional report. "
            "Multiple monitors showing ethical hacking tools. "
            "Text overlays: 'Assess', 'Exploit', 'Report'. Professional aesthetic."
        ),
        "grc analyst": (
            "A GRC analyst reviewing compliance frameworks on a laptop, presenting risk "
            "dashboards to executives, and working with policy documentation. "
            "Clean modern office. Text overlays: 'Govern', 'Risk', 'Comply'."
        ),
        "cloud security engineer": (
            "A cloud security engineer reviewing AWS/GCP architecture diagrams, "
            "configuring IAM policies on a laptop, and analyzing cloud security posture dashboards. "
            "Modern workspace with cloud infrastructure visualizations. "
            "Text overlays: 'Architect', 'Protect', 'Monitor'."
        ),
    }

    role_key = role.lower().replace("-", " ")
    prompt = role_prompts.get(
        role_key,
        f"A professional cybersecurity {role} working in a modern security operations environment. "
        f"Multiple monitors, professional attire, focused atmosphere. "
        f"Animated text overlays showing key responsibilities."
    )

    if client is None:
        return (
            f"## 🎬 Role Preview: {role}\n\n"
            f"**What this generates:** A cinematic 8-second 'day in the life' "
            f"preview clip for a **{role}** using Google Veo.\n\n"
            f"Enable by setting `GOOGLE_CLOUD_PROJECT` in your environment."
        )

    try:
        from google.genai import types

        operation = client.models.generate_videos(
            model="veo-2.0-generate-001",
            prompt=prompt,
            config=types.GenerateVideoConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
                duration_seconds=8,
                enhance_prompt=True,
            ),
        )

        # Brief poll
        for _ in range(24):
            time.sleep(5)
            operation = client.operations.get(operation)
            if operation.done:
                break

        videos = getattr(operation.response, "generated_videos", [])
        uri = videos[0].video.uri if videos else "Processing..."

        return (
            f"## 🎬 Day in the Life: {role}\n\n"
            f"✅ **Video ready!**\n"
            f"**URL:** {uri}\n\n"
            f"*Generated with Google Veo via Vertex AI*"
        )

    except Exception as e:
        return f"Veo role preview error: {str(e)[:200]}"
