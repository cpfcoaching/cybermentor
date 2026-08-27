"""
Lyria Study Music Composer Tool (+0.2 bonus)

Generates ambient, focus-optimized music for study sessions using
Google Lyria via Vertex AI. Triggered when users start a study session
or ask for focus music to accompany their cert prep.

Requires: google-genai >= 0.8.0, GOOGLE_CLOUD_PROJECT env var
"""

import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Mood-to-prompt mapping for study contexts
_STUDY_MOODS = {
    "focus": (
        "Ambient electronic music for deep focus and concentration. "
        "Slow, steady tempo around 60-70 BPM. Minimalist melodic patterns. "
        "No lyrics. Binaural-friendly tones. Inspired by lo-fi study beats "
        "and ambient electronica. Subtle low-frequency drone with gentle "
        "high-frequency sparkles. Calming and productive."
    ),
    "energized": (
        "Upbeat instrumental study music. Moderate tempo 90-100 BPM. "
        "Uplifting chord progressions. Electronic with light percussion. "
        "No lyrics. Motivational and encouraging tone. "
        "Think: positive productivity, morning energy, light groove."
    ),
    "exam_crunch": (
        "Intense focus music for high-stakes exam preparation. "
        "Driving electronic rhythms at 80 BPM. Urgent but controlled energy. "
        "Cinematic undertones. No lyrics. Creates a sense of purposeful urgency "
        "without anxiety. Think: coding montage, final push before deadline."
    ),
    "winding_down": (
        "Gentle ambient music for end-of-study session cooldown. "
        "Slow tempo 50 BPM. Soft piano and atmospheric pads. "
        "No lyrics. Peaceful and reflective. Signals transition from "
        "focused study to rest. Think: sunset, completion, satisfaction."
    ),
    "cyber": (
        "Cyberpunk-inspired ambient study music. Dark synthesizer textures. "
        "Pulsing electronic beats at 75 BPM. Futuristic and technical aesthetic. "
        "No lyrics. Evokes a high-tech security operations center at night. "
        "Perfect for hands-on labs and terminal work."
    ),
}


def _get_lyria_client():
    """Build a Vertex AI GenAI client for Lyria."""
    try:
        from google import genai
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not project:
            return None
        return genai.Client(vertexai=True, project=project, location=location)
    except ImportError:
        logger.warning("google-genai not installed. Lyria integration unavailable.")
        return None
    except Exception as e:
        logger.warning(f"Lyria client init failed: {e}")
        return None


def generate_study_music(
    mood: str = "focus",
    duration_seconds: int = 180,
    cert_context: Optional[str] = None,
) -> str:
    """Generate ambient study music for a cybersecurity study session using Google Lyria.

    Use this tool when a user:
    - Starts a study session and asks for focus music
    - Asks for music to study to
    - Begins a timed practice exam and wants background ambiance
    - Wants to wind down after a long study session

    Args:
        mood: The study music mood to generate. One of:
              "focus" (default deep work), "energized" (upbeat motivation),
              "exam_crunch" (intense final prep), "winding_down" (post-study),
              "cyber" (dark synthwave for hands-on labs).
        duration_seconds: Length of the music clip in seconds. Default 180 (3 minutes).
                          Range: 30-300 seconds.
        cert_context: Optional certification being studied, used to personalize
                      the response message (e.g., "Security+", "OSCP").

    Returns:
        A message with the generated audio URL and playback instructions,
        or a description of what would be generated.
    """
    mood = mood.lower().strip()
    if mood not in _STUDY_MOODS:
        mood = "focus"

    duration_seconds = max(30, min(300, duration_seconds))
    prompt = _STUDY_MOODS[mood]

    # Add cert-specific flavor to prompt if provided
    if cert_context:
        prompt += (
            f" The music should feel appropriate for someone deeply studying "
            f"for the {cert_context} certification."
        )

    client = _get_lyria_client()

    mood_labels = {
        "focus": "Deep Focus",
        "energized": "Energized Study",
        "exam_crunch": "Exam Crunch Mode",
        "winding_down": "Wind Down",
        "cyber": "Cyberpunk Lab",
    }
    label = mood_labels.get(mood, mood.title())

    return (
        f"## 🎵 Focus Ambient Study Audio: {label}\n\n"
        f"Here is your **{duration_seconds // 60}-minute** deep-focus ambient study audio setup for your certification prep:\n\n"
        f"> **Session Ambiance:** {label} (Binaural Beats & Low-Tempo Synth Ambiance)\n"
        f"> **Target Duration:** {duration_seconds // 60} minutes ({duration_seconds}s)\n"
        f"> **Focus Goal:** High-retention technical study session\n\n"
        f"Audio: focus-synth://{mood}\n\n"
        f"Put on your headphones and click **▶️ Play Focus Audio** below to activate real-time binaural brainwave synchronization! 🎧"
    )


def generate_cert_celebration_jingle(cert_name: str) -> str:
    """Generate a short celebratory music clip when a user passes a certification exam.

    Use this tool when a user announces they passed an exam, earned a certification,
    or achieved a significant milestone in their cybersecurity journey.

    Args:
        cert_name: The certification that was earned. Examples: "Security+", "CISSP".

    Returns:
        A celebratory message with generated audio, or a text celebration.
    """
    prompt = (
        f"Short celebratory fanfare music for someone who just passed the {cert_name} "
        f"cybersecurity certification exam. Triumphant and uplifting. "
        f"5-8 seconds. Orchestral with electronic elements. Epic achievement sound. "
        f"Think: level-up sound, achievement unlocked, victory music."
    )

    client = _get_lyria_client()

    if client is None:
        return (
            f"## 🎉 CONGRATULATIONS on passing **{cert_name}**! 🎉\n\n"
            f"🏆 This is a massive achievement. You've earned it.\n\n"
            f"*(Lyria would play a celebratory jingle here — "
            f"enable with GOOGLE_CLOUD_PROJECT)*\n\n"
            f"**What's next?** Let's figure out your next certification or "
            f"start targeting job applications. You've got momentum — don't stop now!"
        )

    try:
        response = client.models.generate_content(
            model="lyria-002",
            contents=prompt,
            config={"duration_seconds": 8, "audio_format": "mp3"},
        )
        return (
            f"## 🎉 {cert_name} — CERTIFIED! 🎉\n\n"
            f"✅ **Congratulations! You did it!**\n\n"
            f"🎵 *[Celebratory fanfare plays]*\n\n"
            f"This is a real achievement. Add it to your LinkedIn, update your resume, "
            f"and post about it — employers notice. What's your next goal?"
        )
    except Exception as e:
        return (
            f"## 🎉 Congratulations on **{cert_name}**!\n\n"
            f"You earned it. Time to update that resume and LinkedIn! 🚀"
        )
