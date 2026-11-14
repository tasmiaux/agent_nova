"""
Tests for phone_number.py.

Run:  python test_phone_number.py
"""

import sys

from phone_number import complete_from_partial, find_phone_numbers

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (description, transcript, expected best number, expected status)
CASES = [
    ("English digits", "my number is nine eight four five zero one two three four five", "9845012345", "complete"),
    ("Hindi number words", "नौ आठ चार पाँच शून्य एक दो तीन चार पाँच", "9845012345", "complete"),
    ("English words in Devanagari (Gnani style)", "नाइन एट फ़ोर फ़ाइव ज़ीरो वन टू थ्री फ़ोर फ़ाइव", "9845012345", "complete"),
    ("Kannada digits", "ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ ಒಂದು ಎರಡು ಮೂರು ನಾಲ್ಕು ಐದು", "9845012345", "complete"),
    ("Mixed languages in one number", "nine एट ನಾಲ್ಕು five ज़ीरो one दो three ನಾಲ್ಕು पाँच", "9845012345", "complete"),
    ("Already written as digits", "मेरा नंबर 98450 12345 है", "9845012345", "complete"),
    ("double", "nine eight double four five one two three four five", "9844512345", "complete"),
    ("triple", "nine eight seven triple zero one two three four", "9870001234", "complete"),
    ("Hindi double (डबल)", "नाइन एट डबल फ़ोर फ़ाइव वन टू थ्री फ़ोर फ़ाइव", "9844512345", "complete"),
    ("+91 prefix removed", "plus nine one nine eight four five zero one two three four five", "9845012345", "complete"),
    ("Leading 0 removed", "zero nine eight four five zero one two three four five", "9845012345", "complete"),
    ("Partial: only 7 digits", "नाइन एट फ़ोर फ़ाइव ज़ीरो वन टू", "9845012", "partial"),
    ("Unclear: starts with 5", "five eight four five zero one two three four five", "5845012345", "unclear"),
    ("Unclear: too many digits", "nine eight four five zero one two three four five six seven", "984501234567", "unclear"),
    # --- Kannada ---
    ("Kannada numerals", "ನನ್ನ ನಂಬರ್ ೯೮೪೫೦ ೧೨೩೪೫", "9845012345", "complete"),
    ("Kannada numerals mixed with words", "೯೮೪೫೦ ಒಂದು ಎರಡು ಮೂರು ನಾಲ್ಕು ಐದು", "9845012345", "complete"),
    ("English digit words in Kannada script", "ನೈನ್ ಎಯ್ಟ್ ಫೋರ್ ಫೈವ್ ಜೀರೋ ವನ್ ಟು ತ್ರೀ ಫೋರ್ ಫೈವ್", "9845012345", "complete"),
    ("Kannada ಡಬಲ್", "ಒಂಬತ್ತು ಎಂಟು ಡಬಲ್ ನಾಲ್ಕು ಐದು ಒಂದು ಎರಡು ಮೂರು ನಾಲ್ಕು ಐದು", "9844512345", "complete"),
    ("Kannada ಟ್ರಿಪಲ್", "ಒಂಬತ್ತು ಎಂಟು ಏಳು ಟ್ರಿಪಲ್ ಸೊನ್ನೆ ಒಂದು ಎರಡು ಮೂರು ನಾಲ್ಕು", "9870001234", "complete"),
    ("Kanglish mix (Kannada + English + Latin)", "ನಂಬರ್ nine ಎಂಟು ನಾಲ್ಕು five ಸೊನ್ನೆ ವನ್ two ಮೂರು ಫೋರ್ ಐದು", "9845012345", "complete"),
    ("Kannada partial", "ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ ಒಂದು ಎರಡು", "9845012", "partial"),
    ("Kannada unclear (starts with 4)", "ನಾಲ್ಕು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ ಒಂದು ಎರಡು ಮೂರು ನಾಲ್ಕು ಐದು", "4845012345", "unclear"),
    ("Devanagari numerals", "नंबर ९८४५० १२३४५ है", "9845012345", "complete"),
    ("No number in the sentence", "हाँ जी, बोलिए", None, None),
    ("No number (Kannada)", "ಹೇಳಿ, ಹೇಳಿ", None, None),
    ("Small counts are not numbers", "हमारे पास दो दुकानें हैं", None, None),
]

# (description, partial digits, follow-up reply, expected completed number)
FOLLOW_UPS = [
    ("Remaining 3 digits", "9845012", "थ्री फ़ोर फ़ाइव", "9845012345"),
    ("Whole number repeated", "9845012", "nine eight four five zero one two three four five", "9845012345"),
    ("Still not enough", "9845012", "थ्री", None),
    ("Kannada remaining digits", "9845012", "ಮೂರು ನಾಲ್ಕು ಐದು", "9845012345"),
    ("Kannada numerals as the rest", "9845012", "೩೪೫", "9845012345"),
]

passed = total = 0
for name, text, number, status in CASES:
    total += 1
    found = find_phone_numbers(text)
    best = found[0] if found else None
    ok = (best["number"] if best else None) == number and (best["status"] if best else None) == status
    passed += ok
    got = f'{best["display"]} ({best["status"]})' if best else "(no number)"
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {got}" + ("" if ok else f"   expected {number} ({status})"))

for name, partial, reply, expected in FOLLOW_UPS:
    total += 1
    r = complete_from_partial(partial, reply)
    got = r["number"] if r else None
    ok = got == expected
    passed += ok
    print(f"[{'PASS' if ok else 'FAIL'}] follow-up: {name}: {partial} + \"{reply}\" -> {got}" + ("" if ok else f"   expected {expected}"))

print(f"\n{passed}/{total} passed")
sys.exit(0 if passed == total else 1)
