# 🎙️ CyberMentor: Google-Native Voice Cloning & Zero-Cost Audio Architecture

This guide outlines how to migrate from third-party paid TTS APIs (ElevenLabs) to **Google Cloud-native Custom Voice** and self-hosted zero-cost voice cloning, making your **Island Boy voice profile** the permanent signature voice of CyberMentor at $0 recurring API cost.

---

## 🏗️ 3 Google & Open Architectures to Replace ElevenLabs

```text
               ┌───────────────────────────────────────────────────────────┐
               │    Island Boy Reference Audio (Christophe Foulon WAVs)    │
               └─────────────────────────────┬─────────────────────────────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   ▼                         ▼                         ▼
    ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
    │ 1. Google Cloud Custom   │ │ 2. Gemini Live Native   │ │ 3. Self-Hosted Zero-Cost│
    │    Voice (Enterprise)   │ │    Audio Synthesis      │ │    Fast Voice Cloner    │
    ├─────────────────────────┤ ├─────────────────────────┤ ├─────────────────────────┤
    │ • Train dedicated custom│ │ • Bidirectional voice   │ │ • Instant 5-second      │
    │   neural model in GCP   │ │   coaching in browser   │ │   reference clone       │
    │ • Seamless Cloud Run    │ │ • Prompt-conditioned    │ │ • Runs on Cloud Run     │
    │   native IAM integration│ │   cadence and warmth    │ │   at $0 extra API cost  │
    └─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

---

## 🚀 Option 1: Google Cloud Text-to-Speech Custom Voice (Recommended)

Google Cloud TTS allows training a **Custom Voice Model** directly within your Google Cloud project (`cybermentor-506813`).

### How It Works

1. **Prepare Audio Dataset**:
   - Provide 15–30 minutes of clean, isolated speech audio from your *Breaking Into Cybersecurity* podcast or studio recordings (WAV 44.1kHz / 48kHz mono).
   - Generate corresponding transcript lines in a CSV file: `audio_filename.wav, "Transcript of spoken audio"`.

2. **Train Model in Google Cloud Console**:
   - Navigate to [Google Cloud Text-to-Speech > Custom Voice](https://console.cloud.google.com/speech/text-to-speech/custom-voices).
   - Upload your audio dataset bucket (`gs://cybermentor-voice-dataset/`).
   - Initiate training for `cybermentor-island-boy`.

3. **Integration**:
   - Once trained, CyberMentor invokes the model directly via the standard Google Cloud Python SDK with project IAM credentials—no third-party keys or credit cards needed!

```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

synthesis_input = texttospeech.SynthesisInput(text="Welcome back Christophe! Ready for your security interview drill?")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    custom_voice=texttospeech.CustomVoiceParams(
        model="projects/cybermentor-506813/locations/us-central1/models/cybermentor-island-boy"
    )
)
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
```

---

## ⚡ Option 2: Google Gemini Live Multimodal Voice Synthesis

Gemini 2.0 / 3.0 supports **native real-time audio output**, allowing voice streaming directly in the browser with custom persona conditioning:

```typescript
const liveSession = await ai.createLiveSession({
  model: 'gemini-2.0-flash-exp',
  config: {
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: {
            voiceName: "Fenrir" // or custom calibrated persona
          }
        }
      }
    },
    systemInstruction: {
      parts: [{
        text: "You are Christophe Foulon, host of Breaking Into Cybersecurity. Speak with a warm, encouraging Caribbean Island cadence, upbeat tone, and crisp cybersecurity terminology."
      }]
    }
  }
});
```

---

## 💡 Option 3: Zero-Cost Open Source Voice Cloning on Cloud Run

For instant 5-second voice cloning with $0 API fees:

- CyberMentor can deploy an open-weights neural voice cloner (such as **XTTS-v2** or **Kokoro**) directly inside the Google Cloud Run container.
- Simply upload a single 10-second reference audio clip (`island_boy_sample.wav`).
- The model generates all coach speech dynamically, saving thousands of dollars in annual TTS subscription costs while keeping full ownership of your AI voice profile!
