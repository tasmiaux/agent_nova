"""
Nova's brain for the Supra AI demo: understand a command, build the onboarding
plan, and verify items for real against the mock Supra AI platform (HTTP).

    classify_command(text)              -> {"intent", "reply"}
    build_plan()                        -> checklist + real account check + engineer task
    run_verification(owner, number)     -> 5 checks + per-item Verified / Blocked
    summary_text(owner, number, ...)    -> English founder report (Avinash reads it)
"""

import json
import time
from datetime import datetime

import requests

import offline
from config import CUSTOMER, CUSTOMER_ID, LLM_MODEL, LLM_URL, MOCK_URL, load_api_key
from phone_number import display

LANG_NAMES = {"hi-IN": "Hindi", "en-IN": "English", "kn-IN": "Kannada"}

# ---------------------------------------------------------------------------
# Checklist Nova builds when asked to onboard the customer
# ---------------------------------------------------------------------------
CHECKLIST = [
    {"id": "account", "icon": "building", "title": "Account created",
     "desc": "Supra AI workspace for Kaveri Handlooms", "owner": "Nova"},
    {"id": "owner", "icon": "user", "title": "Owner details",
     "desc": "Owner's name and contact, captured on the call", "owner": "Customer"},
    {"id": "number", "icon": "phone", "title": "WhatsApp number",
     "desc": "The number the bot will answer on", "owner": "Customer"},
    {"id": "testchat", "icon": "message", "title": "Test chat",
     "desc": "Nova chats with the bot and checks the reply", "owner": "Engineer"},
    {"id": "training", "icon": "calendar", "title": "Training scheduled",
     "desc": "Nova confirms the booking on the CSM calendar", "owner": "CSM"},
]

ENGINEER_TASK = {
    "title": "Connect Kaveri Handlooms' WhatsApp number and upload their FAQ documents, then mark done.",
    "endpoints": ["POST /channels/whatsapp", f"POST /kb/{CUSTOMER_ID}/upload"],
    "base_url": MOCK_URL,
}

# What Nova asks the bot in the test chat, in the customer's language
TEST_MESSAGE = {"hi-IN": "क्या आपके पास कॉटन साड़ियाँ हैं? कीमत क्या है?",
                "kn-IN": "ನಿಮ್ಮ ಹತ್ತಿರ ಕಾಟನ್ ಸೀರೆ ಇದೆಯಾ? ಬೆಲೆ ಎಷ್ಟು?"}


# ---------------------------------------------------------------------------
# HTTP helpers: every check records a one-line technical proof
# ---------------------------------------------------------------------------
def http(method, path, body=None):
    """Call the mock platform. Returns (status_code or None, json or None, proof line)."""
    start = time.perf_counter()
    try:
        r = requests.request(method, MOCK_URL + path, json=body, timeout=5)
        ms = round((time.perf_counter() - start) * 1000)
        try:
            data = r.json()
        except ValueError:
            data = None
        return r.status_code, data, f"{method} {path} → {r.status_code} · {ms} ms"
    except requests.RequestException:
        ms = round((time.perf_counter() - start) * 1000)
        return None, None, f"{method} {path} → no response · {ms} ms"


def check(name, ok, plain, proof, detail=""):
    """One verification check. plain = the sentence people read first;
    proof = the technical line shown on expand."""
    return {"name": name, "ok": ok, "plain": plain, "proof": proof, "detail": detail}


# ---------------------------------------------------------------------------
# Commands ("Ask Nova")
# ---------------------------------------------------------------------------
INTENTS = ("onboard", "call", "verify", "summary")

COMMAND_PROMPT = """You route commands for Nova, the AI onboarding assistant of Supra AI (an AI WhatsApp
customer-support bot). The current customer is Kaveri Handlooms, a saree brand in Mysuru.
The user types or speaks a command (English, Hindi or Hinglish). Pick ONE intent:
- "onboard": start / set up / build the onboarding plan or checklist for the customer
- "call": phone the owner to collect their name and the WhatsApp number for the bot
- "verify": run or retry verification, the bot test chat, or check everything
- "summary": give a status summary or report
- "unknown": anything else
Reply with JSON only: {"intent": "...", "reply": "one short sentence in English saying what Nova will do"}"""

KEYWORDS = (
    ("call", ["call", "phone", "ring", "owner", "suman", "कॉल", "फ़ोन", "फोन"]),
    ("verify", ["verify", "test", "check", "retry", "test chat", "bot test", "जांच", "टेस्ट"]),
    ("summary", ["summary", "summar", "status", "report", "सारांश"]),
    ("onboard", ["onboard", "start", "set up", "setup", "begin", "plan", "kaveri", "शुरू"]),
)


def classify_command(text):
    """Map a free-text command to an intent. Uses Sarvam, falls back to keywords."""
    try:
        if offline.is_on():
            raise RuntimeError("offline demo: keywords only")
        r = requests.post(
            LLM_URL,
            headers={"api-subscription-key": load_api_key("SARVAM_API_KEY")},
            json={"model": LLM_MODEL, "reasoning_effort": None, "temperature": 0, "max_tokens": 120,
                  "response_format": {"type": "json_object"},
                  "messages": [{"role": "system", "content": COMMAND_PROMPT},
                               {"role": "user", "content": text}]},
            timeout=15,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"] or "{}"
        data = json.loads(content.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
        if data.get("intent") in INTENTS + ("unknown",):
            return {"intent": data["intent"], "reply": data.get("reply") or ""}
    except Exception:
        pass  # fall back to keywords below
    t = text.lower()
    for intent, words in KEYWORDS:
        if any(w in t for w in words):
            return {"intent": intent, "reply": ""}
    return {"intent": "unknown", "reply": ""}


# ---------------------------------------------------------------------------
# Plan: build the checklist and verify the account for real
# ---------------------------------------------------------------------------
def build_plan():
    code, body, proof = http("GET", f"/accounts/{CUSTOMER_ID}")
    if code == 200 and body and body.get("status") == "active":
        account = {"status": "verified", "plain": f"Account found and active ({body['plan']} plan)", "proof": proof}
    elif code is None:
        account = {"status": "blocked", "reason": "Supra AI platform not reachable", "plain": "Couldn't reach the platform",
                   "proof": proof}
    else:
        account = {"status": "blocked", "reason": f"Account {CUSTOMER_ID} not found",
                   "plain": "Account not found on the platform", "proof": proof}
    return {"items": CHECKLIST, "account": account, "engineer_task": ENGINEER_TASK}


# ---------------------------------------------------------------------------
# Verification against the Supra AI platform
# ---------------------------------------------------------------------------
def _same_person(reported, recorded):
    """'Suman' matches 'Suman Rao'; case and extra spaces ignored."""
    a, b = (reported or "").lower().split(), (recorded or "").lower().split()
    return bool(a and b) and (set(a) <= set(b) or set(b) <= set(a) or a[0] == b[0])


def run_verification(owner, number):
    """Five checks against the platform. Returns
    {checks, items: {id: {status, plain, proof, reason?}}, outcome, reason,
     reasons, engineer_message, ran_at}."""
    checks, items = [], {}
    shown = display(number) if number else "—"

    # 1. Platform reachable
    code, _, proof = http("GET", "/health")
    reachable = code == 200
    checks.append(check("platform", reachable,
                        "Platform reachable" if reachable else "Platform not reachable", proof))

    # Account (expected language + owner on record)
    _, account, account_proof = http("GET", f"/accounts/{CUSTOMER_ID}")
    account = account or {}
    expected = account.get("preferred_language") or CUSTOMER["preferred_language"]
    expected_name = LANG_NAMES.get(expected, expected)

    # 2. WhatsApp number connected
    code, _, num_proof = http("GET", f"/channels/whatsapp/{number}") if reachable else (None, None, "skipped")
    connected = code == 200
    checks.append(check("whatsapp", connected,
                        f"WhatsApp number {shown} connected" if connected else f"WhatsApp number {shown} not connected",
                        num_proof))

    # 3. FAQ documents indexed
    code, kb, kb_proof = http("GET", f"/kb/{CUSTOMER_ID}") if reachable else (None, None, "skipped")
    docs = (kb or {}).get("indexed", 0)
    checks.append(check("faq", docs > 0,
                        f"{docs} FAQ documents indexed" if docs else "No FAQ documents indexed", kb_proof))

    # 4. Test reply in the customer's language
    message = TEST_MESSAGE.get(expected, TEST_MESSAGE["hi-IN"])
    code, chat, chat_proof = http("POST", "/test-chat", {"account": CUSTOMER_ID, "message": message}) \
        if reachable else (None, None, "skipped")
    reply_lang = (chat or {}).get("language")
    reply_ok = code == 200 and reply_lang == expected and docs > 0
    reply_name = LANG_NAMES.get(reply_lang, reply_lang or "?")
    if code != 200:
        plain = "Test chat failed"
    elif reply_lang != expected:
        plain = f"Bot replied in {reply_name}, but the customer expects {expected_name}"
    elif docs == 0:
        plain = "Bot couldn't answer: no FAQ documents"
    else:
        plain = f"Test reply came in {expected_name}"
    checks.append(check("testchat", reply_ok, plain, chat_proof, (chat or {}).get("reply", "")))

    # 5. Training booked
    code, events, cal_proof = http("GET", f"/calendar/events?customer={CUSTOMER_ID}")
    booked = code == 200 and bool(events)
    when = ""
    if booked:
        when = datetime.fromisoformat(events[0]["start"]).strftime("%a %d %b, %I:%M %p").replace(" 0", " ")
    checks.append(check("training", booked, f"Training booked for {when}" if booked else "No training booked", cal_proof))

    # ---- checks -> checklist results ----
    if account:
        if _same_person(owner, account.get("owner")):
            items["owner"] = {"status": "verified", "plain": f"{owner} matches the account owner", "proof": account_proof}
        else:
            items["owner"] = {"status": "blocked", "reason": f"Name on the call ({owner}) doesn't match the account owner",
                              "plain": "Owner name doesn't match the account", "proof": account_proof}
    items["number"] = ({"status": "verified", "plain": checks[1]["plain"], "proof": num_proof} if connected else
                       {"status": "blocked", "reason": f"WhatsApp number {shown} is not connected to the bot",
                        "plain": checks[1]["plain"], "proof": num_proof})
    if reply_ok:
        items["testchat"] = {"status": "verified", "plain": checks[3]["plain"], "proof": f"{kb_proof}; {chat_proof}"}
    else:
        reasons = []
        if reply_lang and reply_lang != expected:
            reasons.append(f"Bot replied in {reply_name}, but the customer expects {expected_name}.")
        if docs == 0:
            reasons.append("No FAQ documents are indexed.")
        items["testchat"] = {"status": "blocked", "reason": " ".join(reasons) or "Test chat failed.",
                             "plain": checks[3]["plain"], "proof": f"{kb_proof}; {chat_proof}"}
    items["training"] = ({"status": "verified", "plain": f"Booked for {when}", "proof": cal_proof} if booked else
                         {"status": "blocked", "reason": "No training booked on the CSM calendar",
                          "plain": "No booking found", "proof": cal_proof})

    # Short, specific reasons (banner) + one message to the engineer
    short = []
    problems = []
    if not reachable:
        short.append("Platform unreachable")
        problems.append("the Supra AI platform is not reachable")
    if reachable and not connected:
        short.append("Number not connected")
        problems.append("the WhatsApp number is not connected")
    if reachable and docs == 0:
        short.append("No FAQ documents")
        problems.append("no FAQ documents are indexed")
    if reply_lang and reply_lang != expected:
        short.append(f"Bot replies in {reply_name}, customer expects {expected_name}")
        problems.append(f"the test reply came in {reply_name}")
    engineer_message = ""
    if problems:
        joined = problems[0] if len(problems) == 1 else ", ".join(problems[:-1]) + " and " + problems[-1]
        fix = {1: "fix it", 2: "fix both"}.get(len(problems), "fix these")
        engineer_message = f"{joined[0].upper()}{joined[1:]}. Please {fix} and mark done again."
    if items.get("owner", {}).get("status") == "blocked":
        short.append("Owner name doesn't match")
    if not booked:
        short.append("No training booked")

    blocked_items = [items[k]["reason"] for k in ("number", "testchat", "owner", "training")
                     if k in items and items[k]["status"] == "blocked"]
    return {
        "checks": checks,
        "items": items,
        "outcome": "blocked" if blocked_items else "verified",
        "reason": blocked_items[0] if blocked_items else "",
        "reasons": short,
        "engineer_message": engineer_message,
        "ran_at": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# Founder report (read in ENGLISH by the founder voice, Avinash)
# ---------------------------------------------------------------------------
ITEM_NAMES = {
    "account": "account",
    "owner": "owner details",
    "number": "WhatsApp number",
    "testchat": "test chat",
    "training": "training",
}

DIGIT_WORDS_EN = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def spell_number(number):
    """9845012345 -> "nine eight four five zero, one two three four five" so TTS reads
    it digit by digit (the TTS docs recommend writing IDs as spoken words)."""
    words = [DIGIT_WORDS_EN[int(c)] for c in (number or "") if c.isdigit()]
    return " ".join(words[:5]) + (", " + " ".join(words[5:]) if len(words) > 5 else "")


# Short blocked reasons (from run_verification) -> how they read in the report
BLOCK_PHRASES = {
    "Number not connected": "the WhatsApp number wasn't connected",
    "No FAQ documents": "no FAQ documents were indexed",
    "Platform unreachable": "the platform wasn't reachable",
    "Owner name doesn't match": "the owner's name didn't match the account",
    "No training booked": "no training was booked",
}


def _block_phrase(reason):
    if reason.startswith("Bot replies in "):  # "Bot replies in English, customer expects Hindi"
        got, _, want = reason.removeprefix("Bot replies in ").partition(", customer expects ")
        return f"the bot replied in {got} instead of {want}"
    return BLOCK_PHRASES.get(reason, reason[:1].lower() + reason[1:])


def _join(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def _training_when():
    """'Thursday at 11 AM' from the calendar (weekday, not date, so the spoken
    report stays the same from week to week and its cached audio keeps working)."""
    code, events, _ = http("GET", f"/calendar/events?customer={CUSTOMER_ID}")
    if code == 200 and events:
        start = datetime.fromisoformat(events[0]["start"])
        return f"{start.strftime('%A')} at {start.strftime('%I %p').lstrip('0')}"
    return ""


def summary_text(owner, number, statuses=None, language="hi-IN", first_block=None):
    """English report for the founder. statuses = {item_id: status}.
    All verified -> a report of the main activity, ready for go-live approval;
    otherwise a short progress update. first_block = short reasons from the
    first blocked test, if there was one.
    Returns {"en": text to show, "spoken": same text written for TTS, "ready"}."""
    statuses = statuses or {}
    open_items = [k for k in ITEM_NAMES if statuses.get(k) != "verified"]
    if statuses and not open_items:
        lang = LANG_NAMES.get(language, "Hindi")
        when = _training_when()
        shown = display(number) if number else ""

        # Saved summary (Activity): the full story, incl. the first block and the fix
        detail = (f"Account verified. Owner {owner} confirmed on a call in {lang}; WhatsApp number {shown} "
                  "confirmed and a summary sent. Engineer connected the number and uploaded the FAQ. ")
        if first_block:
            detail += f"First test blocked because {_join([_block_phrase(r) for r in first_block])}; fixed and retested. "
        detail += f"Bot replies in {lang}." + (f" Training booked for {when}." if when else "")

        # What the founder SEES: at most 4 key points, one line each (no process, no failures)
        points = [
            f"Kaveri Handlooms · owner {owner}",
            f"WhatsApp number {shown} confirmed",
            "Account verified and number connected",
            "Bot tested in customer's language",
        ]
        # What the founder HEARS (Avinash, always English): the same points, same order.
        # No customer language in it, so ONE audio file covers Hindi and Kannada customers.
        # spoken_parts[0] is the opening line, then one part per bullet, so the typing
        # of each bullet can follow the voice.
        spoken_parts = [
            "Here are your updates.",
            f"Kaveri Handlooms is set up, with {owner} as the owner.",
            f"Their WhatsApp number, {spell_number(number)}, is confirmed.",
            "The account is verified, and the number is connected to the bot.",
            "The bot is tested and replies in the customer's language.",
        ]
        return {"intro": "Here are your updates", "points": points, "spoken_parts": spoken_parts,
                "spoken": " ".join(spoken_parts), "en": detail, "ready": True}

    done = len(ITEM_NAMES) - len(open_items)
    blocked = [k for k in open_items if statuses.get(k) == "blocked"]
    waiting = [k for k in open_items if k not in blocked]
    text = f"Kaveri Handlooms: {done} of 5 items verified. "
    if blocked:
        text += "Blocked: " + ", ".join(ITEM_NAMES[k] for k in blocked) + ". "
    if waiting:
        text += "Still open: " + ", ".join(ITEM_NAMES[k] for k in waiting) + "."
    text = text.strip()
    return {"en": text, "spoken": text, "ready": False}
