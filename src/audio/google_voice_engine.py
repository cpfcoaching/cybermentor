"""
CyberMentor — Google-Native Voice Engine & Zero-Cost Voice Cloning Architecture

Replaces external paid TTS APIs (ElevenLabs) with:
1. Google Cloud Text-to-Speech Custom Neural Voice
2. Gemini Live Bidirectional Native Audio Synthesis
3. Self-Hosted Zero-Cost Reference Voice Cloner (XTTS/Kokoro)
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

class GoogleVoiceEngine:
    """
    Orchestrates zero-marginal-cost voice generation using Google Cloud & Gemini.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "cybermentor-506813")
        self.reference_audio_dir = Path("data/voice_samples")
        self.reference_audio_dir.mkdir(parents=True, exist_ok=True)

    def get_voice_persona_prompt(self) -> str:
        """
        Prompt instructions for Gemini Live native audio to emulate the Island Boy / Christophe Foulon persona.
        """
        return (
            "Voice Persona: Speak as Christophe Foulon, host of Breaking Into Cybersecurity. "
            "Tone: Warm, encouraging, authoritative yet approachable, with a smooth Island cadence, "
            "rhythmic pacing, and clear cybersecurity technical terminology pronunciation."
        )

    def format_google_custom_voice_request(self, text: str, voice_model_id: str = "cybermentor-island-boy") -> Dict[str, Any]:
        """
        Prepares request payload for Google Cloud Custom Voice model.
        """
        return {
            "input": {"text": text},
            "voice": {
                "languageCode": "en-US",
                "customVoice": {
                    "model": f"projects/{self.project_id}/locations/us-central1/models/{voice_model_id}"
                }
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.02,
                "pitch": -0.5,
                "sampleRateHertz": 44100
            }
        }
