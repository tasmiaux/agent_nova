"""
Offline demo mode: run Nova with NO paid API calls (no Gnani, no Sarvam).

Turn it on with any of:
    the Live / Offline switch in the page header
    python app.py --offline
    DRY_RUN=true in nova-ai/.env.local
    DRY_RUN=1 environment variable

What happens instead of paid calls:
  - Speech-to-text: the demo customer sends each reply as a scripted line
    (SCRIPTED below). If you've recorded the matching audio in
    test_audio/demo/<hi|kn>/, the page plays it so you hear the customer, but the
    transcript still comes from the script (no paid STT).
    Unknown audio with no script line -> empty transcript ("Couldn't hear that").
  - Extraction (Sarvam): saved answers for the scripted lines, or a simple
    name rule ("मेरा नाम X है") for anything else. Numbers always go
    through phone_number.py, which is free.
  - Text-to-speech: audio already saved in tts_cache/ is replayed. A line that
    was never generated plays a short silence instead (its text still shows).
  - Command routing: keyword rules only.
The mock Supra AI platform is local, so it works the same as always.
"""

import hashlib
import io
import os
import re
import wave
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
TEST_AUDIO_DIR = BACKEND_DIR.parent / "test_audio"
TTS_CACHE_DIR = BACKEND_DIR / "tts_cache"

_forced = None  # set by app.py --offline or the page switch


def enable(on=True):
    """Turn offline mode on/off at runtime (the page's Live / Offline switch)."""
    global _forced
    _forced = bool(on)


def dry_run_flag():
    """True when DRY_RUN is set (env var or nova-ai/.env.local). Unlike is_on(),
    the page's Live/Offline toggle cannot override this: it always blocks paid calls."""
    if os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes"):
        return True
    env_file = BACKEND_DIR.parent / ".env.local"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DRY_RUN="):
                return line.split("=", 1)[1].strip().strip("\"'").lower() in ("1", "true", "yes")
    return False


def is_on():
    """True when offline mode is on (flag, env var, or DRY_RUN in .env.local)."""
    if _forced is not None:
        return _forced
    return dry_run_flag()


# ---------------------------------------------------------------------------
# Scripted lines the offline demo customer "says" (transcript -> what the
# extraction step returns for it). The page's OFFLINE_SCRIPT uses these.
# ---------------------------------------------------------------------------
SCRIPTED = {
    "हाँ जी, बोलिए।": {"english": "Yes, go ahead.", "owner_name": None},
    # Nova mishears the name on purpose (shows the read-back catching it)
    "मेरा नाम सुमित है।": {"english": "My name is Sumit.", "owner_name": "Sumit", "owner_name_native": "सुमित"},
    "नहीं, गलत है।": {"english": "No, that's wrong.", "owner_name": None},
    "मेरा नाम सुमन है।": {"english": "My name is Suman.", "owner_name": "Suman", "owner_name_native": "सुमन"},
    "हाँ, सही है।": {"english": "Yes, that's right.", "owner_name": None},
    "मेरा व्हाट्सऐप नंबर है नाइन एट फ़ोर फ़ाइव ज़ीरो वन टू।":
        {"english": "My WhatsApp number is [NUMBER].", "owner_name": None},
    "थ्री फ़ोर फ़ाइव।": {"english": "Three four five.", "owner_name": None},
    "हाँ।": {"english": "Yes.", "owner_name": None},
    "मुझे किसी इंसान से बात करनी है।": {"english": "I want to talk to a person.", "owner_name": None},
    # Kannada demo customer
    "ಹೇಳಿ, ಹೇಳಿ.": {"english": "Yes, go ahead.", "owner_name": None},
    "ನನ್ನ ಹೆಸರು ಸುಮಿತ್.": {"english": "My name is Sumit.", "owner_name": "Sumit", "owner_name_native": "ಸುಮಿತ್"},
    "ಇಲ್ಲ, ತಪ್ಪು.": {"english": "No, that's wrong.", "owner_name": None},
    "ನನ್ನ ಹೆಸರು ಸುಮನ್.": {"english": "My name is Suman.", "owner_name": "Suman", "owner_name_native": "ಸುಮನ್"},
    "ಹೌದು, ಸರಿ.": {"english": "Yes, that's right.", "owner_name": None},
    "ನನ್ನ ವಾಟ್ಸಾಪ್ ನಂಬರ್ ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ ಒಂದು ಎರಡು.":
        {"english": "My WhatsApp number is [NUMBER].", "owner_name": None},
    "ಮೂರು ನಾಲ್ಕು ಐದು.": {"english": "Three four five.", "owner_name": None},
    "ಹೌದು.": {"english": "Yes.", "owner_name": None},
    "ನನಗೆ ಮನುಷ್ಯರ ಜೊತೆ ಮಾತಾಡಬೇಕು.": {"english": "I want to talk to a person.", "owner_name": None},
}

# Recordings matched by their exact audio bytes -> saved Gnani transcript.
# Empty for the Supra AI demo until real recordings have been transcribed once
# in Live mode; add {"file name": {"transcript", "english", "owner_name", "language"}}.
RECORDINGS = {}


def legacy_cache_path(text, model="timbre-v2.5", voice="Nalini"):
    """tts_cache file name used before the language was added to the key."""
    key = hashlib.sha256(f"{model}|{voice}|{text}".encode("utf-8")).hexdigest()[:20]
    return TTS_CACHE_DIR / f"{key}.wav"


_by_hash = None


def _audio_index():
    """sha256(audio bytes) -> saved result, built once."""
    global _by_hash
    if _by_hash is None:
        _by_hash = {}
        for name, data in RECORDINGS.items():
            path = TEST_AUDIO_DIR / name
            if path.exists():
                _by_hash[hashlib.sha256(path.read_bytes()).hexdigest()] = data
    return _by_hash


def transcribe(audio_bytes):
    """Saved transcript for known audio, else ""."""
    return transcribe_full(audio_bytes)[0]


def transcribe_full(audio_bytes):
    """(transcript, language code) for known audio, else ("", None)."""
    hit = _audio_index().get(hashlib.sha256(audio_bytes).hexdigest())
    return (hit["transcript"], hit.get("language", "hi-IN")) if hit else ("", None)


def ask_llm(transcript):
    """Same shape as extract.ask_llm(): {english, owner_name, owner_name_native, number_spoken}."""
    for data in RECORDINGS.values():
        if data["transcript"] == transcript:
            return {"english": data["english"], "owner_name": data.get("owner_name"),
                    "owner_name_native": data.get("owner_name_native"), "number_spoken": None}
    if transcript in SCRIPTED:
        return {**SCRIPTED[transcript], "number_spoken": None}
    # Unknown text: simple rule for "मेरा नाम X है" / "mera naam X hai"
    m = re.search(r"(?:मेरा|mera)\s+(?:नाम|naam|name)\s+(.+?)\s+(?:है|hai)", transcript, re.I) \
        or re.search(r"ನನ್ನ\s+ಹೆಸರು\s+([^\s.]+)", transcript)
    name = m.group(1) if m else None
    return {"english": "(offline demo: no translation)", "owner_name": name, "owner_name_native": name, "number_spoken": None}


def silent_wav(seconds=0.8, rate=24000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return buf.getvalue()
