"""
Mock Supra AI platform for the Nova demo (runs on http://127.0.0.1:8001).

Supra AI makes an AI WhatsApp customer-support bot for small businesses. Nova
checks this platform over real HTTP to verify a customer's setup.

Endpoints
  GET    /health                              -> {"status": "ok"}
  GET    /accounts/<id>                       -> account record (incl. preferred language) or 404
  POST   /accounts/<id> {owner?, preferred_language?} -> save the owner confirmed on the call / set the language
  GET    /channels/whatsapp/<number>          -> 200 if the number is connected, 404 if not
  POST   /channels/whatsapp  {number, account}-> connect a number        (demo control)
  DELETE /channels/whatsapp/<number>          -> disconnect a number     (demo control)
  GET    /kb/<account>                        -> FAQ documents indexed
  POST   /kb/<account>/upload {count}         -> index more FAQ documents (demo control)
  POST   /test-chat {account, message}        -> the bot's reply and its language
  GET    /bot/<account>                       -> bot settings
  POST   /bot/<account> {reply_language}      -> set the bot's reply language: en-IN / hi-IN / kn-IN
  GET    /calendar/events?customer=<id>       -> training bookings
  POST   /reset                               -> back to the starting (seed) state

Seed state makes the FIRST verification Blocked on purpose:
the WhatsApp number is not connected, and the bot replies in English
although the customer expects Hindi. Data lives in memory.
Run on its own:  python mock_system.py   (app.py also starts it for you)
"""

import copy
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

mock = Flask("mock_supra_platform")


def _next_weekday(weekday, hour):
    """Next given weekday (0 = Monday) at the given hour, as ISO text."""
    now = datetime.now()
    days = (weekday - now.weekday()) % 7 or 7
    return (now + timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0).isoformat()


def _seed():
    return {
        "accounts": {
            "CUS-0142": {
                "id": "CUS-0142", "name": "Kaveri Handlooms", "city": "Mysuru", "status": "active",
                "plan": "Starter", "owner": None,   # captured on the call: Nova saves the confirmed name
                "preferred_language": "hi-IN",  # per-customer language (Kannada can plug in later)
                "created_at": (datetime.now() - timedelta(days=1)).replace(hour=11, minute=20).isoformat(),
            },
        },
        "whatsapp": {},                       # number -> {number, account, connected_at}; seed: not connected
        "kb": {"CUS-0142": 6},                # FAQ documents indexed (engineer uploaded 6)
        "bot": {"CUS-0142": {"reply_language": "en-IN"}},   # seed: replies in English (wrong)
        "events": [{"customer": "CUS-0142", "title": "Supra AI training: Kaveri Handlooms team",
                    "start": _next_weekday(3, 11), "duration_min": 30, "owner": "CSM"}],
    }


DB = _seed()

# What the bot answers in the test chat, per language
REPLIES = {
    "hi-IN": "नमस्ते! हाँ, हमारी कॉटन साड़ियाँ ₹1,450 से शुरू होती हैं। क्या मैं कुछ डिज़ाइन भेजूँ?",
    "en-IN": "Hello! Yes, our cotton sarees start at ₹1,450. Shall I send you some designs?",
    "kn-IN": "ನಮಸ್ಕಾರ! ಹೌದು, ನಮ್ಮ ಕಾಟನ್ ಸೀರೆಗಳು ₹1,450 ರಿಂದ ಶುರು. ಕೆಲವು ಡಿಸೈನ್ ಕಳಿಸಲಾ?",
}
NO_FAQ = {"hi-IN": "माफ़ कीजिए, मेरे पास अभी यह जानकारी नहीं है।", "en-IN": "Sorry, I don't have that information yet.",
          "kn-IN": "ಕ್ಷಮಿಸಿ, ಈ ಮಾಹಿತಿ ಇನ್ನೂ ನನ್ನ ಹತ್ತಿರ ಇಲ್ಲ."}


@mock.after_request
def cors(response):
    # The Nova page reads/changes this platform directly from Demo controls
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return response


@mock.get("/health")
def health():
    return jsonify({"status": "ok", "system": "Supra AI platform (mock)"})


@mock.get("/accounts/<account_id>")
def get_account(account_id):
    account = DB["accounts"].get(account_id)
    return (jsonify(account), 200) if account else (jsonify({"error": "account not found"}), 404)


@mock.post("/accounts/<account_id>")
def update_account(account_id):
    account = DB["accounts"].get(account_id)
    if not account:
        return jsonify({"error": "account not found"}), 404
    data = request.get_json(silent=True) or {}
    if "owner" in data:                       # Nova saves the owner confirmed on the call
        owner = (data.get("owner") or "").strip()
        if not owner:
            return jsonify({"error": "owner must be a non-empty name"}), 400
        account["owner"] = owner
    if "preferred_language" in data:          # demo control: the customer's language
        lang = data["preferred_language"]
        if lang not in REPLIES:
            return jsonify({"error": f"preferred_language must be one of {list(REPLIES)}"}), 400
        account["preferred_language"] = lang
    if "owner" not in data and "preferred_language" not in data:
        return jsonify({"error": "send owner and/or preferred_language"}), 400
    return jsonify(account)


@mock.get("/channels/whatsapp/<number>")
def get_channel(number):
    record = DB["whatsapp"].get(number)
    return (jsonify(record), 200) if record else (jsonify({"error": f"{number} is not connected"}), 404)


@mock.get("/channels/whatsapp")
def list_channels():
    return jsonify(list(DB["whatsapp"].values()))


@mock.post("/channels/whatsapp")
def connect_channel():
    data = request.get_json(silent=True) or {}
    number = "".join(ch for ch in str(data.get("number", "")) if ch.isdigit())
    if len(number) != 10:
        return jsonify({"error": "a 10-digit number is required"}), 400
    DB["whatsapp"][number] = {"number": number, "account": data.get("account", "CUS-0142"),
                              "connected_at": datetime.now().isoformat(timespec="seconds")}
    return jsonify(DB["whatsapp"][number]), 201


@mock.delete("/channels/whatsapp/<number>")
def disconnect_channel(number):
    removed = DB["whatsapp"].pop(number, None)
    return (jsonify({"disconnected": number}), 200) if removed else (jsonify({"error": "not connected"}), 404)


@mock.get("/kb/<account>")
def get_kb(account):
    return jsonify({"account": account, "documents": DB["kb"].get(account, 0), "indexed": DB["kb"].get(account, 0)})


@mock.post("/kb/<account>/upload")
def upload_kb(account):
    count = int((request.get_json(silent=True) or {}).get("count", 1))
    DB["kb"][account] = max(0, DB["kb"].get(account, 0) + count)
    return jsonify({"account": account, "indexed": DB["kb"][account]})


@mock.get("/bot/<account>")
def get_bot(account):
    return jsonify(DB["bot"].setdefault(account, {"reply_language": "en-IN"}))


@mock.post("/bot/<account>")
def set_bot(account):
    lang = (request.get_json(silent=True) or {}).get("reply_language")
    if lang not in REPLIES:
        return jsonify({"error": f"reply_language must be one of {list(REPLIES)}"}), 400
    DB["bot"].setdefault(account, {})["reply_language"] = lang
    return jsonify(DB["bot"][account])


@mock.post("/test-chat")
def test_chat():
    data = request.get_json(silent=True) or {}
    account = data.get("account", "CUS-0142")
    lang = DB["bot"].get(account, {}).get("reply_language", "en-IN")
    reply = REPLIES[lang] if DB["kb"].get(account, 0) > 0 else NO_FAQ[lang]
    return jsonify({"account": account, "message": data.get("message", ""), "reply": reply, "language": lang,
                    "faq_documents": DB["kb"].get(account, 0)})


@mock.get("/calendar/events")
def list_events():
    customer = request.args.get("customer")
    return jsonify([e for e in DB["events"] if not customer or e["customer"] == customer])


@mock.post("/reset")
def reset():
    DB.clear()
    DB.update(copy.deepcopy(_seed()))
    return jsonify({"reset": True})


if __name__ == "__main__":
    mock.run(host="127.0.0.1", port=8001)
