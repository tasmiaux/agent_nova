"""
Small, free (no API) rules used on every customer reply:

    yes_no(text)                 -> "yes" | "no" | None   (Hindi, Hinglish, English)
    wants_human(text)            -> True if the customer asks for a person
    language_label(code, text)   -> {"code": "hi-IN", "label": "Hinglish"}

They run the same way in Live and Offline mode.
"""

import re

# Whole-word matches. Order matters: "no" phrases are checked first so
# "नहीं, सही नहीं है" is a no even though it contains "सही".
NO_WORDS = ["नहीं", "नही", "ना", "गलत", "ग़लत", "no", "nahi", "nahin", "nope", "galat", "wrong", "incorrect",
            "ಇಲ್ಲ", "ಇಲ್ಲಾ", "ತಪ್ಪು", "ಬೇಡ", "illa", "tappu"]
YES_WORDS = ["हाँ", "हां", "हा", "जी", "सही", "ठीक", "बिल्कुल", "बिलकुल", "हाँजी",
             "yes", "haan", "han", "ha", "ji", "sahi", "theek", "thik", "correct", "right", "ok", "okay", "yeah", "yep",
             "ಹೌದು", "ಹೌದ್", "ಸರಿ", "ಹೂಂ", "ಓಕೆ", "houdu", "sari"]

# Includes the exact word Nova tells people to say ("human" / ह्यूमन / ಹ್ಯೂಮನ್)
# plus common spellings STT may produce for it.
HUMAN_PATTERNS = [
    r"\bhuman\b", r"\bhumen\b", r"\bperson\b", r"\bagent\b", r"\breal person\b", r"\bsomeone\b",
    r"ह्यूमन", r"ह्युमन", r"ह्यूमैन", r"इंसान", r"इन्सान", r"एजेंट", r"एजेन्ट", r"मानव", r"आदमी से",
    r"किसी से बात", r"कस्टमर केयर", r"टीम से बात",
    r"\binsaan\b", r"\binsan\b", r"\baadmi\b",
    r"ಹ್ಯೂಮನ್", r"ಹ್ಯುಮನ್", r"ಮನುಷ್ಯ", r"ಏಜೆಂಟ್", r"ಏಜೆಂಟ", r"\bmanushya\b",
]


def _words(text):
    text = re.sub(r"[।॥,.!?;:\"'()\-]", " ", text.lower())
    return text.split()


def yes_no(text):
    words = _words(text)
    if not words:
        return None
    if any(w in NO_WORDS for w in words):
        return "no"
    if any(w in YES_WORDS for w in words):
        return "yes"
    return None


def wants_human(text):
    t = text.lower()
    return any(re.search(p, t) for p in HUMAN_PATTERNS)


LABELS = {"hi-IN": "Hindi", "kn-IN": "Kannada", "en-IN": "English", "ta-IN": "Tamil", "te-IN": "Telugu",
          "mr-IN": "Marathi", "bn-IN": "Bengali", "gu-IN": "Gujarati", "ml-IN": "Malayalam", "pa-IN": "Punjabi"}


def script_language(text, default="hi-IN"):
    """Language from the script used: Kannada script -> kn-IN, Devanagari -> hi-IN."""
    if re.search(r"[\u0C80-\u0CFF]", text or ""):
        return "kn-IN"
    if re.search(r"[\u0900-\u097F]", text or ""):
        return "hi-IN"
    return default


def language_label(code, text=""):
    """Speech that mixes in English words (in Latin letters) is shown as Hinglish / Kanglish."""
    code = (code or "hi-IN").split(",")[0]
    mixed = re.search(r"[A-Za-z]{3,}", text or "")
    if code == "hi-IN" and mixed:
        return {"code": code, "label": "Hinglish"}
    if code == "kn-IN" and mixed:
        return {"code": code, "label": "Kanglish"}
    return {"code": code, "label": LABELS.get(code, code)}
