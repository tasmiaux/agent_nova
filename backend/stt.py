"""
Gnani speech-to-text for the Nova app, using the locked settings in config.py.

    from stt import transcribe
    text = transcribe("recording.aac", speech="hinglish")   # or "hindi"
"""

from pathlib import Path

import requests

import offline
from config import STT_SETTINGS, STT_URL, load_api_key

# Formats the Gnani REST docs accept directly (detected from the extension)
MIME_TYPES = {
    ".wav": "audio/wav", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
    ".flac": "audio/flac", ".aac": "audio/aac", ".m4a": "audio/mp4",
}


def transcribe(audio_path, speech="hinglish", api_key=None):
    """Return just the transcript (see transcribe_full for the language too)."""
    return transcribe_full(audio_path, speech, api_key)[0]


def transcribe_full(audio_path, speech="hinglish", api_key=None):
    """Return (transcript, detected language code) for one audio file (max 30 s, mono).
    speech: "hinglish", "hindi", or "digits" for phone numbers
    (see STT_SETTINGS in config.py)."""
    audio_path = Path(audio_path)
    mime = MIME_TYPES.get(audio_path.suffix.lower())
    if mime is None:
        raise ValueError(f"Unsupported audio format {audio_path.suffix}; convert to .wav first")
    if speech not in STT_SETTINGS:
        raise ValueError(f"speech must be one of {list(STT_SETTINGS)}")
    if offline.is_on():  # demo mode: saved transcript, no paid call
        return offline.transcribe_full(audio_path.read_bytes())

    with open(audio_path, "rb") as f:
        response = requests.post(
            STT_URL,
            headers={"X-API-Key-ID": api_key or load_api_key()},
            files={"audio_file": (audio_path.name, f, mime)},
            data=STT_SETTINGS[speech],
            timeout=60,
        )
    body = response.json()
    if not response.ok or body.get("success") is False:
        raise RuntimeError(f"Gnani STT error {response.status_code}: {body.get('error') or body}")
    # Gnani reports the detected language; fall back to the first requested one
    language = body.get("detected_language_code") or STT_SETTINGS[speech]["language_code"].split(",")[0]
    return body.get("transcript", ""), language
