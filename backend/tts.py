"""
Gnani text-to-speech for the Nova app.

    from tts import speak
    wav_bytes = speak("नमस्ते सुमन जी", voice="customer")      # Nalini, Hindi
    wav_bytes = speak("All five items are verified.", voice="founder")  # Avinash, English

Docs: https://docs.gnani.ai/api/TTS/tts-inference.md
"""

import hashlib
import time
from pathlib import Path

import requests

import offline
from config import TTS_URL, TTS_VOICES, load_api_key

CACHE_DIR = Path(__file__).resolve().parent / "tts_cache"


def fix_wav_header(data):
    """Gnani sends a 'streaming' WAV header with placeholder sizes (0xFFFFFFFF),
    so players show a wrong length. Write the real sizes into the header."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return data
    pos = data.find(b"data", 12)
    if pos == -1:
        return data
    fixed = bytearray(data)
    fixed[4:8] = (len(data) - 8).to_bytes(4, "little")                    # RIFF chunk size
    fixed[pos + 4:pos + 8] = (len(data) - pos - 8).to_bytes(4, "little")  # data chunk size
    return bytes(fixed)


def synthesize(text, model, voice, language="hi-IN", api_key=None, sample_rate=24000, retry=True):
    """Call Gnani TTS and return WAV bytes. Retries once on 429/5xx (unless retry=False)."""
    payload = {
        "text": text,
        "model": model,
        "voice": voice,
        "language": language,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": sample_rate,
            "num_channels": 1,
            "sample_width": 2,      # 16-bit
            "encoding": "linear_pcm",
            "container": "wav",
        },
    }
    headers = {"Content-Type": "application/json", "X-API-Key-ID": api_key or load_api_key()}
    for attempt in range(2 if retry else 1):
        response = requests.post(TTS_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("audio"):
            return fix_wav_header(response.content)
        # 429 = one request at a time on some accounts; 5xx = temporary
        if response.status_code in (429, 500, 503, 504) and attempt == 0:
            time.sleep(1.5)
            continue
        raise RuntimeError(f"Gnani TTS error {response.status_code}: {response.text[:300]}")


def speak(text, voice="customer"):
    """Text -> WAV bytes using one of Nova's voices (see TTS_VOICES in config.py).
    Results are cached on disk, so repeated lines (greetings) are instant and free."""
    if voice not in TTS_VOICES:
        raise ValueError(f"voice must be one of {list(TTS_VOICES)}")
    model, voice_name, language = TTS_VOICES[voice]
    key = hashlib.sha256(f"{model}|{voice_name}|{language}|{text}".encode("utf-8")).hexdigest()[:20]
    cached = CACHE_DIR / f"{key}.wav"
    if cached.exists():
        return cached.read_bytes()
    if offline.is_on() or offline.dry_run_flag():  # demo mode / DRY_RUN: never call Gnani
        legacy = offline.legacy_cache_path(text, model, voice_name)
        return legacy.read_bytes() if legacy.exists() else offline.silent_wav()
    # Founder report: exactly one paid call, no retry (cached by the text hash above)
    audio = synthesize(text, model, voice_name, language=language, retry=(voice != "founder"))
    CACHE_DIR.mkdir(exist_ok=True)
    cached.write_bytes(audio)
    return audio
