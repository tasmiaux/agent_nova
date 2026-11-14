"""
Nova backend config: API key loading and the LOCKED Gnani settings.

Change settings here only, so the app and the test scripts stay in sync.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR.parent / ".env.local"  # nova-ai/.env.local holds the keys

# ---------- Gnani STT (Prisma) ----------
# Docs: https://docs.gnani.ai/api/STT/speech-to-text.md
STT_URL = "https://api.vachana.ai/stt/v3"
STT_MODEL = "prisma-v3.0"

# Locked after the 2026-11-11 test (see test_results.md):
#  - Hinglish: hi-IN,en-IN + codemix keeps English words in Latin script,
#    which is easier to process.
#  - Hindi: hi-IN gives digits ("15") instead of number words.
#  - Digits: plain hi-IN converts numbers itself and can drop or merge spoken
#    characters. verbatim keeps every spoken word ("नाइन एट फ़ोर ..."), which
#    phone_number.py turns into 9845012345. Use "digits" when Nova asks for a
#    phone number.
STT_SETTINGS = {
    "hinglish": {"model": STT_MODEL, "language_code": "hi-IN,en-IN", "format": "codemix"},
    "hindi": {"model": STT_MODEL, "language_code": "hi-IN"},
    "digits": {"model": STT_MODEL, "language_code": "hi-IN", "format": "verbatim"},
    # Kannada (checked 2026-11-12 with kn-IN audio): codemix keeps English words
    # like "WhatsApp" in Latin; verbatim keeps digits as Kannada words.
    "kanglish": {"model": STT_MODEL, "language_code": "kn-IN,en-IN", "format": "codemix"},
    "digits_kn": {"model": STT_MODEL, "language_code": "kn-IN", "format": "verbatim"},
}

# ---------- Demo customer ----------
# preferred_language is per customer so Kannada (kn-IN) can plug in later.
# The owner is not fixed here: Nova saves the name confirmed on the call to the account.
CUSTOMER = {"id": "CUS-0142", "name": "Kaveri Handlooms", "preferred_language": "hi-IN"}

# ---------- Gnani TTS (Timbre) ----------
# Docs: https://docs.gnani.ai/api/TTS/tts-inference.md
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"
# voice role -> (model, voice name, language)
TTS_VOICES = {
    "customer": ("timbre-v2.5", "Nalini", "hi-IN"),      # Nova asking the customer, in Hindi/Hinglish
    "customer_kn": ("timbre-v3.0", "Lakshmi", "kn-IN"),  # Nova asking the customer, in Kannada/Kanglish
    "founder": ("timbre-v3.0", "Avinash", "en-IN"),      # reports back to the founder, in English
}

# ---------- Stage 2: mock customer system (started by app.py) ----------
CUSTOMER_ID = "CUS-0142"
MOCK_PORT = 8001
MOCK_URL = f"http://127.0.0.1:{MOCK_PORT}"

# ---------- Sarvam LLM (field extraction + English translation) ----------
# Docs: https://docs.sarvam.ai/api-reference/chat/chat-completions-v1.md
# Tested 2026-11-11: -conversations model with reasoning off answers in ~0.5 s.
LLM_URL = "https://api.sarvam.ai/v1/chat/completions"
LLM_MODEL = "sarvam-105b-conversations"


def load_api_key(name="GNANI_API_KEY"):
    """Read a key from nova-ai/.env.local (simple KEY=VALUE parser, no extra library)."""
    if not ENV_FILE.exists():
        sys.exit(f"Missing {ENV_FILE}. Create it with a line: {name}=your-key")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(name + "="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            if key:
                return key
    sys.exit(f"{name} is empty or missing in {ENV_FILE}.")
