"""
Nova MVP backend (Stages 1 + 2).

Stage 1:
  POST /transcribe   form-data: audio (file), mode (hinglish | hindi | digits) -> {transcript, language}
  POST /speak        JSON: {text, voice: customer | founder}                 -> audio/wav
  POST /extract      JSON: {transcript, want: ["owner", "number"], partial_number?} -> fields + ask_again
Stage 2:
  POST /nova/command JSON: {text}            -> {intent, reply}
  POST /nova/plan                            -> checklist + real account check + engineer task
  POST /nova/verify  JSON: {owner, number}   -> verification report (real HTTP checks)
  POST /nova/summary JSON: {owner, number, statuses} -> {en, spoken, ready} founder report
  GET/POST /config   JSON: {offline}         -> Live / Offline demo switch
Also serves the web page from ../frontend at http://localhost:8000
and starts the mock customer system at http://127.0.0.1:8001

Run:  python app.py              (live: real Gnani + Sarvam calls)
      python app.py --offline    (demo: no paid calls, see offline.py)
"""

import tempfile
import threading
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory
from werkzeug.serving import make_server

import nova_flow
import offline
from config import MOCK_PORT, STT_SETTINGS
from dialog import language_label, script_language
from extract import extract
from mock_system import mock
from stt import MIME_TYPES, transcribe_full
from tts import speak

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, static_folder=None)


@app.after_request
def no_cache(response):
    # Always serve the latest page/JS/CSS (avoids seeing an old cached UI)
    if request.path == "/" or request.path.endswith((".html", ".js", ".css")):
        response.headers["Cache-Control"] = "no-store"
    return response


def error(message, status=400):
    return jsonify({"error": message}), status


@app.post("/transcribe")
def transcribe_route():
    audio = request.files.get("audio")
    mode = request.form.get("mode", "hinglish")
    if audio is None:
        return error("Send the recording as form field 'audio'")
    if mode not in STT_SETTINGS:
        return error(f"mode must be one of {list(STT_SETTINGS)}")
    suffix = Path(audio.filename or "audio.wav").suffix.lower() or ".wav"
    if suffix not in MIME_TYPES:
        return error(f"Unsupported audio format {suffix}")

    # Offline demo: the simulated customer may send a scripted line as text
    demo_text = (request.form.get("demo_text") or "").strip()
    if offline.is_on() and demo_text:
        lang = script_language(demo_text)
        return jsonify({"transcript": demo_text, "mode": mode, "language": language_label(lang, demo_text)})

    # Save to a temp file because stt.transcribe_full() takes a path
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"reply{suffix}"
        audio.save(path)
        try:
            text, lang = transcribe_full(path, speech=mode)
        except Exception as e:  # Gnani error, network error
            return error(str(e), 502)
    return jsonify({"transcript": text, "mode": mode, "language": language_label(lang, text) if text else None})


@app.post("/speak")
def speak_route():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    voice = data.get("voice", "customer")
    if not text:
        return error("Send JSON with 'text'")
    try:
        audio = speak(text, voice=voice)
    except ValueError as e:
        return error(str(e))
    except Exception as e:
        return error(str(e), 502)
    return Response(audio, mimetype="audio/wav")


@app.post("/extract")
def extract_route():
    data = request.get_json(silent=True) or {}
    transcript = (data.get("transcript") or "").strip()
    want = data.get("want", ["owner", "number"])  # [] = yes/no read-back turn
    partial_number = data.get("partial_number")
    if not transcript:
        # Nothing heard: Nova should ask again
        return jsonify({"english": "", "owner_name": None, "numbers": [], "number": None,
                        "number_display": None, "number_status": "missing", "number_missing": 10,
                        "confirm": None, "wants_human": False, "ask_again": True, "missing": list(want)})
    try:
        return jsonify(extract(transcript, want=want, partial_number=partial_number))
    except Exception as e:
        return error(str(e), 502)


# ---------- Stage 2: Nova actions ----------
@app.post("/nova/command")
def command_route():
    text = ((request.get_json(silent=True) or {}).get("text") or "").strip()
    if not text:
        return error("Send JSON with 'text'")
    return jsonify(nova_flow.classify_command(text))


@app.post("/nova/plan")
def plan_route():
    return jsonify(nova_flow.build_plan())


@app.post("/nova/verify")
def verify_route():
    data = request.get_json(silent=True) or {}
    if not data.get("number"):
        return error("A confirmed WhatsApp number is needed before testing")
    return jsonify(nova_flow.run_verification(data.get("owner") or "", data["number"]))


@app.post("/nova/summary")
def summary_route():
    data = request.get_json(silent=True) or {}
    return jsonify(nova_flow.summary_text(data.get("owner") or "", data.get("number") or "", data.get("statuses") or {},
                                          data.get("language") or "hi-IN", data.get("first_block") or []))


# ---------- Live / Offline demo switch ----------
@app.get("/config")
def config_route():
    return jsonify({"offline": offline.is_on()})


@app.post("/config")
def set_config_route():
    data = request.get_json(silent=True) or {}
    if "offline" in data:
        offline.enable(bool(data["offline"]))
    return jsonify({"offline": offline.is_on()})


@app.get("/test_audio/<path:filename>")
def test_audio_route(filename):
    # Only in offline demo mode: lets the demo mic play your test recordings
    if not offline.is_on():
        return error("Only available in offline demo mode", 404)
    return send_from_directory(offline.TEST_AUDIO_DIR, filename)


# ---------- web page ----------
@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


def start_mock_system():
    """Run the mock customer system on its own port in a background thread,
    so Nova tests it over real HTTP but you only start one program."""
    server = make_server("127.0.0.1", MOCK_PORT, mock, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Mock customer system at http://127.0.0.1:{MOCK_PORT}")


if __name__ == "__main__":
    import sys
    if "--offline" in sys.argv:
        offline.enable()
    if offline.is_on():
        print("OFFLINE DEMO: no Gnani or Sarvam calls (saved results and saved audio only)")
    start_mock_system()
    print("Nova running at http://localhost:8000")
    # No auto-reloader: it would start the mock server twice
    app.run(host="127.0.0.1", port=8000, threaded=True)
