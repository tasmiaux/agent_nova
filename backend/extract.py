"""
Pull the owner's name and WhatsApp number out of a customer reply.

  - The LLM (Sarvam) finds the owner's name, translates the reply to English,
    and copies the number words exactly as spoken.
  - The number itself ALWAYS comes from phone_number.py, never from the LLM
    (LLMs mis-read spoken digits).
  - If the number is missing, partial or unclear, ask_again=True so Nova re-asks.
  - yes/no (for read-backs) and "wants a human" come from dialog.py rules.

    from extract import extract
    extract("मेरा नाम सुमन है", want=["owner"])
"""

import json
import re

import requests

import offline
from config import LLM_MODEL, LLM_URL, load_api_key
from dialog import wants_human, yes_no
from phone_number import complete_from_partial, find_phone_numbers

# Number-shaped text the LLM may write in its English line, e.g. "98450 12345" or "9845012345"
NUMBER_LIKE = re.compile(r"\+?\d[\d\s-]{5,14}\d")

SYSTEM_PROMPT = """You help Nova, an AI onboarding assistant for Supra AI (an AI WhatsApp
customer-support bot for small businesses). Nova is on a phone call with the owner of a
small business, setting up their WhatsApp support bot.
You get one reply from the customer (Hindi, Hinglish, Kannada or English).
Reply with JSON only, exactly these keys:
{
  "english": "the reply translated to natural English. Write [NUMBER] in place of a phone number spoken.",
  "owner_name": "the speaker's own name in Latin script (e.g. 'Suman'), or null if they don't say their name",
  "owner_name_native": "the same name copied EXACTLY as written in the reply, in the reply's script (e.g. 'सुमन' or 'ಸುಮನ್'), or null",
  "number_spoken": "the phone-number words copied EXACTLY as they appear in the reply, same script, or null"
}
Do not guess. If something is not said, use null."""


def ask_llm(transcript):
    """Send the transcript to Sarvam and return the parsed JSON dict."""
    if offline.is_on():  # demo mode: saved answer, no paid call
        return offline.ask_llm(transcript)
    response = requests.post(
        LLM_URL,
        headers={"api-subscription-key": load_api_key("SARVAM_API_KEY")},
        json={
            "model": LLM_MODEL,
            "reasoning_effort": None,          # thinking off: fast, and content is never empty
            "temperature": 0.1,
            "max_tokens": 500,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
        },
        timeout=30,
    )
    body = response.json()
    if not response.ok:
        raise RuntimeError(f"Sarvam error {response.status_code}: {body.get('error') or body}")
    content = body["choices"][0]["message"]["content"] or "{}"
    content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return json.loads(content)


def all_numbers(transcript, number_spoken, partial_number):
    """Numbers in the reply, best first. A partial from the previous turn
    is completed if this reply finishes it."""
    found = find_phone_numbers(transcript)
    if not found and number_spoken:
        found = find_phone_numbers(number_spoken)
    if partial_number and not any(n["status"] == "complete" for n in found):
        merged = complete_from_partial(partial_number, transcript)
        if merged:
            found = [merged]
    return found


def extract(transcript, want=("owner", "number"), partial_number=None):
    """Return {english, owner_name, owner_name_native, numbers, number, number_display, number_status,
    number_missing, confirm, wants_human, ask_again, missing}.
    want: which fields this turn asks for ([] for a yes/no read-back turn).
    partial_number: digits heard so far (e.g. "9845012"), so a follow-up
    like "three four five" can finish it."""
    confirm = yes_no(transcript)
    human = wants_human(transcript)

    # Read-back turn with a clear yes/no (or a human request): no LLM needed
    if (not want and confirm) or human:
        english = "I want to talk to a person." if human else {"yes": "Yes.", "no": "No."}[confirm]
        return {"english": english, "owner_name": None, "owner_name_native": None, "numbers": [], "number": None, "number_display": None,
                "number_status": "missing", "number_missing": 10, "confirm": confirm, "wants_human": human,
                "ask_again": False, "missing": []}

    llm = ask_llm(transcript)
    owner = (llm.get("owner_name") or "").strip() or None
    # Name as heard, in the customer's script (for the spoken read-back).
    # Only trusted if it really appears in the transcript; else fall back to Latin.
    native = (llm.get("owner_name_native") or "").strip() or None
    if not owner or (native and native not in transcript):
        native = None
    numbers = all_numbers(transcript, llm.get("number_spoken"), partial_number if "number" in want else None)
    best = numbers[0] if numbers else None

    english = llm.get("english") or ""
    english = english.replace("[NUMBER]", best["display"] if best else "(number unclear)")
    if best:
        # The LLM sometimes writes its own (wrong) digits; use the normalizer's answer
        english = NUMBER_LIKE.sub(best["display"], english)

    missing = []
    if "owner" in want and not owner:
        missing.append("owner")
    if "number" in want and not (best and best["status"] == "complete"):
        missing.append("number")

    return {
        "english": english,
        "owner_name": owner,
        "owner_name_native": native or owner,
        "numbers": numbers,
        "number": best["number"] if best else None,
        "number_display": best["display"] if best else None,
        "number_status": best["status"] if best else "missing",
        "number_missing": best["missing"] if best else 10,   # digits still needed (partial)
        "confirm": confirm,
        "wants_human": human,
        "ask_again": bool(missing),
        "missing": missing,
    }
