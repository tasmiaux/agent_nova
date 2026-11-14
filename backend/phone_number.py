"""
Phone number normalizer for Nova.

Gnani STT writes spoken numbers as words, e.g.
    "नाइन एट फ़ोर फ़ाइव ज़ीरो वन टू थ्री फ़ोर फ़ाइव"   ->  9845012345
    "nine eight double four five one two three four five" -> 9844512345
    "ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ..."                             -> Kannada digit words work too
    "೯೮೪೫೦ ೧೨೩೪೫"                                        -> Kannada numerals too

Main functions:
    find_phone_numbers(text) -> [{"number", "display", "status", "missing"}, ...]
        number   "9845012345" (digits only)
        display  "98450 12345"
        status   "complete" | "partial" (fewer than 10 digits) | "unclear"
        missing  how many digits are still needed (partial), else 0
    complete_from_partial(partial_digits, text) -> result or None
        finishes a partial number with the customer's follow-up

Valid Indian mobile numbers: 10 digits, first digit 6-9.
A leading +91 / 91 / 0 is removed.
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# Digit words (Hindi, English, Kannada; Devanagari/Kannada spellings are
# written without the nukta dot because clean() strips nuktas)
# ---------------------------------------------------------------------------
DIGITS = {
    "0": ["zero", "oh", "o", "shunya", "sunya", "sonne",
          "जीरो", "शून्य", "सून्य",
          "ಜೀರೋ", "ಜೀರೊ", "ಸೊನ್ನೆ", "ಶೂನ್ಯ"],
    "1": ["one", "ek", "ondu",
          "वन", "एक",
          "ವನ್", "ಒಂದು"],
    "2": ["two", "to", "too", "do", "eradu",
          "टू", "दो",
          "ಟು", "ಟೂ", "ಎರಡು"],
    "3": ["three", "tree", "teen", "mooru", "muru",
          "थ्री", "तीन",
          "ತ್ರೀ", "ಮೂರು"],
    "4": ["four", "for", "char", "chaar", "naalku", "nalku",
          "फोर", "फॉर", "चार",
          "ಫೋರ್", "ನಾಲ್ಕು"],
    "5": ["five", "paanch", "panch", "aidu", "aydu",
          "फाइव", "फाईव", "पांच", "पाँच",
          "ಫೈವ್", "ಐದು"],
    "6": ["six", "chhe", "chhah", "che", "aaru", "aru",
          "सिक्स", "छह", "छः", "छे",
          "ಸಿಕ್ಸ್", "ಆರು"],
    "7": ["seven", "saat", "elu", "yelu",
          "सेवन", "सात",
          "ಸೆವೆನ್", "ಸೆವನ್", "ಏಳು"],
    "8": ["eight", "aath", "aat", "entu", "yentu",
          "एट", "एइट", "आठ",
          "ಎಯ್ಟ್", "ಏಟ್", "ಎಂಟು"],
    "9": ["nine", "nau", "ombattu", "ombhattu",
          "नाइन", "नौ",
          "ನೈನ್", "ಒಂಬತ್ತು"],
}

# "double five" -> 55, "triple zero" -> 000 (Hindi and Kannada speakers use the English words)
REPEAT = {2: ["double", "dabal", "डबल", "ದಬಲ್", "ಡಬಲ್"], 3: ["triple", "tripal", "ट्रिपल", "ಟ್ರಿಪಲ್"]}

# Spoken two-digit groups people sometimes use ("ninety eight", "twelve")
TEENS = {"10": ["ten", "टेन"], "11": ["eleven", "इलेवन"], "12": ["twelve", "ट्वेल्व"], "13": ["thirteen"],
         "14": ["fourteen"], "15": ["fifteen"], "16": ["sixteen"], "17": ["seventeen"], "18": ["eighteen"],
         "19": ["nineteen"]}
TENS = {"2": ["twenty"], "3": ["thirty"], "4": ["forty"], "5": ["fifty"], "6": ["sixty"], "7": ["seventy"],
        "8": ["eighty"], "9": ["ninety", "नाइंटी"]}

# Words allowed inside a number without breaking it
FILLERS = {"dash", "hyphen", "plus", "प्लस"}


def _index(table):
    return {word: value for value, words in table.items() for word in words}


DIGIT_WORDS = _index(DIGITS)
REPEAT_WORDS = _index(REPEAT)
TEEN_WORDS = _index(TEENS)
TENS_WORDS = _index(TENS)


# Kannada (೦-೯) and Devanagari (०-९) numerals -> 0-9
NATIVE_DIGITS = str.maketrans("೦೧೨೩೪೫೬೭೮೯०१२३४५६७८९", "01234567890123456789")


def clean(text):
    """Lowercase, native numerals to 0-9, drop nukta dots, punctuation (। , . -) to spaces."""
    text = text.translate(NATIVE_DIGITS)
    text = unicodedata.normalize("NFD", text)
    text = text.replace("़", "")  # Devanagari nukta
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[।॥,.!?;:\-–—/()\"']", " ", text)
    return text.lower()


def word_to_digits(word, next_word=None):
    """One word -> (digits, words_used), or (None, 0) if it isn't part of a number."""
    if re.fullmatch(r"\+?\d+", word):
        return word.lstrip("+"), 1
    if word in DIGIT_WORDS:
        return DIGIT_WORDS[word], 1
    if word in REPEAT_WORDS and next_word is not None:
        nxt, used = word_to_digits(next_word)
        if nxt and len(nxt) == 1:
            return nxt * REPEAT_WORDS[word], 2
    if word in TEEN_WORDS:
        return TEEN_WORDS[word], 1
    if word in TENS_WORDS:
        if next_word in DIGIT_WORDS and DIGIT_WORDS[next_word] != "0":
            return TENS_WORDS[word] + DIGIT_WORDS[next_word], 2
        return TENS_WORDS[word] + "0", 1
    return None, 0


def digit_runs(text):
    """Runs of consecutive number words -> ["9845012345", ...]."""
    words = clean(text).split()
    runs, current, i = [], "", 0
    while i < len(words):
        nxt = words[i + 1] if i + 1 < len(words) else None
        digits, used = word_to_digits(words[i], nxt)
        if digits:
            current += digits
            i += used
        elif words[i] in FILLERS:
            i += 1
        else:
            if current:
                runs.append(current)
            current = ""
            i += 1
    if current:
        runs.append(current)
    return runs


def strip_prefix(digits):
    """Remove a country code or trunk prefix: +91 / 91 / 0."""
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    return digits


def display(digits):
    """9845012345 -> "98450 12345" (partials are shown as heard)."""
    return f"{digits[:5]} {digits[5:]}" if len(digits) > 5 else digits


def normalize(digits):
    """Check a run of digits. Returns {"number", "display", "status", "missing"}."""
    digits = strip_prefix(digits)
    if not digits:
        return None
    starts_ok = digits[0] in "6789"
    if len(digits) == 10 and starts_ok:
        status, missing = "complete", 0
    elif len(digits) < 10 and starts_ok:
        status, missing = "partial", 10 - len(digits)
    else:
        status, missing = "unclear", 0   # starts with 0-5, or too many digits
    return {"number": digits, "display": display(digits), "status": status, "missing": missing}


def find_phone_numbers(text):
    """All numbers in a transcript, best first (complete > partial > unclear, then longest).
    Runs of one or two digits are ignored ("दो गाड़ियाँ" is not a phone number)."""
    order = {"complete": 0, "partial": 1, "unclear": 2}
    results = [r for r in (normalize(run) for run in digit_runs(text) if len(run) >= 3) if r]
    return sorted(results, key=lambda r: (order[r["status"]], -len(r["number"])))


def complete_from_partial(partial, text):
    """Finish a partial number with the follow-up reply.
    E.g. partial "9845012" + reply "थ्री फ़ोर फ़ाइव" -> 9845012345.
    If the reply is a whole number on its own, that wins."""
    runs = digit_runs(text)
    if not runs or not partial:
        return None
    candidates = []
    for run in runs:
        candidates.append(run)            # the reply may be the full number again
        candidates.append(partial + run)  # or just the missing digits
    for c in candidates:
        r = normalize(c)
        if r and r["status"] == "complete":
            return r
    return None


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sample = " ".join(sys.argv[1:]) or "नाइन एट फ़ोर फ़ाइव ज़ीरो वन टू थ्री फ़ोर फ़ाइव"
    print(sample)
    for r in find_phone_numbers(sample):
        print(" ->", r["display"], f"({r['status']}, missing {r['missing']})")
