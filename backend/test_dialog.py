"""
Tests for dialog.py: handoff ("talk to a human") and yes/no detection.

Run:  python test_dialog.py
"""

import sys

from dialog import wants_human, yes_no

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HUMAN = [
    # the exact words Nova tells people to say
    ("human", True), ("Human please", True), ("ह्यूमन", True), ("ಹ್ಯೂಮನ್", True),
    # common variants and phrasings
    ("मुझे किसी इंसान से बात करनी है", True), ("एजेंट से बात कराइए", True), ("agent", True),
    ("I want to talk to an agent", True), ("ನನಗೆ ಮನುಷ್ಯರ ಜೊತೆ ಮಾತಾಡಬೇಕು", True), ("ಏಜೆಂಟ್ ಬೇಕು", True),
    ("ह्युमन", True), ("ಹ್ಯುಮನ್", True), ("insaan se baat karni hai", True),
    # must NOT trigger
    ("मेरा नाम सुमन है", False), ("ನನ್ನ ಹೆಸರು ಸುಮನ್", False), ("हाँ, सही है", False),
    ("नाइन एट फ़ोर फ़ाइव", False), ("ಹೌದು, ಸರಿ", False),
]

YES_NO = [
    ("हाँ, सही है।", "yes"), ("नहीं, गलत है।", "no"), ("ಹೌದು, ಸರಿ.", "yes"), ("ಇಲ್ಲ, ತಪ್ಪು.", "no"),
    ("yes", "yes"), ("no", "no"), ("ಸರಿ", "yes"), ("शायद", None),
]

passed = total = 0
for text, expected in HUMAN:
    total += 1
    got = wants_human(text)
    passed += got == expected
    print(f"[{'PASS' if got == expected else 'FAIL'}] human? {text!r} -> {got}")
for text, expected in YES_NO:
    total += 1
    got = yes_no(text)
    passed += got == expected
    print(f"[{'PASS' if got == expected else 'FAIL'}] yes/no {text!r} -> {got}")
print(f"\n{passed}/{total} passed")
sys.exit(0 if passed == total else 1)
